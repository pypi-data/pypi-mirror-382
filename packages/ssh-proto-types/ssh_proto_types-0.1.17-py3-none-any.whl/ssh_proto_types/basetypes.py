import ctypes
import enum
import typing


class Notset(enum.Enum):
    Notset = enum.auto()


NOTSET = Notset.Notset


class rest:
    pass


class nested:
    pass


class exclude:
    pass


R_TYPES = (rest,)
C_TYPES = (ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint64)
P_TYPES = (int, bytes, str)
UNDERLAYING_TYPES = (*C_TYPES, *P_TYPES, *R_TYPES)

R_TYPES_T = rest
C_TYPES_T = ctypes.c_uint8 | ctypes.c_uint16 | ctypes.c_uint32 | ctypes.c_uint64
P_TYPES_T = bytes | str | int
UNDERLAYING_TYPES_T = C_TYPES_T | P_TYPES_T | R_TYPES_T


def is_c_types_t(annotation: type) -> typing.TypeGuard[type[C_TYPES_T]]:
    return annotation in C_TYPES


def is_p_types_t(annotation: type) -> typing.TypeGuard[type[P_TYPES_T]]:
    return annotation in P_TYPES


def is_r_types_t(annotation: type) -> typing.TypeGuard[type[R_TYPES_T]]:
    return annotation in R_TYPES
