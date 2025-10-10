import ctypes
import dataclasses
from collections.abc import Mapping
from typing import Annotated, Any, ClassVar, Literal, Self, override

import pytest

from ssh_proto_types import Packet, StreamReader, StreamWriter, marshal, rest, unmarshal
from ssh_proto_types.basetypes import Notset, exclude, nested
from ssh_proto_types.packet import FieldClassProto, FieldProto, InvalidHeader, PFieldInfo, field, get_class_info


def test_invalid_type():
    with pytest.raises(TypeError):

        class InvalidPacket(Packet):  # pyright: ignore[reportUnusedClass]
            a: float


def test_invalid_type_field_annotation():
    with pytest.raises(TypeError):

        class InvalidPacket(Packet):  # pyright: ignore[reportUnusedClass]
            a: Annotated[float, float]


def test_invalid_type_field():
    with pytest.raises(TypeError):

        class InvalidPacket(Packet):  # pyright: ignore[reportUnusedClass]
            a: Annotated[int, field(float)]  # pyright: ignore[reportCallIssue, reportArgumentType]


def test_invalid_parent():
    class InvalidParent(Packet):
        a: int

    with pytest.raises(TypeError):

        class Child(InvalidParent):  # pyright: ignore[reportUnusedClass]
            a: ClassVar[int] = 1  # pyright: ignore[reportIncompatibleVariableOverride]


def test_invalid_child():
    class Parent(Packet):
        a: ClassVar[int]

    with pytest.raises(TypeError):

        class InvalidChild(Parent):  # pyright: ignore[reportUnusedClass]
            a: ClassVar[int]


def test_class_info() -> None:
    class APacket(Packet):
        a: int
        b: bytes

    info = get_class_info(APacket)
    assert not info.header
    assert info.fields["a"] == PFieldInfo(
        name="a",
        is_class_var=False,
        is_discriminator=False,
        const_value=Notset.Notset,
        underlaying_type=int,
        is_excluded=False,
    )
    assert info.fields["b"] == PFieldInfo(
        name="b",
        is_class_var=False,
        is_discriminator=False,
        const_value=Notset.Notset,
        underlaying_type=bytes,
        is_excluded=False,
    )


def test_class_excluded_info() -> None:
    class APacket(Packet):
        a: ClassVar[Annotated[int, exclude]] = 1
        b: ClassVar[bytes] = b"const"
        c: Annotated[bytes, exclude]
        d: int

    info = get_class_info(APacket)
    assert not info.header
    assert info.fields["a"] == PFieldInfo(
        name="a",
        is_class_var=True,
        is_discriminator=False,
        const_value=1,
        underlaying_type=int,
        is_excluded=True,
    )
    assert info.fields["b"] == PFieldInfo(
        name="b",
        is_class_var=True,
        is_discriminator=False,
        const_value=b"const",
        underlaying_type=bytes,
        is_excluded=False,
    )
    assert info.fields["c"] == PFieldInfo(
        name="c",
        is_class_var=False,
        is_discriminator=False,
        const_value=Notset.Notset,
        underlaying_type=bytes,
        is_excluded=True,
    )
    assert info.fields["d"] == PFieldInfo(
        name="d",
        is_class_var=False,
        is_discriminator=False,
        const_value=Notset.Notset,
        underlaying_type=int,
        is_excluded=False,
    )


def test_simple_annotatin():
    class SimplePacket(Packet):
        a: Annotated[int, ctypes.c_uint8]
        b: Annotated[bytes, bytes]
        c: Annotated[
            str,
            field(
                bytes,
                parser=lambda x: x.decode("utf8"),
                serializer=lambda x: x.encode("utf8"),
            ),
        ]
        d: Annotated[int, field(ctypes.c_uint16)] = 2

    unmarshal(SimplePacket, marshal(SimplePacket(a=1, b=b"hello", c="world")))


def test_invalid_child_discriminator():
    class Parent(Packet):
        version: ClassVar[int]

    with pytest.raises(TypeError):

        class Child(Parent):  # pyright: ignore[reportUnusedClass]
            n: int


