from typing import IO, Self, override

from attrs import frozen

from . import ansi, color
from .ansi import AnsiBase


@frozen(hash=True)
class Style(AnsiBase):
    """
    Appearance of text (e.g. bold, italic).

    Unlike colors, styles can be stacked.
    """

    _value: int

    @override
    def activate(self) -> set[str]:
        return {f"\x1b[{self._value}m"}

    @override
    def deactivate(self) -> set[str]:
        return {"\x1b[0m"}

    @override
    @classmethod
    def is_supported(cls, stream: IO | None = None) -> bool:
        """
        Checks whether this style will likely/unlikely be displayed correctly.
        """
        return color.ColorBasic.is_supported(stream)

    @override
    def __add__(self, other: AnsiBase) -> AnsiBase:
        return ansi.empty() + self + other

    @classmethod
    def bold(cls) -> Self:
        return cls(1)

    @classmethod
    def dimmed(cls) -> Self:
        return cls(2)

    @classmethod
    def italic(cls) -> Self:
        return cls(3)

    @classmethod
    def underline(cls) -> Self:
        return cls(4)

    @classmethod
    def blink(cls) -> Self:
        return cls(5)

    @classmethod
    def hidden(cls) -> Self:
        return cls(8)

    @classmethod
    def strike(cls) -> Self:
        return cls(9)
