from typing import ClassVar

import pytest

from ssh_proto_types import Packet, marshal, unmarshal
from ssh_proto_types.packet import InvalidHeader


class SimplePacket(Packet):
    a: int
    b: bytes
    c: str


class DefaultFieldPacket(Packet):
    a: int
    b: bytes
    c: str = "fdas"


class HeaderPacket(Packet):
    version: ClassVar[int] = 1
    mode: ClassVar[str] = "active"
    name: str


class ParentPacket(Packet):
    version: ClassVar[int] = 1
    mode: ClassVar[str]


class ChildPacketA(ParentPacket):
    mode: ClassVar[str] = "active"
    a: int


testdata_marshal: list[tuple[Packet, bytes]] = [
    (
        SimplePacket(a=1, b=b"hello", c="world"),
        b"\x00\x00\x00\x01\x01\x00\x00\x00\x05hello\x00\x00\x00\x05world",
    ),
    (
        DefaultFieldPacket(a=1, b=b"hello", c="world"),
        b"\x00\x00\x00\x01\x01\x00\x00\x00\x05hello\x00\x00\x00\x05world",
    ),
    (
        DefaultFieldPacket(a=1, b=b"hello"),
        b"\x00\x00\x00\x01\x01\x00\x00\x00\x05hello\x00\x00\x00\x04fdas",
    ),
    (
        HeaderPacket(name="test"),
        b"\x00\x00\x00\x01\x01\x00\x00\x00\x06active\x00\x00\x00\x04test",
    ),
    (
        ChildPacketA(a=42),
        b"\x00\x00\x00\x01\x01\x00\x00\x00\x06active\x00\x00\x00\x01\x2a",
    ),
]


@pytest.mark.parametrize("value,want", testdata_marshal)
def test_marshal(value: Packet, want: bytes) -> None:
    got = marshal(value)
    assert got == want


testdata_unmarshal: list[tuple[type[Packet], bytes, Packet]] = [
    (value.__class__, want, value) for value, want in testdata_marshal
]


@pytest.mark.parametrize("cls,value,want", testdata_unmarshal)
def test_unmarshal(cls: type[Packet], value: bytes, want: Packet) -> None:
    got = unmarshal(cls, value)
    assert got == want


def test_unmarshal_parent_raises() -> None:
    with pytest.raises(ValueError):
        unmarshal(
            ParentPacket,
            b"\x00\x00\x00\x01\x01\x00\x00\x00\x05activ\x00\x00\x00\x01\x2a",
        )


def test_unmarshal_parent_finds_child() -> None:
    got = unmarshal(
        ParentPacket,
        b"\x00\x00\x00\x01\x01\x00\x00\x00\x06active\x00\x00\x00\x01\x2a",
    )
    want = ChildPacketA(a=42)
    assert got == want


def test_marshal_parent_raises() -> None:
    with pytest.raises(ValueError):
        marshal(ParentPacket())


def test_unmarshal_invalid_header():
    class Header(Packet):
        version: ClassVar[int] = 2
        mode: ClassVar[str] = "active"
        name: str

    with pytest.raises(InvalidHeader):
        unmarshal(
            Header,
            b"\x00\x00\x00\x01\x01\x00\x00\x00\x06active\x00\x00\x00\x04test",
        )


def test_unmarshal_reader():
    class SimplePacket(Packet):
        a: int
        b: bytes
        c: str

    data = b"\x00\x00\x00\x01\x01\x00\x00\x00\x05hello\x00\x00\x00\x05world\x01"
    from ssh_proto_types import StreamReader

    reader = StreamReader(data)
    got = unmarshal(SimplePacket, reader)
    want = SimplePacket(a=1, b=b"hello", c="world")
    assert got == want
    assert not reader.eof()
    assert reader.read_raw(1) == b"\x01"
    assert reader.eof()
