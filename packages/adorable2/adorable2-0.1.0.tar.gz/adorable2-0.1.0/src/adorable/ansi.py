"""Classes and utilities related to ANSI escape sequences."""

import os
import sys
from abc import ABC, abstractmethod
from typing import IO, Self, override

from attrs import define, field


@define
class AnsiBase(ABC):
    def __format__(self, format_spec: str) -> str:
        """Applies the style on the format specifier."""
        return self(format_spec)

    def __call__(self, text: str) -> str:
        """Applies the style on the argument."""
        return f"{self.begin}{text}{self.end}"

    @abstractmethod
    def activate(self) -> set[str]:
        """Returns a set of ANSI escape sequences that activate this."""

    @abstractmethod
    def deactivate(self) -> set[str]:
        """Returns a set of ANSI escape sequences that deactivate this."""

    def __add__(self, other: "AnsiBase") -> "AnsiBase":
        """Combines two ANSI instances."""
        return empty() + self + other

    @property
    def begin(self) -> str:
        """Returns the ANSI escape sequence(s) needed to enable this."""
        return "".join(self.activate())

    @property
    def end(self) -> str:
        """Returns the ANSI escape sequence(s) needed to disable this."""
        return "".join(self.deactivate())

    @classmethod
    def is_supported(cls, stream: IO | None = None) -> bool:
        """
        Returns `True` when this ANSI sequence is supported.

        # References

        - <https://no-color.org/>
        - <https://force-color.org/>
        """
        return False


@define
class Ansi(AnsiBase):
    """
    A wrapper around one or usually multiple instances of {py:class}`AnsiBase`.
    """
    _children: list[AnsiBase] = field(init=False, factory=list)

    @override
    def activate(self) -> set[str]:
        res = set()
        for child in self._children:
            res.update(child.activate())
        return res

    @override
    def deactivate(self) -> set[str]:
        res = set()
        for child in self._children:
            res.update(child.deactivate())
        return res

    @override
    def __add__(self, other: AnsiBase) -> AnsiBase:
        self._children.append(other)
        return self


def empty() -> Ansi:
    """
    Utility function to return an empty dummy ansi object.
    """
    return Ansi()
