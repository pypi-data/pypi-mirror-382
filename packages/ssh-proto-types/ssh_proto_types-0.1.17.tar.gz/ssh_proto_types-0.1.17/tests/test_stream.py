import ctypes
from typing import Any

import pytest

from ssh_proto_types import StreamReader, StreamWriter, rest

testdata_writer: list[tuple[type, Any, bytes]] = [
    (ctypes.c_uint8, 1, b"\x01"),
    (ctypes.c_uint16, 1, b"\x00\x01"),
    (ctypes.c_uint32, 1, b"\x00\x00\x00\x01"),
    (ctypes.c_uint64, 1, b"\x00\x00\x00\x00\x00\x00\x00\x01"),
    (ctypes.c_uint8, 2**8 - 1, b"\xff"),
    (ctypes.c_uint16, 2**16 - 1, b"\xff\xff"),
    (ctypes.c_uint32, 2**32 - 1, b"\xff\xff\xff\xff"),
    (ctypes.c_uint64, 2**64 - 1, b"\xff\xff\xff\xff\xff\xff\xff\xff"),
    (int, 1, b"\x00\x00\x00\x01\x01"),
    (int, -1, b"\x00\x00\x00\x01\xff"),
    (int, -255, b"\x00\x00\x00\x02\xff\x01"),
    (int, -256, b"\x00\x00\x00\x02\xff\x00"),
    (int, 0, b"\x00\x00\x00\x00"),
    (int, 0x9A378F9B2E332A7, bytes.fromhex("0000000809a378f9b2e332a7")),
    (int, 0x80, b"\x00\x00\x00\x02\x00\x80"),
    (int, -0x1234, bytes.fromhex("00000002edcc")),
    (int, 2**32 - 1, b"\x00\x00\x00\x05\x00\xff\xff\xff\xff"),
    (bytes, b"hello", b"\x00\x00\x00\x05hello"),
    (str, "hello", b"\x00\x00\x00\x05hello"),
]


@pytest.mark.parametrize("ctype,value,want", testdata_writer)
def test_streamwriter(ctype: type, value: Any, want: bytes) -> None:
    writer = StreamWriter()
    writer.write(value, ctype)
    got = writer.get_bytes()
    assert got == want


testdata_reader: list[tuple[type, bytes, Any]] = [(ctype, want, value) for ctype, value, want in testdata_writer]


@pytest.mark.parametrize("ctype,value,want", testdata_reader)
def test_streamreader(ctype: type, value: bytes, want: Any) -> None:
    reader = StreamReader(value)
    got = reader.read(ctype)
    assert got == want
    assert reader.eof()


def test_streamreader_eof() -> None:
    reader = StreamReader(b"\x00\x01")
    assert not reader.eof()
    assert reader.read(ctypes.c_uint16) == 1
    assert reader.eof()
    with pytest.raises(EOFError):
        reader.read(ctypes.c_uint8)


def test_streamwriter_invalid_type():
    writer = StreamWriter()
    with pytest.raises(TypeError):
        writer.write(float, 1.0)  # pyright: ignore[reportCallIssue, reportArgumentType]


def test_streamreader_invalid_type():
    reader = StreamReader(b"\x00\x01")
    with pytest.raises(TypeError):
        reader.read(float)  # pyright: ignore[reportCallIssue, reportArgumentType]


def test_streamreader_rest():
    reader = StreamReader(memoryview(b"\x00\x01restdata"))
    got = reader.read(ctypes.c_uint16)
    assert got == 1
    got = reader.read(rest)
    assert got == b"restdata"
    assert reader.eof()


def test_streamreader_ssh_key():
    data = b"openssh-key-v1\x00\x00\x00\x00\naes256-ctr\x00\x00\x00\x06bcrypt\x00\x00\x00\x18\x00\x00\x00\x10L\xe0\xa4\x1d\xf6t\xca\x1e'3\x1c\x9fDV\x0c3\x00\x00\x00\x18\x00\x00\x00\x01\x00\x00\x003\x00\x00\x00\x0bssh-ed25519\x00\x00\x00 n\r\xf09\x94fn)\xfdFB(\x15p\r\x95\xb3\xa8U\xba)\x1a@f\xb7;\x0b]\x9f\x0e\xbb\x8e\x00\x00\x00\x90E\xec\xc6-\x91kb\x07\x7fP#X\x08\xa6\xf8\xaa\xa0\x13\x1b\x16\xd2\x8b\xe2\"tI\xeb8\xe1e>u\xdc\x06(\xe1\x8ftO\x17\xe10fV)\xdd\xd0\xbcw\x98\xfaZ\xf1Q\xa1\xa3\xe7\xd2\xb1\xa4\xff\xd1\xc5\xf2a\xa2\x04C\xef\xf3\xe5\x9fV\xfe| o\x1f\x94\xe6\t\xc8\xa6'_K\t/\x1d\x92\xfbe\xd2\xc7|\x062\x07\\X\xfc\xc2X\xe8&\xc04<\xc8\x0b\xc9\xbd\x19Sk\xa6q\xd1\x1e\x1a:1)\xa7\xbc\x87\xb7<S\xe6\xe8j\x0cc/%\x80\xf0\xb7\xbd\x94\xf9\xfa\xdf"
    data = data[15:]  # Skip "openssh-key-v1\x00"
    reader = StreamReader(memoryview(data))
    assert reader.read_string() == "aes256-ctr"
    assert reader.read_string() == "bcrypt"
    assert reader.read_bytes() == b"\x00\x00\x00\x10L\xe0\xa4\x1d\xf6t\xca\x1e'3\x1c\x9fDV\x0c3\x00\x00\x00\x18"
    assert reader.read_uint32() == 1
    assert reader.read_bytes() == (
        b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00 n\r\xf09\x94fn)\xfdFB(\x15p\r\x95\xb3\xa8U\xba)\x1a@f\xb7;\x0b]\x9f\x0e\xbb\x8e"
    )
    reader2 = StreamReader(
        b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00 n\r\xf09\x94fn)\xfdFB(\x15p\r\x95\xb3\xa8U\xba)\x1a@f\xb7;\x0b]\x9f\x0e\xbb\x8e"
    )
    assert reader2.read_string() == "ssh-ed25519"
    assert reader2.read_bytes() == b"n\r\xf09\x94fn)\xfdFB(\x15p\r\x95\xb3\xa8U\xba)\x1a@f\xb7;\x0b]\x9f\x0e\xbb\x8e"

    assert reader.read_bytes() == (
        b'E\xec\xc6-\x91kb\x07\x7fP#X\x08\xa6\xf8\xaa\xa0\x13\x1b\x16\xd2\x8b\xe2"'
        + b"tI\xeb8\xe1e>u\xdc\x06(\xe1\x8ftO\x17\xe10fV)\xdd\xd0\xbcw\x98\xfaZ"
        + b"\xf1Q\xa1\xa3\xe7\xd2\xb1\xa4\xff\xd1\xc5\xf2a\xa2\x04C\xef\xf3\xe5\x9f"
        + b"V\xfe| o\x1f\x94\xe6\t\xc8\xa6'_K\t/\x1d\x92\xfbe\xd2\xc7|\x062\x07\\X"
        + b"\xfc\xc2X\xe8&\xc04<\xc8\x0b\xc9\xbd\x19Sk\xa6q\xd1\x1e\x1a:1)\xa7"
        + b"\xbc\x87\xb7<S\xe6\xe8j\x0cc/%\x80\xf0\xb7\xbd\x94\xf9\xfa\xdf"
    )

    assert reader.read_raw(None) == b""
