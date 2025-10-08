"""Classes and utilities related to ANSI colors specifically."""

import copy
import os
import sys
from abc import ABC, abstractmethod
from math import sqrt
from typing import IO, Self, override

from attrs import define, frozen

from . import _color_space
from .ansi import AnsiBase
from .palettes import web as web_color

type RGB = tuple[int, int, int] | int | str


@define(hash=True, eq=True, slots=True)
class _RGBTuple:
    r: int
    g: int
    b: int

    @classmethod
    def from_string(cls, string: str):
        string = string.removeprefix("#")
        if len(string) == 3:
            try:
                r = int(string[0:1] * 2, 16)
                g = int(string[1:2] * 2, 16)
                b = int(string[2:3] * 2, 16)
            except ValueError:
                raise ValueError(f"invalid hex digit in {string!r}")
        elif len(string) == 6:
            try:
                r = int(string[0:2], 16)
                g = int(string[2:4], 16)
                b = int(string[4:6], 16)
            except ValueError:
                raise ValueError(f"invalid hex digit in {string!r}")
        else:
            raise ValueError(f"expected 3 or 6 hex digits; got {len(string)}")
        return cls(r, g, b)

    @classmethod
    def from_int(cls, code: int):
        r = (code >> 16) & 0xFF
        g = (code >> 8) & 0xFF
        b = code & 0xFF
        return cls(r, g, b)


enforced_color_class: type["Color"] | None = None


def _closest_rgb[Key](target: _RGBTuple, palette: _color_space.ColorSpace[Key]) -> Key:
    (_distance, (_rgb, key)) = min(
        (
            (
                sqrt(
                    (target.r - color[0][0]) ** 2
                    + (target.g - color[0][1]) ** 2
                    + (target.b - color[0][2]) ** 2
                ),
                color,
            )
            for color in palette
        ),
        key=lambda x: x[0],
    )
    return key


@frozen(hash=True)
class Color[T](AnsiBase, ABC):
    """
    The base class for colors.

    A color consists of one of or both a foreground and background color.
    """

    _value_fg: T | None
    _value_bg: T | None

    @override
    @classmethod
    def is_supported(cls, stream: IO | None = None) -> bool:
        """
        Checks whether this color will likely/unlikely be displayed correctly.
        """
        possible_stream: IO = stream or sys.stdout

        # Check if stream is a terminal
        if not possible_stream.isatty():
            return False

        supported_colorspace = _supported_colorspace(possible_stream)
        return supported_colorspace.supersedes(cls)

    @classmethod
    @abstractmethod
    def supersedes(cls, other: type["Color"]) -> bool:
        """
        Returns `True` when this color set is a subset or the same set of
        `other`.
        """

    @property
    def has_fg(self) -> bool:
        """
        Returns `True` when this color has a foreground color.
        """
        return self._value_fg is not None

    @property
    def has_bg(self) -> bool:
        """
        Returns `True` when this color has a background color.
        """
        return self._value_bg is not None

    def fg(self) -> Self:
        """
        Uses the color as a foreground (text) color.

        This will raise {py:class}`ValueError` if the color has both a
        foreground and background color set.
        """
        if self.has_fg and self.has_bg:
            raise ValueError("both foreground and background color are set")
        if self.has_bg:
            return copy.replace(self, value_fg=self._value_bg, value_bg=None)  # type: ignore # https://github.com/python/mypy/issues/18304
        return self

    def bg(self) -> Self:
        """
        Uses the color as a background color.

        This will raise {py:class}`ValueError` if the color has both a
        foreground and background color set.
        """
        if self.has_fg and self.has_bg:
            raise ValueError("both foreground and background color are set")
        if self._value_fg is not None:
            return copy.replace(self, value_fg=None, value_bg=self._value_fg)  # type: ignore # https://github.com/python/mypy/issues/18304
        return self

    def on(self, background_color: "Color") -> Self:
        """
        Sets this color as a foreground color and adds `background_color` as
        the background color.

        This will raise {py:class}`ValueError` if this or the other color has
        both a foreground and background color set.
        """
        if self.has_fg and self.has_bg:
            raise ValueError("both foreground and background color are set")
        return copy.replace(self, value_bg=background_color.bg()._value_bg)  # type: ignore # https://github.com/python/mypy/issues/18304

    @classmethod
    @abstractmethod
    def _from_rgb(cls, rgb: _RGBTuple) -> Self: ...

    @classmethod
    def from_rgb(cls, rgb: RGB) -> Self:
        """
        Constructs the by this color set nearest representable color from an RGB
        value.
        """
        if isinstance(rgb, int):
            color = _RGBTuple.from_int(rgb)
        elif isinstance(rgb, str):
            color = _RGBTuple.from_string(rgb)
        else:
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]
            color = _RGBTuple(r, g, b)
        return cls._from_rgb(color)

    @classmethod
    def from_name(cls, name: str) -> Self:
        return cls.from_rgb(web_color[name.lower()])

    @override
    def __add__(self, other: AnsiBase) -> AnsiBase:
        if isinstance(other, Color):
            if (self.has_fg and self.has_bg) or (other.has_fg and self.has_bg):
                raise ValueError("both foreground and background color are set")
            if self.has_fg:
                return self.on(other)
            return other.on(self)
        return super().__add__(other)