def test_strange_order() -> None:
    class StrangeOrderPacket(Packet):
        a: ClassVar[int] = 1
        b: int
        c: ClassVar[str]

    class ChildStrangeOrderPacket(StrangeOrderPacket):
        c: ClassVar[str] = "active"
        d: ClassVar[int] = 2
        e: int

    obj = ChildStrangeOrderPacket(b=1, e=3)
    got = unmarshal(ChildStrangeOrderPacket, marshal(obj))
    assert got == obj


def test_strange_order_2() -> None:
    class StrangeOrderPacket(Packet):
        a: ClassVar[int] = 1
        c: ClassVar[str]

    with pytest.raises(TypeError):

        class ChildStrangeOrderPacket(StrangeOrderPacket):  # pyright: ignore[reportUnusedClass]
            a: ClassVar[int] = 2
            c: ClassVar[str] = "active"


def test_double_discriminator():
    class Parent(Packet):
        version: ClassVar[int] = 1
        mode: ClassVar[str]

    class ChildPacketA(Parent):  # pyright: ignore[reportUnusedClass]
        mode: ClassVar[str] = "active"
        a: int

    with pytest.raises(TypeError):

        class ChildPacketB(Parent):  # pyright: ignore[reportUnusedClass]
            mode: ClassVar[str] = "active"
            b: int


def test_very_illegal_packet():
    class Parent(Packet):
        a: ClassVar[int] = 1
        b: ClassVar[int]

    class ChildPacketA(Packet):
        a: ClassVar[int] = 1
        b: ClassVar[int] = 2

    get_class_info(Parent).children[1] = ChildPacketA

    assert marshal(ChildPacketA()) == b"\x00\x00\x00\x01\x01\x00\x00\x00\x01\x02"
    with pytest.raises(InvalidHeader):
        unmarshal(Parent, b"\x00\x00\x00\x01\x01\x00\x00\x00\x01\x01")


def test_packet_with_rest():
    class RestPacket(Packet):
        a: int
        rest: Annotated[bytes, rest]  # type: ignore[type-arg]

    obj = RestPacket(a=1, rest=b"restdata")
    got = unmarshal(RestPacket, marshal(obj))
    assert got == obj


class PaddingCls(FieldClassProto[bool]):
    BLOCK_SIZE = 8

    @override
    @classmethod
    def unmarshal_sshwire(cls, stream: StreamReader, parsed: Mapping[str, Any]) -> bool:
        missing_amount = (cls.BLOCK_SIZE - (stream.amount_read() % cls.BLOCK_SIZE)) % cls.BLOCK_SIZE
        value = stream.read_raw(missing_amount)  # Discard padding bytes
        return value == bytes(range(1, missing_amount + 1))

    @override
    @classmethod
    def marshal_sshwire(cls, obj: bool, stream: StreamWriter) -> None:
        if not obj:
            raise ValueError("Padding field must be True")

        missing_amount = (cls.BLOCK_SIZE - (len(stream) % cls.BLOCK_SIZE)) % cls.BLOCK_SIZE
        stream.write_raw(bytes(range(1, missing_amount + 1)))  # Write padding bytes


def test_proto_works() -> None:
    from ssh_proto_types.packet import _FIELD_CLASS_PROTO_SIG, _Signatures  # pyright: ignore[reportPrivateUsage]

    obj_sig = _Signatures.from_cls(PaddingCls)
    obj = obj_sig.get_obj()
    assert obj is bool
    _proto_sig = _FIELD_CLASS_PROTO_SIG.replace_obj(obj)
    assert obj_sig.marshal_sig == _proto_sig.marshal_sig
    assert obj_sig.unmarshal_sig == _proto_sig.unmarshal_sig
    assert obj_sig.marshal_ann == _proto_sig.marshal_ann
    assert obj_sig.unmarshal_ann == _proto_sig.unmarshal_ann


