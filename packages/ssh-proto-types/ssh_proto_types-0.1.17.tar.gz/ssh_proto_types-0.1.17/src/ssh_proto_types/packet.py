import dataclasses
import inspect
import typing
from collections.abc import Callable, Mapping
from types import UnionType

from ssh_proto_types.basetypes import (
    C_TYPES_T,
    NOTSET,
    P_TYPES,
    P_TYPES_T,
    R_TYPES_T,
    UNDERLAYING_TYPES,
    UNDERLAYING_TYPES_T,
    Notset,
    exclude,
    is_c_types_t,
    is_p_types_t,
    is_r_types_t,
    nested,
)
from ssh_proto_types.stream import StreamReader, StreamWriter

_SSH_PROTO_TYPE_INFO = "__ssh_proto_type_info__"


def _is_dataclass(cls: type) -> bool:
    return "__dataclass_params__" in cls.__dict__


def _is_classvar(annotation: type) -> bool:
    origin = typing.get_origin(annotation)
    return origin is typing.ClassVar


def make_parser[U, O](overlaying_type: Callable[[U], O]) -> Callable[[U], O]:
    def _parser(x: U) -> O:
        return overlaying_type(x)

    return _parser


def make_serializer[U, O](underlaying_type: Callable[[O], U]) -> Callable[[O], U]:
    def _serializer(x: O) -> U:
        return underlaying_type(x)

    return _serializer


@dataclasses.dataclass(frozen=True, kw_only=True, eq=True)
class _Signatures:
    unmarshal_sig: inspect.Signature
    marshal_sig: inspect.Signature
    unmarshal_ann: dict[str, type]
    marshal_ann: dict[str, type]

    def get_obj(self) -> type:
        return self.unmarshal_sig.return_annotation

    @classmethod
    def from_cls(cls, c: type) -> typing.Self:
        unmarshal_sshwire = getattr(c, "unmarshal_sshwire")
        if not callable(unmarshal_sshwire):
            raise TypeError(f"Class {c.__name__} does not have callable unmarshal_sshwire method")
        marshal_sshwire = getattr(c, "marshal_sshwire")
        if not callable(marshal_sshwire):
            raise TypeError(f"Class {c.__name__} does not have callable marshal_sshwire method")
        return cls(
            unmarshal_sig=inspect.signature(unmarshal_sshwire),
            marshal_sig=inspect.signature(marshal_sshwire),
            unmarshal_ann=inspect.get_annotations(unmarshal_sshwire),
            marshal_ann=inspect.get_annotations(marshal_sshwire),
        )

    def replace_obj(self, obj_t: type[typing.Any]):
        unmarshal_sig = self.unmarshal_sig.replace(return_annotation=obj_t)
        params = [p for p in self.marshal_sig.parameters.values()]
        params[0] = params[0].replace(annotation=obj_t)
        marshal_sig = self.marshal_sig.replace(parameters=params)
        unmarshal_ann = dict(self.unmarshal_ann)
        unmarshal_ann["return"] = obj_t
        marshal_ann = dict(self.marshal_ann)
        marshal_ann["obj"] = obj_t
        return _Signatures(
            unmarshal_sig=unmarshal_sig,
            marshal_sig=marshal_sig,
            unmarshal_ann=unmarshal_ann,
            marshal_ann=marshal_ann,
        )


class FieldProto(typing.Protocol):
    @classmethod
    def unmarshal_sshwire(cls, stream: StreamReader, parsed: Mapping[str, typing.Any]) -> typing.Self:
        raise NotImplementedError()

    def marshal_sshwire(self, stream: StreamWriter) -> None:
        raise NotImplementedError()


_FIELD_PROTO_SIG = _Signatures.from_cls(FieldProto)


class FieldClassProto[O](typing.Protocol):
    @classmethod
    def unmarshal_sshwire(cls, stream: StreamReader, parsed: Mapping[str, typing.Any]) -> O:
        raise NotImplementedError()

    @classmethod
    def marshal_sshwire(cls, obj: O, stream: StreamWriter) -> None:
        raise NotImplementedError()


_FIELD_CLASS_PROTO_SIG = _Signatures.from_cls(FieldClassProto[typing.Any])


def _is_field_proto_t(annotation: type) -> typing.TypeGuard[type[FieldProto]]:
    try:
        sig = _Signatures.from_cls(annotation)
    except Exception:
        return False

    return sig == _FIELD_PROTO_SIG