@frozen(hash=True)
class ColorBasic(Color[int]):
    """
    The basic color set (8 different colors).

    Note that the appearance may differ depending on the user's preference.
    """

    @override
    def activate(self) -> set[str]:
        res = set()
        if (value := self._value_fg) is not None:
            res.add(f"\x1b[{value + 30}m")
        if (value := self._value_bg) is not None:
            res.add(f"\x1b[{value + 40}m")
        return res

    @override
    def deactivate(self) -> set[str]:
        return {"\x1b[0m"}

    @override
    @classmethod
    def supersedes(cls, other: type[Color]) -> bool:
        if other == Colorless:
            return True
        if other == ColorBasic:
            return True
        if other == ColorSystem:
            return False
        if other == ColorExtended:
            return False
        if other == ColorRGB:
            return False
        raise ValueError(f"unknown class {other!r}")

    @override
    @classmethod
    def _from_rgb(cls, rgb: _RGBTuple) -> Self:
        return cls(_closest_rgb(rgb, _color_space.basic), None)


@frozen
class ColorSystem(Color[int]):
    """
    The Xterm system color set (8 different colors plus bright variants making
    up a total of 16 colors).

    Note that the appearance may differ depending on the user's preference.
    """

    @override
    def activate(self) -> set[str]:
        res = set()
        if (value := self._value_fg) is not None:
            res.add(f"\x1b[{value + 90}m")
        if (value := self._value_bg) is not None:
            res.add(f"\x1b[{value + 100}m")
        return res

    @override
    def deactivate(self) -> set[str]:
        return {"\x1b[0m"}

    @override
    @classmethod
    def supersedes(cls, other: type[Color]) -> bool:
        if other == Colorless:
            return True
        if other == ColorBasic:
            return True
        if other == ColorSystem:
            return True
        if other == ColorExtended:
            return False
        if other == ColorRGB:
            return False
        raise ValueError(f"unknown class {other!r}")

    @override
    @classmethod
    def _from_rgb(cls, rgb: _RGBTuple) -> Self:
        return cls(_closest_rgb(rgb, _color_space.system), None)


@frozen(hash=True)
class ColorExtended(Color[int]):
    """
    The extended color set (256 different colors).
    """

    @override
    @classmethod
    def supersedes(cls, other: type[Color]) -> bool:
        if other == Colorless:
            return True
        if other == ColorBasic:
            return True
        if other == ColorSystem:
            return True
        if other == ColorExtended:
            return True
        if other == ColorRGB:
            return False
        raise RuntimeError(f"unknown class {other!r}")

    @override
    def activate(self) -> set[str]:
        res = set()
        if (value := self._value_fg) is not None:
            res.add(f"\x1b[38;5;{self._value_fg}m")
        if (value := self._value_bg) is not None:
            res.add(f"\x1b[48;5;{self._value_bg}m")
        return res

    @override
    def deactivate(self) -> set[str]:
        return {"\x1b[0m"}

    @override
    @classmethod
    def _from_rgb(cls, rgb: _RGBTuple) -> Self:
        return cls(_closest_rgb(rgb, _color_space.extended), None)