def test_packet_with_padding():
    class PaddingPacket(Packet):
        a: int
        padding: Annotated[bool, PaddingCls]

    obj = PaddingPacket(a=1, padding=True)
    v = marshal(obj)
    assert v == b"\x00\x00\x00\x01\x01\x01\x02\x03"
    got = unmarshal(PaddingPacket, marshal(obj))
    assert got == obj


def test_packet_with_padding_unmarshal():
    class PaddingPacket(Packet):
        a: int
        padding: Annotated[bool, PaddingCls]

    class PaddingPacket2(Packet):
        a: int
        padding: ClassVar[Annotated[bool, PaddingCls]] = True

    valid = b"\x00\x00\x00\x01\x01\x01\x02\x03"
    invalid = b"\x00\x00\x00\x01\x01\x01\x02\x04"

    got = unmarshal(PaddingPacket, valid)
    assert got == PaddingPacket(a=1, padding=True)

    got = unmarshal(PaddingPacket, invalid)
    assert got == PaddingPacket(a=1, padding=False)

    got = unmarshal(PaddingPacket2, valid)
    assert got == PaddingPacket2(a=1)

    with pytest.raises(InvalidHeader):
        unmarshal(PaddingPacket2, invalid)


@dataclasses.dataclass
class Padding(FieldProto):
    BLOCK_SIZE = 8
    require: Literal[True] = True

    @override
    @classmethod
    def unmarshal_sshwire(cls, stream: StreamReader, parsed: Mapping[str, Any]) -> Self:
        missing_amount = (cls.BLOCK_SIZE - (stream.amount_read() % cls.BLOCK_SIZE)) % cls.BLOCK_SIZE
        value = stream.read_raw(missing_amount)  # Discard padding bytes
        if value != bytes(range(1, missing_amount + 1)):
            raise ValueError("Invalid padding bytes")
        return cls()

    @override
    def marshal_sshwire(self, stream: StreamWriter) -> None:
        missing_amount = (self.BLOCK_SIZE - (len(stream) % self.BLOCK_SIZE)) % self.BLOCK_SIZE
        stream.write_raw(bytes(range(1, missing_amount + 1)))  # Write padding bytes


def test_packet_with_padding_obj():
    class PaddingPacket(Packet):
        a: int
        padding: Padding = dataclasses.field(default_factory=Padding)

    obj = PaddingPacket(a=1)
    v = marshal(obj)
    assert v == b"\x00\x00\x00\x01\x01\x01\x02\x03"
    got = unmarshal(PaddingPacket, marshal(obj))
    assert got == obj


def test_composition_packet() -> None:
    class InnerPacket(Packet):
        x: int
        y: int

    class OuterPacket(Packet):
        a: int
        inner: InnerPacket
        b: bytes

    assert marshal(OuterPacket(a=1, inner=InnerPacket(x=2, y=3), b=b"hello")) == (
        b"\x00\x00\x00\x01\x01"  # a
        b"\x00\x00\x00\x01\x02"  # inner.x
        b"\x00\x00\x00\x01\x03"  # inner.y
        b"\x00\x00\x00\x05hello"  # b
    )


def test_nested_packet() -> None:
    class InnerPacket(Packet):
        x: int
        y: int

    class OuterPacket(Packet):
        a: int
        inner: Annotated[InnerPacket, nested]
        b: bytes

    assert marshal(OuterPacket(a=1, inner=InnerPacket(x=2, y=3), b=b"hello")) == (
        b"\x00\x00\x00\x01\x01"  # a
        b"\x00\x00\x00\x0a"  # inner length
        b"\x00\x00\x00\x01\x02"  # inner.x
        b"\x00\x00\x00\x01\x03"  # inner.y
        b"\x00\x00\x00\x05hello"  # b
    )


