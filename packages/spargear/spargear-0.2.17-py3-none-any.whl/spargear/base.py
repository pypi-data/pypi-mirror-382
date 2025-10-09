import argparse
import inspect
import json
import logging
import pickle
from copy import deepcopy
from dataclasses import field, make_dataclass
from enum import Enum
from pathlib import Path
from traceback import print_exc
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
    overload,
)

from ._typing import (
    Action,
    Annotated,
    assert_type,
    extract_attr_docstrings,
    get_args,
    get_arguments_of_container_types,
    get_origin,
    get_type_hints,
    get_type_of_element_of_container_types,
    is_optional,
    sanitize_flag,
)
from .argspec import ArgumentSpec, ArgumentSpecType, ensure_no_optional
from .subcommand import SubcommandSpec

logger = logging.getLogger(__name__)


class BaseArguments:
    """Base class for defining arguments declaratively using ArgumentSpec."""

    __arguments__: Dict[str, Tuple[ArgumentSpec[object], ArgumentSpecType]]
    __subcommands__: Dict[str, SubcommandSpec["BaseArguments"]]
    __subcommand: Optional["BaseArguments"] = None

    @property
    def last_subcommand(self) -> Optional["BaseArguments"]:
        return self.__subcommand

    def __init__(self, args: Optional[Sequence[str]] = None, _internal_init: bool = False) -> None:
        """
        Initializes the BaseArguments instance and loads arguments from the command line or a given list of arguments.
        If no arguments are provided, it uses sys.argv[1:] by default.
        """
        # Initialize instance-specific argument values and specs
        self.__instance_values__: Dict[str, object] = {}
        self.__instance_specs__: Dict[str, ArgumentSpec[object]] = {}

        # only load at root (내부 생성이 아닌 경우)
        if not _internal_init:
            cls = self.__class__
            parser = cls.get_parser()
            try:
                parsed_args = parser.parse_args(args)
            except SystemExit:
                raise

            # load this class's own specs
            self.__load_from_namespace(parsed_args)

            # now walk down through any subcommands
            current_cls = cls
            current_inst: Optional["BaseArguments"] = None
            depth = 0
            while current_cls._has_subcommands():
                # 각 레벨에 맞는 dest 이름 사용
                if depth == 0:
                    dest_name = "subcommand"
                else:
                    dest_name = f"subcommand_depth_{depth}"

                subname = getattr(parsed_args, dest_name, None)
                if not subname:
                    break

                subc = current_cls.__subcommands__.get(subname)
                if not subc:
                    break

                try:
                    argument_class = subc.get_argument_class()
                except Exception:
                    break

                # Create subcommand instance with internal flag
                inst = argument_class(args=None, _internal_init=True)
                # Load values from parsed args
                inst.__load_from_namespace(parsed_args)
                current_inst = inst
                current_cls = argument_class
                depth += 1
            self.__subcommand = current_inst

    def __str__(self) -> str:
        """String representation of the BaseArguments instance."""
        return f"{self.__class__.__name__}({self.to_json(indent=2)})"

    def __getitem__(self, key: str) -> Optional[object]:
        return self.__instance_values__.get(key, self.__class__.__arguments__[key][0].value)

    def __setattr__(self, name: str, value: object) -> None:
        """Override attribute setting to store values in instance-specific storage."""
        if name not in self.__arguments__:
            # If the attribute is not an argument, use normal setattr
            super().__setattr__(name, value)
            return

        spec, spec_type = self.__arguments__[name]
        if spec_type.is_specless_type:
            # If it's a specless type, store the value directly
            self.__instance_values__[name] = value
            return

        # For ArgumentSpec types, assign the value to the instance-specific spec
        instance_specs = self.__instance_specs__
        if name in self.__instance_specs__:
            # If the spec exists in instance_specs, update its value
            instance_specs[name].value = value
        else:
            # Create a new instance copy of the spec if it doesn't exist
            instance_spec: ArgumentSpec[object] = deepcopy(spec)
            instance_spec.value = value
            instance_specs[name] = instance_spec

    def __getattribute__(self, name: str) -> object:
        """Override attribute access to return instance-specific ArgumentSpec objects or values."""
        # For special attributes, use normal access
        if TYPE_CHECKING:
            arguments = self.__arguments__
        else:
            arguments = super().__getattribute__("__arguments__")

        if name not in arguments:
            return super().__getattribute__(name)

        if TYPE_CHECKING:
            instance_values = self.__instance_values__
            instance_specs = self.__instance_specs__
        else:
            instance_values = super().__getattribute__("__instance_values__")
            instance_specs = super().__getattribute__("__instance_specs__")

        spec, spec_type = arguments[name]

        # For specless types, return the actual value if it exists
        if spec_type.is_specless_type:
            if name in instance_values:
                # If the value is already set in instance_values, return it
                return instance_values[name]
            return spec.default

        # For ArgumentSpec types, return the instance-specific spec
        if name in instance_specs:
            # If the spec exists in instance_specs, return it
            return instance_specs[name]

        # Create a new instance copy of the spec if it doesn't exist
        instance_spec: ArgumentSpec[object] = deepcopy(spec)
        instance_specs[name] = instance_spec
        return instance_spec

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls.__arguments__ = {}
        cls.__subcommands__ = {}

        for current_cls in reversed(cls.__mro__):
            if current_cls in (object, BaseArguments):
                continue
            # Subcommands
            for attr_value in vars(current_cls).values():
                if isinstance(attr_value, SubcommandSpec):
                    attr_value = cast(SubcommandSpec["BaseArguments"], attr_value)
                    cls.__subcommands__[attr_value.name] = attr_value

            # ArgumentSpecs
            docstrings: Dict[str, str] = extract_attr_docstrings(current_cls)
            for attr_name, attr_hint in _get_type_hints(current_cls):
                attr_value: Optional[object] = getattr(current_cls, attr_name, None)
                if isinstance(attr_value, ArgumentSpec):
                    spec: ArgumentSpec[object] = cast(ArgumentSpec[object], attr_value)
                else:
                    spec, attr_hint = _infer_spec_and_correct_typehint_from_nonspec_typehint(
                        attr_name=attr_name,
                        type_no_spec=attr_hint,
                        attr_value=attr_value,
                        docstrings=docstrings,
                    )

                if attr_name in cls.__arguments__:
                    logger.debug(f"Duplicate argument name '{attr_name}' in {current_cls.__name__}.")

                try:
                    # Extract type information from type hint
                    spec_type: ArgumentSpecType = ArgumentSpecType.from_type_hint(attr_hint)

                    # Set `choices` and `type`
                    if detected_choices := spec_type.choices:
                        spec.choices = detected_choices
                    if spec.type is None and (detected_type := spec_type.type):
                        if isinstance(detected_type, type(Enum)):
                            spec.type = detected_type.__getitem__
                        else:
                            spec.type = detected_type

                    # Determine `nargs` depending on list/tuple type
                    if tn := spec_type.tuple_nargs:
                        spec.nargs = tn
                    elif spec.nargs is None and spec_type.should_return_as_list or spec_type.should_return_as_tuple:
                        spec.nargs = "*"

                    cls.__arguments__[attr_name] = (spec, spec_type)
                except Exception as e:
                    print_exc()
                    logger.warning(f"Error processing {attr_name} in {current_cls.__name__}: {e}")
                    continue

    def get(self, key: str) -> Optional[object]:
        return self.__instance_values__.get(key, self.__class__.__arguments__[key][0].value)

    def keys(self) -> Iterable[str]:
        yield from (k for k, _v in self.items())

    def values(self) -> Iterable[object]:
        yield from (v for _k, v in self.items())

    def items(self) -> Iterable[Tuple[str, object]]:
        for key, spec, _ in self.__class__.__iter_arguments():
            value = self.__instance_values__.get(key, spec.value)
            if value is not None:
                yield key, value

    def to_dataclass(self, class_name: Optional[str] = None) -> Any:
        """Convert the BaseArguments instance to a dataclass instance.

        Args:
            class_name: Name for the generated dataclass. Defaults to {ClassName}Config.

        Returns:
            A dataclass instance with all the argument values.
        """
        if class_name is None:
            class_name = f"{self.__class__.__name__}Config"

        # Collect all argument values
        field_definitions: List[Tuple[str, type, Any]] = []
        field_values: Dict[str, Any] = {}

        for key, spec, spec_type in self.__class__.__iter_arguments():
            # Get the value from instance
            if hasattr(self, "__instance_values__") and key in self.__instance_values__:
                value = self.__instance_values__[key]
            else:
                value = spec.default

            # Determine the field type
            field_type = spec_type.type_no_optional_or_spec if spec_type.type_no_optional_or_spec is not object else Any
            if not isinstance(field_type, type):
                field_type = Any

            # Create field definition - handle mutable defaults
            if isinstance(value, (list, dict, set)):
                # Use default_factory for mutable types
                def make_factory(val: Any) -> Callable[[], Any]:
                    if hasattr(val, "copy"):
                        return lambda: val.copy()
                    else:
                        return lambda: list(val)

                field_definitions.append((
                    key,
                    cast(type, field_type),
                    field(default_factory=make_factory(value)),
                ))
            else:
                field_definitions.append((
                    key,
                    cast(type, field_type),
                    field(default=value),
                ))
            field_values[key] = value

        # Create the dataclass
        DataclassType = make_dataclass(class_name, field_definitions)

        # Create instance with current values
        return DataclassType(**field_values)

    def to_dict(self) -> Dict[str, object]:
        """Convert the BaseArguments instance to a dictionary.

        Returns:
            A dictionary with all argument names and their values.
        """
        result: Dict[str, object] = {}
        for key, spec, _ in self.__class__.__iter_arguments():
            if hasattr(self, "__instance_values__") and key in self.__instance_values__:
                value = self.__instance_values__[key]
            else:
                value = spec.default

            # Only include non-None values
            if value is not None:
                result[key] = value

        return result

    def to_json(
        self,
        skipkeys: bool = False,
        ensure_ascii: bool = True,
        check_circular: bool = True,
        allow_nan: bool = True,
        cls: Optional[Type[json.JSONEncoder]] = None,
        indent: Optional[Union[int, str]] = None,
        separators: Optional[Tuple[str, str]] = None,
        default: Optional[Callable[[object], object]] = None,
        sort_keys: bool = False,
        **kwds: Any,
    ) -> str:
        """Serialize the BaseArguments instance to JSON."""
        data = self.to_dict()

        # Convert non-serializable types
        def default_fallback(obj: object) -> object:
            if isinstance(obj, Path):
                return str(obj)
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            else:
                return str(obj)

        json_str = json.dumps(
            data,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            cls=cls,
            indent=indent,
            separators=separators,
            default=default or default_fallback,
            sort_keys=sort_keys,
            **kwds,
        )

        return json_str

    @overload
    def to_pickle(
        self,
        protocol: Optional[int] = None,
        *,
        fix_imports: bool = True,
        buffer_callback: Optional[Callable[[object], None]] = None,
        pickler: pickle.Pickler,
    ) -> None: ...
    @overload
    def to_pickle(
        self,
        protocol: Optional[int] = None,
        *,
        fix_imports: bool = True,
        buffer_callback: Optional[Callable[[object], None]] = None,
        pickler: None = None,
    ) -> bytes: ...
    def to_pickle(
        self,
        protocol: Optional[int] = None,
        *,
        fix_imports: bool = True,
        buffer_callback: Optional[Callable[[object], None]] = None,
        pickler: Optional[pickle.Pickler] = None,
    ) -> Optional[bytes]:
        """Serialize the BaseArguments instance to a pickle file."""

        # Remove all lambda-based default factories
        for key, spec in self.__instance_specs__.items():
            if spec.default_factory is not None and callable(spec.default_factory):
                logger.warning(f"Removing default_factory from {spec.name_or_flags} in {self.__class__.__name__}.")
                spec.default_factory = None
                spec_and_spectype = self.__arguments__.get(key)
                if spec_and_spectype is None:
                    continue
                spec, _ = spec_and_spectype
                if spec.default_factory is not None and callable(spec.default_factory):
                    spec.default_factory = None

        # If a pickler is provided, use it to serialize
        if pickler is None:
            # If no pickler is provided, use default pickle serialization
            return pickle.dumps(
                self,
                protocol=protocol,
                fix_imports=fix_imports,
                buffer_callback=buffer_callback,
            )

        # If a pickler is provided, use it to serialize
        # This allows for custom pickling behavior if needed
        pickler.dump(self)
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], args: Optional[Sequence[str]] = None):
        """Create a BaseArguments instance from a dictionary.

        Args:
            data: Dictionary with argument names and values.
            args: Optional command line arguments to parse first.

        Returns:
            A new BaseArguments instance with values from the dictionary.
        """
        # Create instance with command line args first (if provided)
        instance = cls(args or [])

        # Apply dictionary values only for keys not set by command line
        if hasattr(instance, "__instance_values__"):
            for key, value in data.items():
                if key in cls.__arguments__:
                    # Only set if not already set by command line args or if it's still the default
                    spec, _ = cls.__arguments__[key]

                    # Set from dict if: not in instance values, is None, or is still the default value
                    if (
                        key not in instance.__instance_values__
                        or instance.__instance_values__[key] is None
                        or instance.__instance_values__[key] == spec.default
                    ):
                        instance.__instance_values__[key] = value
                        # Also update instance specs if they exist
                        if hasattr(instance, "__instance_specs__") and key in instance.__instance_specs__:
                            instance.__instance_specs__[key].value = value

        return instance

    @classmethod
    def from_json(cls, json_data: Union[str, Path], args: Optional[Sequence[str]] = None):
        """Create a BaseArguments instance from JSON data.

        Args:
            json_data: JSON string or path to JSON file.
            args: Optional command line arguments to parse first.

        Returns:
            A new BaseArguments instance with values from the JSON.
        """
        if isinstance(json_data, Path):
            # It's a file path
            data = json.loads(Path(json_data).read_text(encoding="utf-8"))
        else:
            # It's a JSON string
            data = json.loads(str(json_data))

        return cls.from_dict(data, args)

    @classmethod
    def from_pickle(
        cls,
        path_or_bytes: Union[str, Path, bytes],
        args: Optional[Sequence[str]] = None,
    ):
        """Create a BaseArguments instance from a pickle file.

        Args:
            path_or_bytes: Path to the pickle file or bytes data.
            args: Optional command line arguments to parse first.

        Returns:
            A new BaseArguments instance with values from the pickle file.
        """
        if isinstance(path_or_bytes, bytes):
            # If file_path is bytes, assume it's a serialized BaseArguments instance
            data = pickle.loads(path_or_bytes)

        else:
            with open(path_or_bytes, "rb") as f:
                data = pickle.load(f)
        if isinstance(data, cls):
            return data
        else:
            raise ValueError("Bytes data does not represent a BaseArguments instance.")

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update the current instance with values from a dictionary.

        Args:
            data: Dictionary with argument names and values to update.
        """
        if hasattr(self, "__instance_values__"):
            for key, value in data.items():
                if key in self.__class__.__arguments__:
                    self.__instance_values__[key] = value
                    # Also update instance specs if they exist
                    if hasattr(self, "__instance_specs__") and key in self.__instance_specs__:
                        self.__instance_specs__[key].value = value

    @classmethod
    def load_config(
        cls,
        file_path: Union[str, Path],
        format: Optional[Literal["json", "pickle"]] = None,
        args: Optional[Sequence[str]] = None,
    ):
        """Load configuration from a file.

        Args:
            file_path: Path to the configuration file.
            format: File format. If None, inferred from file extension.
            args: Optional command line arguments to parse first.

        Returns:
            A new BaseArguments instance with values from the file.
        """
        path = Path(file_path)

        if format is None:
            # Infer format from extension
            if path.suffix.lower() == ".json":
                format = "json"
            elif path.suffix.lower() in (".pkl", ".pickle"):
                format = "pickle"
            else:
                raise ValueError(f"Cannot infer format from extension: {path.suffix}")

        if format == "json":
            return cls.from_json(path, args)
        elif format == "pickle":
            return cls.from_pickle(path, args)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        arg_parser = argparse.ArgumentParser(
            description=cls.__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=False,
        )
        arg_parser.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Show this help message and exit.",
        )
        cls.__configure_parser(arg_parser)
        return arg_parser

    @classmethod
    def __iter_arguments(
        cls,
    ) -> Iterable[Tuple[str, ArgumentSpec[object], ArgumentSpecType]]:
        yield from ((key, spec, spec_type) for key, (spec, spec_type) in cls.__arguments__.items())

    @classmethod
    def __iter_subcommands(
        cls,
    ) -> Iterable[Tuple[str, SubcommandSpec["BaseArguments"]]]:
        yield from cls.__subcommands__.items()

    @classmethod
    def _has_subcommands(cls) -> bool:
        return bool(cls.__subcommands__)

    @classmethod
    def __add_argument_to_parser(
        cls, parser: argparse.ArgumentParser, name_or_flags: List[str], **kwargs: object
    ) -> None:
        parser.add_argument(*name_or_flags, **kwargs)  # type: ignore

    @classmethod
    def __configure_parser(cls, parser: argparse.ArgumentParser, _depth: int = 0) -> None:
        # 1) add this class's own arguments
        for key, spec, _ in cls.__iter_arguments():
            kwargs = spec.get_add_argument_kwargs()
            is_positional = not any(name.startswith("-") for name in spec.name_or_flags)
            if is_positional:
                kwargs.pop("required", None)
                cls.__add_argument_to_parser(parser, spec.name_or_flags, **kwargs)
            else:
                kwargs.setdefault("dest", key)
                cls.__add_argument_to_parser(parser, spec.name_or_flags, **kwargs)

        # 2) if there are subcommands, add them at this level
        if cls._has_subcommands():
            # 각 레벨에 고유한 dest 이름 사용
            if _depth == 0:
                dest_name = "subcommand"
            else:
                dest_name = f"subcommand_depth_{_depth}"

            subparsers = parser.add_subparsers(
                title="subcommands",
                dest=dest_name,
                metavar="subcommand",  # Always show 'subcommand' in help text
                help="Available subcommands",
                required=not cls.__arguments__ and bool(cls.__subcommands__),
            )
            for name, subc in cls.__iter_subcommands():
                subparser = subparsers.add_parser(
                    name,
                    help=subc.help,
                    description=subc.description or subc.help,
                )
                try:
                    argument_class = subc.get_argument_class()
                    argument_class.__configure_parser(subparser, _depth + 1)
                except Exception:
                    # If getting the argument class fails, skip this subcommand configuration
                    pass

    def __load_from_namespace(self, args: argparse.Namespace) -> None:
        # First, create instance-specific copies of all ArgumentSpecs
        for key, spec, spec_type in self.__class__.__iter_arguments():
            # Create a copy of the spec for this instance

            instance_spec = deepcopy(spec)
            self.__instance_specs__[key] = instance_spec

        for key, spec, spec_type in self.__class__.__iter_arguments():
            instance_spec: ArgumentSpec[object] = self.__instance_specs__[key]
            is_positional: bool = not any(n.startswith("-") for n in spec.name_or_flags)
            attr = spec.name_or_flags[0] if is_positional else (spec.dest or key)
            if not hasattr(args, attr):
                continue
            val: object = cast(object, getattr(args, attr))
            if val is argparse.SUPPRESS:
                continue

            checkable_type: Optional[type] = (
                spec.type if spec.type is not None and isinstance(spec.type, type) else None
            )

            # Type check for list/tuple
            if spec_type.should_return_as_list:
                if isinstance(val, list):
                    val = cast(List[object], val)

                elif val is not None:
                    val = [val]
                if val is not None and checkable_type is not None:
                    for v in val:
                        assert_type(v, checkable_type)

            elif spec_type.should_return_as_tuple:
                if isinstance(val, tuple):
                    val = cast(Tuple[object, ...], val)
                elif val is not None:
                    if isinstance(val, list):
                        val = tuple(cast(List[object], val))
                    else:
                        val = (val,)
                if val is not None and checkable_type is not None:
                    for v in val:
                        assert_type(v, checkable_type)

            elif val is not None and checkable_type is not None:
                assert_type(val, checkable_type)

            # Store value in instance-specific storage
            self.__instance_values__[key] = val
            # Update the instance-specific spec
            instance_spec.value = val

        # Apply default factories after all values are loaded
        for key, spec, spec_type in self.__class__.__iter_arguments():
            instance_spec = self.__instance_specs__[key]
            # Only apply default factory if no value was set from command line
            if key not in self.__instance_values__ or self.__instance_values__[key] is None:
                if instance_spec.default_factory is not None:
                    factory_value = instance_spec.default_factory()
                    self.__instance_values__[key] = factory_value
                    # Update the instance-specific spec
                    instance_spec.value = factory_value


ignored_annotations = tuple(get_type_hints(BaseArguments).keys())


def _get_type_hints(obj: type) -> Iterator[Tuple[str, object]]:
    """Get type hints for an object, excluding those in BaseArguments."""
    for k, v in get_type_hints(obj, include_extras=True).items():
        if k not in ignored_annotations:
            yield k, v


def _infer_spec_and_correct_typehint_from_nonspec_typehint(
    attr_name: str, type_no_spec: object, attr_value: object, docstrings: Dict[str, str]
) -> Tuple[ArgumentSpec[object], object]:
    action: Optional[Action] = None
    type: Optional[Callable[[str], object]] = None

    optional: bool = is_optional(type_no_spec)
    type_no_optional_or_spec: object = ensure_no_optional(type_no_spec)

    if get_origin(type_no_optional_or_spec) is Annotated:
        args = get_args(type_no_optional_or_spec)

        optional = optional or is_optional(args[0])
        type_no_optional_or_spec = ensure_no_optional(args[0])
        callable_metadata = next((a for a in args[1:] if callable(a)), None)
    else:
        callable_metadata: Optional[Callable[[str], object]] = None

    if callable_metadata is not None:
        type = callable_metadata
        if get_arguments_of_container_types(
            type_no_optional_or_spec=type_no_optional_or_spec,
            container_types=(list, tuple),
        ):
            type_no_optional_or_spec = get_type_of_element_of_container_types(
                type_no_optional_or_spec=ensure_no_optional(type_no_optional_or_spec),
                container_types=(list, tuple),
            )
    elif type_no_optional_or_spec is bool:
        if attr_value is False:
            # If the default is False, we want to set action to store_true
            action = "store_true"
        elif attr_value is True:
            # If the default is True, we want to set action to store_false
            action = "store_false"
        else:
            # If the default is None, we want to get explicit boolean value
            def get_boolean(x: str) -> bool:
                if x.lower() in ("true", "1", "yes"):
                    return True
                elif x.lower() in ("false", "0", "no"):
                    return False
                raise argparse.ArgumentTypeError(f"Invalid boolean value: {x}")

            type = get_boolean

    # Check if attr_value is a callable (potential default factory)
    default_factory: Optional[Callable[[], object]] = None
    default_value: Optional[object] = attr_value

    # If attr_value is callable and not a type, treat it as default_factory
    if callable(attr_value) and not inspect.isclass(attr_value) and attr_value is not type:
        default_factory = attr_value
        default_value = None

    spec = ArgumentSpec(
        name_or_flags=[sanitize_flag(attr_name)],
        default=default_value,
        default_factory=default_factory,
        required=default_value is None and default_factory is None and not optional,
        help=docstrings.get(attr_name, ""),
        action=action,
        type=type,
    )
    return spec, type_no_optional_or_spec