@frozen(hash=True)
class ColorRGB(Color[_RGBTuple]):
    """
    The RGB color set.
    """

    @override
    @classmethod
    def supersedes(cls, other: type[Color]) -> bool:
        if other == Colorless:
            return True
        if other == ColorBasic:
            return True
        if other == ColorSystem:
            return True
        if other == ColorExtended:
            return True
        if other == ColorRGB:
            return True
        raise ValueError(f"unknown class {other!r}")

    @override
    def activate(self) -> set[str]:
        res = set()
        if (value := self._value_fg) is not None:
            res.add(f"\x1b[38;2;{value.r};{value.g};{value.b}m")
        if (value := self._value_bg) is not None:
            res.add(f"\x1b[48;2;{value.r};{value.g};{value.b}m")
        return res

    @override
    def deactivate(self) -> set[str]:
        return {"\x1b[0m"}

    @override
    @classmethod
    def _from_rgb(cls, rgb: _RGBTuple) -> Self:
        return cls(rgb, None)


@frozen(hash=True)
class Colorless(Color):
    """
    The empty color set (no colors at all).
    """

    @override
    @classmethod
    def supersedes(cls, other: type[Color]) -> bool:
        if other == Colorless:
            return True
        if other == ColorBasic:
            return False
        if other == ColorSystem:
            return False
        if other == ColorExtended:
            return False
        if other == ColorRGB:
            return False
        raise ValueError(f"unknown class {other!r}")


def _supported_colorspace(stream: IO) -> type[Color]:
    if enforced_color_class is not None:
        return enforced_color_class
    if (value := os.getenv("ADORABLE_COLOR")) is not None:
        if value == "Colorless":
            return Colorless
        if value == "ColorBasic":
            return ColorBasic
        if value == "ColorSystem":
            return ColorSystem
        if value == "ColorExtended":
            return ColorExtended
        if value == "ColorRGB":
            return ColorRGB
    if os.getenv("NO_COLOR"):
        return Colorless
    if os.getenv("FORCE_COLOR") in {"false", "0"}:
        return Colorless
    if os.getenv("FORCE_COLOR") in {"true", "1"}:
        return ColorBasic
    if os.getenv("FORCE_COLOR") == "2":
        return ColorExtended
    if (force_color := os.getenv("FORCE_COLOR")) is not None:
        try:
            integer = int(force_color)
        except ValueError:
            integer = 0
        if integer >= 3:
            return ColorRGB
    if (clicolor_force := os.getenv("CLICOLOR_FORCE")) is not None:
        if clicolor_force == "0":
            return Colorless
        else:
            return ColorBasic
    if (
        os.getenv("COLORTERM") in {"truecolor", "24bit"}
        or os.getenv("TERM") in {"direct", "truecolor"}
        or os.getenv("TERM_PROGRAM") == "iTerm.app"
    ):
        return ColorRGB
    if (
        os.getenv("TERM") in {"256", "256color"}
        or os.getenv("TERM_PROGRAM") == "Apple_Terminal"
    ):
        return ColorExtended
    if os.getenv("COLORTERM") is not None or os.getenv("TERM") != "cygwin":
        return ColorBasic
    return Colorless


def from_rgb(rgb: RGB) -> Color:
    # TODO: links in doc don't work yet
    """
    Initializes a color from an RGB value.

    This function guesses the largest color space that is supported. If you
    want to manually choose the color space, use
    {py:meth}`adorable.color.ColorBasic.from_rgb`,
    {py:meth}`adorable.color.ColorExtended.from_rgb` or
    {py:meth}`adorable.color.ColorRGB.from_rgb`.

    # Examples

    ```python3
    from adorable import color

    red = color.from_rgb((255, 0, 0))
    print(f"This is {red:important}!")

    green = color.from_rgb(0x00FF00)
    print(f"This is {green:good}!")
    ```
    """
    return _supported_colorspace(sys.stdout).from_rgb(rgb)
