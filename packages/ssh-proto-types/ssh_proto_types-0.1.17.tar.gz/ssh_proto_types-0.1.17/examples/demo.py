import dataclasses
import inspect
from typing import ClassVar


class A:
    pass


class B(A):
    pass


class C(A):
    pass


@dataclasses.dataclass(frozen=True)
class Demo:
    __child_types: ClassVar[dict[str, str]] = {}
    a: A

    def __init_subclass__(cls, typ: str) -> None:
        print(inspect.get_annotations(cls))  # Force evaluation of annotations
        cls.__child_types[typ] = cls.__name__

    def show_child_types(self):
        print(self.__child_types)


@dataclasses.dataclass(frozen=True)
class Demo2(Demo, typ="B"):
    a: B


@dataclasses.dataclass(frozen=True)
class Demo3(Demo, typ="C"):
    a: C


d2 = Demo2(a=B())
print(d2)
d2.show_child_types()