def test_exclude_packet_marshal() -> None:
    class InnerPacket(Packet):
        x: ClassVar[Annotated[int, exclude]] = 1
        y: int

    class OuterPacket(Packet):
        a: Annotated[int, exclude] = 1
        inner: Annotated[InnerPacket, nested]
        b: bytes

    assert marshal(OuterPacket(inner=InnerPacket(y=3), b=b"hello")) == (
        b""  # a excluded
        b"\x00\x00\x00\x05"  # length of inner
        b""  # x excluded
        b"\x00\x00\x00\x01\x03"  # inner.y
        b"\x00\x00\x00\x05hello"  # b
    )


def test_exclude_packet_unmarshal() -> None:
    class InnerPacket(Packet):
        y: int

    class OuterPacket(Packet):
        a: Annotated[int, exclude] = 1
        inner: Annotated[InnerPacket, nested]
        b: bytes

    arg = (
        b""  # a excluded
        b"\x00\x00\x00\x05"  # length of inner
        b""  # x excluded
        b"\x00\x00\x00\x01\x03"  # inner.y
        b"\x00\x00\x00\x05hello"  # b
    )

    want = OuterPacket(a=2, inner=InnerPacket(y=3), b=b"hello")
    got = unmarshal(OuterPacket, arg, parsed={"a": 2})
    assert got == want


def test_exclude_parent_unmarshal() -> None:
    class ParentPacket(Packet):
        a: ClassVar[Annotated[int, exclude]]

    class ChildPacket(ParentPacket):
        a: ClassVar[Annotated[int, exclude]] = 1
        b: bytes

    arg = b"\x00\x00\x00\x05hello"  # b

    want = ChildPacket(b=b"hello")
    got = unmarshal(ParentPacket, arg, parsed={"a": 1})
    assert got == want


def test_exclude_parent_marshal() -> None:
    class ParentPacket(Packet):
        a: ClassVar[Annotated[int, exclude]]

    class ChildPacket(ParentPacket):
        a: ClassVar[Annotated[int, exclude]] = 1
        b: bytes

    arg = ChildPacket(b=b"hello")
    want = b"\x00\x00\x00\x05hello"  # b
    got = marshal(arg)
    assert got == want


def test_exclude_parent_strange_marshal() -> None:
    class ParentPacket(Packet):
        a: ClassVar[int]
        b: str
        c: int | None
        d: str

    class ChildPacketA(ParentPacket):
        a: ClassVar[int] = 1
        c: None = None

    class ChildPacketB(ParentPacket):
        a: ClassVar[int] = 2
        c: int

    arg = ChildPacketA(b="hello", d="world")
    want = (
        b"\x00\x00\x00\x01\x01"  # a
        b"\x00\x00\x00\x05hello"  # b
        b""  # c excluded
        b"\x00\x00\x00\x05world"  # d
    )
    got = marshal(arg)
    assert got == want

    arg = ChildPacketB(b="hello", c=3, d="world")
    want = (
        b"\x00\x00\x00\x01\x02"  # a
        b"\x00\x00\x00\x05hello"  # b
        b"\x00\x00\x00\x01\x03"  # c
        b"\x00\x00\x00\x05world"  # d
    )
    got = marshal(arg)
    assert got == want


def test_exclude_parent_strange_unmarshal() -> None:
    class ParentPacket(Packet):
        a: ClassVar[int]
        b: str
        c: int | None
        d: str

    class ChildPacketA(ParentPacket):
        a: ClassVar[int] = 1
        c: None = None

    class ChildPacketB(ParentPacket):
        a: ClassVar[int] = 2
        c: int

    want = ChildPacketA(b="hello", d="world")
    arg = (
        b"\x00\x00\x00\x01\x01"  # a
        b"\x00\x00\x00\x05hello"  # b
        b""  # c excluded
        b"\x00\x00\x00\x05world"  # d
    )
    got = unmarshal(ParentPacket, arg)
    assert got == want

    want = ChildPacketB(b="hello", c=3, d="world")
    arg = (
        b"\x00\x00\x00\x01\x02"  # a
        b"\x00\x00\x00\x05hello"  # b
        b"\x00\x00\x00\x01\x03"  # c
        b"\x00\x00\x00\x05world"  # d
    )
    got = unmarshal(ParentPacket, arg)
    assert got == want
