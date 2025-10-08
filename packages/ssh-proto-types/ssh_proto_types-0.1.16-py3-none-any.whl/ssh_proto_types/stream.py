import contextlib
import ctypes
import dataclasses
import typing

from ssh_proto_types.basetypes import UNDERLAYING_TYPES_T, rest


@dataclasses.dataclass
class StreamWriter:
    data: bytearray = dataclasses.field(default_factory=bytearray)
    offset: int = 0

    @classmethod
    @contextlib.contextmanager
    def of(cls, data: "bytearray | StreamWriter | None"):
        if not isinstance(data, StreamWriter):
            data = data if data is not None else bytearray()
            yield cls(data)
            return

        with data.substream() as stream:
            yield stream

    @contextlib.contextmanager
    def substream(self):
        yield StreamWriter(self.data, offset=len(self))

    def write_uint8(self, value: int) -> None:
        self.data.append(value & 0xFF)

    def write_uint16(self, value: int) -> None:
        self.data.extend(value.to_bytes(2, "big"))

    def write_uint32(self, value: int) -> None:
        self.data.extend(value.to_bytes(4, "big"))

    def write_uint64(self, value: int) -> None:
        self.data.extend(value.to_bytes(8, "big"))

    def write_bytes(self, value: bytes) -> None:
        self.write_uint32(len(value))
        self.data.extend(value)

    def write_mpint(self, value: int) -> None:
        if value == 0:
            self.write_bytes(b"")
            return
        byte_length = value.bit_length() // 8 + 1
        byte_data = value.to_bytes(byte_length, "big", signed=True)
        self.write_bytes(byte_data)

    def write_string(self, value: str) -> None:
        b = value.encode("utf-8")
        self.write_bytes(b)

    def write_raw(self, value: bytes) -> None:
        self.data.extend(value)

    @typing.overload
    def write(
        self, value: int, ctype: type[int | ctypes.c_uint8 | ctypes.c_uint16 | ctypes.c_uint32 | ctypes.c_uint64]
    ) -> None: ...

    @typing.overload
    def write(self, value: bytes, ctype: type[rest]) -> None: ...

    @typing.overload
    def write(self, value: int, ctype: type[int] | None = ...) -> None: ...

    @typing.overload
    def write(self, value: bytes, ctype: type[bytes] | None = ...) -> None: ...

    @typing.overload
    def write(self, value: str, ctype: type[str] | None = ...) -> None: ...

    def write(self, value: int | bytes | str, ctype: type[UNDERLAYING_TYPES_T] | None = None) -> None:
        if ctype is None:
            if isinstance(value, int):
                ctype = int
            elif isinstance(value, bytes):
                ctype = bytes
            else:
                ctype = str

        match ctype:
            case c if c is ctypes.c_uint8:
                self.write_uint8(value)  # type: ignore[arg-type]
            case c if c is ctypes.c_uint16:
                self.write_uint16(value)  # type: ignore[arg-type]
            case c if c is ctypes.c_uint32:
                self.write_uint32(value)  # type: ignore[arg-type]
            case c if c is ctypes.c_uint64:
                self.write_uint64(value)  # type: ignore[arg-type]
            case c if c is int:
                self.write_mpint(value)  # type: ignore[arg-type]
            case c if c is bytes:
                self.write_bytes(value)  # type: ignore[arg-type]
            case c if c is str:
                self.write_string(value)  # type: ignore[arg-type]
            case c if c is rest:
                self.write_raw(value)  # type: ignore[arg-type]
            case _:
                raise TypeError(f"Unsupported type {ctype} for writing")

    def get_bytes(self) -> bytes:
        return bytes(self.data[self.offset :])

    def __len__(self) -> int:
        return len(self.data) - self.offset


@dataclasses.dataclass
class StreamReader:
    data: dataclasses.InitVar["bytes | memoryview[bytes]"]
    _data: "memoryview[bytes]" = dataclasses.field(init=False)
    _idx: int = dataclasses.field(default=0, init=False)
    offset: int = 0

    def __post_init__(self, data: "bytes | memoryview[bytes]") -> None:
        self._data = memoryview(data).cast("c") if isinstance(data, bytes) else data

    @classmethod
    @contextlib.contextmanager
    def of(cls, data: "bytes | memoryview[bytes] | StreamReader"):
        if isinstance(data, StreamReader):
            with data.substream() as stream:
                yield stream
        else:
            yield cls(data)

    @contextlib.contextmanager
    def substream(self):
        stream = StreamReader(self._data, offset=self.idx)
        try:
            yield stream
        finally:
            self.idx = stream.idx

    @property
    def idx(self) -> int:
        return self._idx + self.offset

    @idx.setter
    def idx(self, value: int) -> None:
        self._idx = value - self.offset

    def _get_slice(self, length: int) -> bytes:
        if self.idx + length > len(self._data):
            raise EOFError("Not enough data to read")
        value = self._data[self.idx : self.idx + length]
        self.idx += length
        return bytes(value)

    def read_uint8(self) -> int:
        data = self._get_slice(1)
        return data[0]

    def read_uint16(self) -> int:
        data = self._get_slice(2)
        return int.from_bytes(data, "big")

    def read_uint32(self) -> int:
        data = self._get_slice(4)
        return int.from_bytes(data, "big")

    def read_uint64(self) -> int:
        data = self._get_slice(8)
        return int.from_bytes(data, "big")

    def read_bytes(self) -> bytes:
        length = self.read_uint32()
        data = self._get_slice(length)
        return data

    def read_mpint(self) -> int:
        data = self.read_bytes()
        return int.from_bytes(data, "big", signed=True)

    def read_string(self) -> str:
        data = self.read_bytes()
        return data.decode("utf-8")

    def read_raw(self, length: int | None) -> bytes:
        if length is None:
            length = len(self._data) - self.idx
        data = self._get_slice(length)
        return data

    @typing.overload
    def read(self, ctype: type[ctypes.c_uint8 | ctypes.c_uint16 | ctypes.c_uint32 | ctypes.c_uint64 | int]) -> int: ...

    @typing.overload
    def read(self, ctype: type[rest]) -> bytes: ...

    @typing.overload
    def read(self, ctype: type[bytes]) -> bytes: ...

    @typing.overload
    def read(self, ctype: type[str]) -> str: ...

    def read(self, ctype: type[UNDERLAYING_TYPES_T]) -> int | bytes | str:
        match ctype:
            case c if c is ctypes.c_uint8:
                return self.read_uint8()
            case c if c is ctypes.c_uint16:
                return self.read_uint16()
            case c if c is ctypes.c_uint32:
                return self.read_uint32()
            case c if c is ctypes.c_uint64:
                return self.read_uint64()
            case c if c is int:
                return self.read_mpint()
            case c if c is bytes:
                return self.read_bytes()
            case c if c is str:
                return self.read_string()
            case c if c is rest:
                return self.read_raw(None)
            case _:
                raise TypeError(f"Unsupported type {ctype} for reading")

    def eof(self) -> bool:
        return self.idx >= len(self._data)

    def __len__(self) -> int:
        return len(self._data) - self.idx

    def amount_read(self) -> int:
        return self._idx