def _is_field_class_proto_t(annotation: type) -> typing.TypeGuard[type[FieldClassProto[typing.Any]]]:
    try:
        sig = _Signatures.from_cls(annotation)
        obj = sig.get_obj()
    except Exception:
        return False

    return sig == _FIELD_CLASS_PROTO_SIG.replace_obj(obj)


@dataclasses.dataclass(kw_only=True)
class FieldInfoBase[O]:
    name: str
    is_class_var: bool
    is_discriminator: bool
    const_value: O | Notset
    is_excluded: bool

    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> O:
        raise NotImplementedError()

    def _marshal_value(self, stream: "StreamWriter", obj: O) -> None:
        raise NotImplementedError()

    @typing.final
    def unmarshal(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> O:
        if self.is_excluded and self.name not in parsed:
            raise ValueError(f"Field {self.name} is excluded, but not present in parsed values")

        o_value = parsed[self.name] if self.name in parsed else self._unmarshal_value(stream, parsed)

        if self.const_value is not NOTSET and o_value != self.const_value:
            raise InvalidHeader(f"Field {self.name} has constant value {self.const_value}, but got {o_value}")

        return o_value

    @typing.final
    def marshal(self, stream: "StreamWriter", obj: O) -> None:
        o_value = getattr(obj, self.name)
        if self.const_value is not NOTSET and o_value != self.const_value:
            raise ValueError(f"Field {self.name} has constant value {self.const_value}, but got {o_value}")
        return self._marshal_value(stream, o_value)


@dataclasses.dataclass
class FieldPacketInfo(FieldInfoBase["Packet"]):
    packet_type: type["Packet"]
    nested: bool
    discriminator_name: str | None

    @typing.override
    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> "Packet":
        # if self.discriminator_name is not None and self.discriminator_name not in parsed:
        #    raise ValueError(
        #        f"Field {self.name} is a discriminator, but discriminator name {self.discriminator_name} is not present in parsed values"
        #    )

        data = stream.read_bytes() if self.nested else stream
        # child_parsed = (
        #    {} if self.discriminator_name is None else {self.discriminator_name: parsed[self.discriminator_name]}
        # )
        return unmarshal(self.packet_type, data, {})

    @typing.override
    def _marshal_value(self, stream: "StreamWriter", obj: "Packet") -> None:
        data = marshal(obj)
        if self.nested:
            stream.write_bytes(data)
        else:
            stream.write_raw(data)


@dataclasses.dataclass
class FieldProtoInfo[O: FieldProto](FieldInfoBase[O]):
    custom_type: type[O]

    @typing.override
    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> O:
        return self.custom_type.unmarshal_sshwire(stream, parsed)

    @typing.override
    def _marshal_value(self, stream: "StreamWriter", obj: O) -> None:
        return self.custom_type.marshal_sshwire(obj, stream)


@dataclasses.dataclass
class _FieldInfoWithUnderlayingType[U: UNDERLAYING_TYPES_T, M: int | str | bytes, O](FieldInfoBase[O]):
    underlaying_type: type[U]

    def _write_value(self, stream: "StreamWriter", value: M) -> None:
        raise NotImplementedError()

    def _read_value(self, stream: "StreamReader") -> M:
        raise NotImplementedError()


# region FieldInfoBase


@dataclasses.dataclass
class _RFieldInfoBase[U: R_TYPES_T, O](_FieldInfoWithUnderlayingType[U, bytes, O]):
    @typing.override
    def _write_value(self, stream: "StreamWriter", value: bytes) -> None:
        stream.write(value, self.underlaying_type)

    @typing.override
    def _read_value(self, stream: "StreamReader") -> bytes:
        return stream.read(self.underlaying_type)


@dataclasses.dataclass
class _CFieldInfoBase[U: C_TYPES_T, O](_FieldInfoWithUnderlayingType[U, int, O]):
    @typing.override
    def _write_value(self, stream: "StreamWriter", value: int) -> None:
        stream.write(value, self.underlaying_type)

    @typing.override
    def _read_value(self, stream: "StreamReader") -> int:
        return stream.read(self.underlaying_type)


@dataclasses.dataclass
class _PFieldInfoBase[U: P_TYPES_T, O](_FieldInfoWithUnderlayingType[U, U, O]):
    @typing.override
    def _write_value(self, stream: "StreamWriter", value: U) -> None:
        stream.write(value)

    @typing.override
    def _read_value(self, stream: "StreamReader") -> U:
        return stream.read(self.underlaying_type)


# endregion

# region FieldInfo


@dataclasses.dataclass
class RFieldInfo[U: R_TYPES_T](_RFieldInfoBase[U, bytes]):
    @typing.override
    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> bytes:
        return self._read_value(stream)

    @typing.override
    def _marshal_value(self, stream: "StreamWriter", obj: bytes) -> None:
        self._write_value(stream, obj)


@dataclasses.dataclass
class CFieldInfo[U: C_TYPES_T](_CFieldInfoBase[U, int]):
    @typing.override
    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> int:
        return self._read_value(stream)

    @typing.override
    def _marshal_value(self, stream: "StreamWriter", obj: int) -> None:
        self._write_value(stream, obj)


@dataclasses.dataclass
class PFieldInfo[O: P_TYPES_T](_PFieldInfoBase[O, O]):
    @typing.override
    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> O:
        return self._read_value(stream)

    @typing.override
    def _marshal_value(self, stream: "StreamWriter", obj: O) -> None:
        self._write_value(stream, obj)


# endregion

# region FullFieldInfo


@dataclasses.dataclass
class FullRFieldInfo[U: R_TYPES_T, O](_RFieldInfoBase[U, O]):
    parser: Callable[[bytes], O]
    serializer: Callable[[O], bytes]

    @typing.override
    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> O:
        u_value = stream.read(self.underlaying_type)
        return self.parser(u_value)

    @typing.override
    def _marshal_value(self, stream: "StreamWriter", obj: O) -> None:
        u_value = self.serializer(obj)
        stream.write(u_value, self.underlaying_type)


@dataclasses.dataclass
class FullCFieldInfo[U: C_TYPES_T, O](_CFieldInfoBase[U, O]):
    parser: Callable[[int], O]
    serializer: Callable[[O], int]

    @typing.override
    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> O:
        u_value = stream.read(self.underlaying_type)
        return self.parser(u_value)

    @typing.override
    def _marshal_value(self, stream: "StreamWriter", obj: O) -> None:
        u_value = self.serializer(obj)
        stream.write(u_value, self.underlaying_type)


@dataclasses.dataclass
class FullPFieldInfo[U: P_TYPES_T, O](_PFieldInfoBase[U, O]):
    parser: Callable[[U], O]
    serializer: Callable[[O], U]

    @typing.override
    def _unmarshal_value(self, stream: "StreamReader", parsed: Mapping[str, typing.Any]) -> O:
        u_value = self._read_value(stream)
        return self.parser(u_value)

    @typing.override
    def _marshal_value(self, stream: "StreamWriter", obj: O) -> None:
        u_value = self.serializer(obj)
        self._write_value(stream, u_value)


# endregion


# region Field


@dataclasses.dataclass
class RField:
    type: type[R_TYPES_T]
    parser: Callable[[bytes], typing.Any] | None = None
    serializer: Callable[[typing.Any], bytes] | None = None


def is_r_field(obj: typing.Any) -> typing.TypeGuard[RField]:
    return isinstance(obj, RField)


@dataclasses.dataclass
class CField:
    type: type[C_TYPES_T]
    parser: Callable[[int], typing.Any] | None = None
    serializer: Callable[[typing.Any], int] | None = None


def is_c_field(obj: typing.Any) -> typing.TypeGuard[CField]:
    return isinstance(obj, CField)


@dataclasses.dataclass
class PField[T: P_TYPES_T]:
    type: type[T]
    parser: Callable[[T], typing.Any] | None = None
    serializer: Callable[[typing.Any], T] | None = None


def is_p_field(obj: typing.Any) -> typing.TypeGuard[PField[typing.Any]]:
    return isinstance(obj, PField)


# endregion

# region field factory


@typing.overload
def field(
    type: type[R_TYPES_T],
    parser: Callable[[bytes], typing.Any] | None = ...,
    serializer: Callable[[typing.Any], bytes] | None = ...,
) -> RField: ...


@typing.overload
def field(
    type: type[C_TYPES_T],
    parser: Callable[[int], typing.Any] | None = ...,
    serializer: Callable[[typing.Any], int] | None = ...,
) -> CField: ...


@typing.overload
def field[T: P_TYPES_T](
    type: type[T],
    parser: Callable[[T], typing.Any] | None = ...,
    serializer: Callable[[typing.Any], T] | None = ...,
) -> PField[typing.Any]: ...


def field(
    type: type[UNDERLAYING_TYPES_T],
    parser: Callable[[typing.Any], typing.Any] | None = None,
    serializer: Callable[[typing.Any], typing.Any] | None = None,
) -> CField | PField[typing.Any] | RField:
    if is_c_types_t(type):
        return CField(type=type, parser=parser, serializer=serializer)
    elif is_p_types_t(type):
        return PField(type=type, parser=parser, serializer=serializer)
    elif is_r_types_t(type):
        return RField(type=type, parser=parser, serializer=serializer)
    else:
        raise TypeError(f"Unsupported type {type} for field. Supported types are: {UNDERLAYING_TYPES}")


# endregion


@dataclasses.dataclass
class _ClassInfo:
    header: bool
    children: dict[typing.Any, type["Packet"]] = dataclasses.field(default_factory=dict[typing.Any, type["Packet"]])
    fields: dict[str, FieldInfoBase[typing.Any]] = dataclasses.field(
        default_factory=dict[str, FieldInfoBase[typing.Any]]
    )
    headers: dict[str, typing.Any] = dataclasses.field(default_factory=dict[str, typing.Any])

    def get_descriptor_field(self) -> FieldInfoBase[typing.Any]:
        for field in self.fields.values():
            if field.is_discriminator:
                return field
        raise ValueError("No discriminator field found")

    def get_child(self, parsed: Mapping[str, typing.Any]) -> type["Packet"]:
        descriptor_field = self.get_descriptor_field()
        descriptor_value = parsed[descriptor_field.name]
        if descriptor_value not in self.children:
            raise ValueError(f"Unknown descriptor value {descriptor_value} for field {descriptor_field.name} in class")
        return self.children[descriptor_value]


def _generate_field_info(cls: type, name: str, annotation: type) -> FieldInfoBase[typing.Any] | None:
    # region ClassVar
    is_class_var = _is_classvar(annotation)
    if is_class_var:
        annotation = typing.get_args(annotation)[0]

    const_value: typing.Any | Notset = NOTSET
    if is_class_var and hasattr(cls, name):
        const_value = getattr(cls, name)

    is_discriminator = is_class_var and const_value is NOTSET
    # endregion

    is_annotated = typing.get_origin(annotation) is typing.Annotated

    is_excluded = False
    if is_annotated:
        _args = typing.get_args(annotation)
        overlaying_type = _args[0]
        annotations = _args[1:]
        for ann in annotations:
            if ann is exclude:
                is_excluded = True
                break
    else:
        overlaying_type: type = annotation
        annotations: tuple[typing.Any, ...] = ()

    if _is_field_proto_t(overlaying_type):
        return FieldProtoInfo(
            name=name,
            custom_type=overlaying_type,
            is_class_var=is_class_var,
            is_discriminator=is_discriminator,
            const_value=const_value,
            is_excluded=is_excluded,
        )

    if isinstance(overlaying_type, typing.NewType):
        overlaying_type = getattr(overlaying_type, "__supertype__")

    if not is_annotated:
        if isinstance(overlaying_type, UnionType):  # type: ignore[misc] This can be union type maybe
            return FieldInfoBase(
                name=name,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                is_excluded=is_excluded,
            )
        if overlaying_type is None:  # pyright: ignore[reportUnnecessaryComparison] This might be None
            return None
        if issubclass(overlaying_type, Packet):
            child_info = get_class_info(overlaying_type)
            child_discriminator_name = None
            if child_info.header:
                child_discriminator = child_info.get_descriptor_field()
                child_discriminator_name = child_discriminator.name

            return FieldPacketInfo(
                name=name,
                packet_type=overlaying_type,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                nested=False,
                is_excluded=is_excluded,
                discriminator_name=child_discriminator_name,
            )
        if overlaying_type not in P_TYPES:
            raise TypeError(
                f"Field {name} in class {cls.__name__} has unsupported type {overlaying_type}. Supported types are: {P_TYPES} and typing.Annotated[...]"
            )
        return PFieldInfo(
            name=name,
            underlaying_type=overlaying_type,
            is_class_var=is_class_var,
            is_discriminator=is_discriminator,
            const_value=const_value,
            is_excluded=is_excluded,
        )

    if len(annotations) == 1:
        underlaying_type = annotations[0]
        if is_r_types_t(underlaying_type):
            if overlaying_type is bytes:
                return RFieldInfo(
                    name=name,
                    underlaying_type=underlaying_type,
                    is_class_var=is_class_var,
                    is_discriminator=is_discriminator,
                    const_value=const_value,
                    is_excluded=is_excluded,
                )

            return FullRFieldInfo(
                name=name,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                underlaying_type=underlaying_type,
                parser=make_parser(overlaying_type),
                serializer=make_serializer(bytes),
                is_excluded=is_excluded,
            )
        if is_c_types_t(underlaying_type):
            if overlaying_type is int:
                return CFieldInfo(
                    name=name,
                    underlaying_type=underlaying_type,
                    is_class_var=is_class_var,
                    is_discriminator=is_discriminator,
                    const_value=const_value,
                    is_excluded=is_excluded,
                )

            return FullCFieldInfo(
                name=name,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                underlaying_type=underlaying_type,
                parser=make_parser(overlaying_type),
                serializer=make_serializer(int),
                is_excluded=is_excluded,
            )
        if is_p_types_t(underlaying_type):
            return FullPFieldInfo(
                name=name,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                underlaying_type=underlaying_type,
                parser=make_parser(overlaying_type),
                serializer=make_serializer(underlaying_type),
                is_excluded=is_excluded,
            )
        if _is_field_class_proto_t(underlaying_type):
            return FieldProtoInfo(
                name=name,
                custom_type=underlaying_type,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                is_excluded=is_excluded,
            )

    for underlaying_type in annotations:
        if is_r_field(underlaying_type):
            _field = underlaying_type
            _underlaying_type = _field.type
            return FullRFieldInfo(
                name=name,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                underlaying_type=_underlaying_type,
                parser=_field.parser if _field.parser is not None else make_parser(overlaying_type),
                serializer=_field.serializer if _field.serializer is not None else make_serializer(bytes),
                is_excluded=is_excluded,
            )
        if is_p_field(underlaying_type):
            _field = underlaying_type
            _underlaying_type = _field.type
            return FullPFieldInfo(
                name=name,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                underlaying_type=_underlaying_type,
                parser=_field.parser if _field.parser is not None else make_parser(overlaying_type),
                serializer=_field.serializer if _field.serializer is not None else make_serializer(_underlaying_type),
                is_excluded=is_excluded,
            )
        if is_c_field(underlaying_type):
            _field = underlaying_type
            _underlaying_type = _field.type
            return FullCFieldInfo(
                name=name,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                underlaying_type=_underlaying_type,
                parser=_field.parser if _field.parser is not None else make_parser(overlaying_type),
                serializer=_field.serializer if _field.serializer is not None else make_serializer(int),
                is_excluded=is_excluded,
            )
        if _is_field_class_proto_t(underlaying_type):
            return FieldProtoInfo(
                name=name,
                custom_type=underlaying_type,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                is_excluded=is_excluded,
            )
        if underlaying_type is nested and issubclass(overlaying_type, Packet):
            child_info = get_class_info(overlaying_type)
            child_discriminator_name = None
            if child_info.header:
                child_discriminator = child_info.get_descriptor_field()
                child_discriminator_name = child_discriminator.name
            return FieldPacketInfo(
                name=name,
                packet_type=overlaying_type,
                is_class_var=is_class_var,
                is_discriminator=is_discriminator,
                const_value=const_value,
                nested=True,
                is_excluded=is_excluded,
                discriminator_name=child_discriminator_name,
            )

    if issubclass(overlaying_type, Packet):
        child_info = get_class_info(overlaying_type)
        child_discriminator_name = None
        if child_info.header:
            child_discriminator = child_info.get_descriptor_field()
            child_discriminator_name = child_discriminator.name
        return FieldPacketInfo(
            name=name,
            packet_type=overlaying_type,
            is_class_var=is_class_var,
            is_discriminator=is_discriminator,
            const_value=const_value,
            nested=False,
            is_excluded=is_excluded,
            discriminator_name=child_discriminator_name,
        )
    if overlaying_type in P_TYPES:
        return PFieldInfo(
            name=name,
            underlaying_type=overlaying_type,
            is_class_var=is_class_var,
            is_discriminator=is_discriminator,
            const_value=const_value,
            is_excluded=is_excluded,
        )

    raise TypeError(
        f"Field {name} in class {cls.__name__} has unsupported type {annotation}. Supported types are: {UNDERLAYING_TYPES} and typing.Annotated[...]"
    )


def _process_field(
    cls: type, name: str, annotation: type, parent_field_info: FieldInfoBase[typing.Any] | None
) -> FieldInfoBase[typing.Any] | None:
    field_info = _generate_field_info(cls, name, annotation)
    if field_info is None:
        return None
    if parent_field_info is None:
        return field_info
    if parent_field_info.is_discriminator:
        if field_info.const_value is NOTSET:
            raise TypeError(
                f"Class {cls.__name__} is missing constant value for discriminator field {name} from parent class"
            )
    else:
        if field_info.const_value != parent_field_info.const_value:
            raise TypeError(
                f"Class {cls.__name__} is overriding classvar field {name} from parent class with a new value, which is not allowed"
            )
    return field_info


def _process_class(cls: "type[Packet]") -> None:
    if _is_dataclass(cls):
        return

    dataclasses.dataclass(slots=True, kw_only=True)(cls)

    fields: dict[str, FieldInfoBase[typing.Any]] = {}

    parent = get_parent_class(cls)
    parent_info = None if parent is None else get_class_info(parent)
    if parent is not None and parent_info is not None:
        if not parent_info.header:
            raise TypeError(
                f"Class {cls.__name__} has parent class {parent.__name__} which is not a header class, but {cls.__name__} is a header class."
            )

        for field_name, field in parent_info.fields.items():
            fields[field_name] = field

    field_annotations = inspect.get_annotations(cls)
    for field_name, field_annotation in field_annotations.items():
        field_info = _process_field(cls, field_name, field_annotation, fields.get(field_name))
        if field_info is not None:
            fields[field_name] = field_info
        else:
            if field_name in fields:
                del fields[field_name]

    if parent is not None and parent_info is not None:
        parent_field = parent_info.get_descriptor_field()
        child_field = fields[parent_field.name]

        if child_field.const_value is NOTSET:
            raise TypeError(
                f"Class {cls.__name__} is missing constant value for discriminator field {parent_field.name} from parent class {parent.__name__}"
            )

        if child_field.const_value in parent_info.children:
            raise TypeError(
                f"Class {cls.__name__} has descriptor value {child_field.const_value} for field {child_field.name}, but this value is already used by class {parent_info.children[child_field.const_value].__name__}"
            )
        parent_info.children[child_field.const_value] = cls

    header = any(x.is_discriminator for x in fields.values())

    info = _ClassInfo(header=header, fields=fields)

    setattr(cls, _SSH_PROTO_TYPE_INFO, info)


@typing.dataclass_transform(kw_only_default=True, frozen_default=True)
class Packet:
    def __init_subclass__(cls: "type[Packet]") -> None:
        _process_class(cls)

    @classmethod
    def model_unmarshal(cls, stream: "StreamReader", parsed: dict[str, typing.Any]) -> typing.Self:
        return cls(**parsed)  # type: ignore[call-arg]

    def model_marshal(self, stream: "StreamWriter") -> None:
        pass

    def __bytes__(self) -> bytes:
        return marshal(self)


def is_packet(cls: type) -> bool:
    return hasattr(cls, _SSH_PROTO_TYPE_INFO)


def get_class_info(cls: Packet | type[Packet]) -> _ClassInfo:
    return getattr(cls, _SSH_PROTO_TYPE_INFO)


def get_parent_class(cls: type[Packet]) -> type[Packet] | None:
    if is_packet(cls.__bases__[0]):
        return cls.__bases__[0]
    return None


class InvalidHeader(RuntimeError):
    pass


def _unmarshal[T: Packet](
    stream: StreamReader, cls: type[T], parsed: dict[str, typing.Any]
) -> tuple[dict[str, typing.Any], type[T]]:
    info = get_class_info(cls)

    for field in info.fields.values():
        parsed[field.name] = field.unmarshal(stream, parsed)
        if field.is_discriminator:
            break

    if not info.header:
        return parsed, cls

    parsed, child_cls = _unmarshal(stream, info.get_child(parsed), parsed)
    return parsed, typing.cast(type[T], child_cls)


def unmarshal[T: Packet](cls: type[T], data: bytes | StreamReader, parsed: dict[str, typing.Any] | None = None) -> T:
    if parsed is None:
        parsed = {}
    with StreamReader.of(data) as stream:
        parsed, cls = _unmarshal(stream, cls, parsed)

        for field in get_class_info(cls).fields.values():
            if field.is_class_var:
                del parsed[field.name]

        return cls.model_unmarshal(stream, parsed)  # type: ignore[call-arg]


def marshal(obj: Packet, stream: StreamWriter | None = None) -> bytes:
    info = get_class_info(obj)
    if info.header:
        raise ValueError("Cannot marshal header class directly")

    with StreamWriter.of(stream) as _stream:
        for field in info.fields.values():
            if field.is_excluded:
                continue
            field.marshal(_stream, obj)

        obj.model_marshal(_stream)

        return _stream.get_bytes()
