"""Collection of common ANSI styles."""

__all__ = [
    "BLACK",
    "MAROON",
    "GREEN",
    "OLIVE",
    "NAVY",
    "PURPLE",
    "TEAL",
    "SILVER",
    "GRAY",
    "GREY",
    "RED",
    "GREEN",
    "YELLOW",
    "BLUE",
    "FUCHSIA",
    "AQUA",
    "WHITE",
    "DEFAULT",
    "BOLD",
    "DIMMED",
    "ITALIC",
    "UNDERLINE",
    "BLINK",
    "HIDDEN",
    "STRIKE",
]

from .color import ColorBasic, ColorSystem
from .style import Style

BLACK = ColorBasic(0, None)
MAROON = ColorBasic(1, None)
GREEN = ColorBasic(2, None)
OLIVE = ColorBasic(3, None)
NAVY = ColorBasic(4, None)
PURPLE = ColorBasic(5, None)
TEAL = ColorBasic(6, None)
SILVER = ColorBasic(7, None)

GRAY = GREY = ColorSystem(0, None)
RED = ColorSystem(1, None)
LIME = ColorSystem(2, None)
YELLOW = ColorSystem(3, None)
BLUE = ColorSystem(4, None)
FUCHSIA = ColorSystem(5, None)
AQUA = ColorSystem(6, None)
WHITE = ColorSystem(7, None)

DEFAULT = ColorBasic(9, None)

BOLD = Style.bold()
DIMMED = Style.dimmed()
ITALIC = Style.italic()
UNDERLINE = Style.underline()
BLINK = Style.blink()
HIDDEN = Style.hidden()
STRIKE = Style.strike()
