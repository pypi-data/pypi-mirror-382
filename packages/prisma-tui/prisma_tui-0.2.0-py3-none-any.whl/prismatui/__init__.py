from ._tui._backend.backend import Backend
from ._tui._backend.backend_curses import BackendCurses
from ._tui._backend.constants import *

# --------------------------------------------------------------------------
_CURRENT_BACKEND: Backend = BackendCurses()
BLANK_CHAR = ' '
BLANK_ATTR = A_NORMAL

MAX_PALETTE_COLORS = 256
MAX_PALETTE_PAIRS  = 256
ALPHA_THRESHOLD = 128

# --------------------------------------------------------------------------
from ._tui._misc.blend_mode import BlendMode
from ._tui._misc.palette import Palette
from ._tui._misc.parser_pri import load_layer, save_layer

from ._utils.debug_logger import DebugLogger
from ._utils.mosaic_parser import mosaic_parser

from ._tui._components.pixel import Pixel
from ._tui._components.layer import Layer
from ._tui._components.section import Section
from ._tui._components.terminal import Terminal

# --------------------------------------------------------------------------
def set_backend(backend: str|Backend) -> None:
    global _CURRENT_BACKEND

    if isinstance(backend, Backend):
        _CURRENT_BACKEND = backend

    elif isinstance(backend, str):
        match backend:
            case "curses": _CURRENT_BACKEND = BackendCurses()
            case _: raise ValueError(f"Unknown backend: {backend}")


# --------------------------------------------------------------------------
def set_nodelay(boolean: bool) -> None:
    """Set the nodelay mode for the backend. When enabled, get_key() will not block the terminal."""
    _CURRENT_BACKEND.set_nodelay(boolean)

def sleep(ms: int) -> None:
    """Sleep for a given number of milliseconds."""
    _CURRENT_BACKEND.sleep(ms)

def write_text(y: int, x: int, chars: str, attr: int = BLANK_ATTR) -> None:
    """Write text to the terminal at a specific position."""
    _CURRENT_BACKEND.write_text(y, x, chars, attr)

def get_size(update: bool = False) -> tuple[int, int]:
    """Get the size of the terminal, as (COLS, LINES).
    If update is True, a backend method will be called to update the current COLS and LINES values."""
    return _CURRENT_BACKEND.get_size(update)

def supports_color() -> bool:
    """Check if the backend supports color."""
    return _CURRENT_BACKEND.supports_color()

def init_color(i: int, r: int, g: int, b: int) -> None:
    """Initialize a color with index 'i' and values 'r','g','b' to be used in color pairs by the terminal."""
    _CURRENT_BACKEND.init_color(i, r, g, b)

def init_pair(i: int, fg: int, bg: int) -> None:
    """Initialize a color pair (fg,bg) which can be accessed with index 'i'."""
    _CURRENT_BACKEND.init_pair(i, fg, bg)

def get_color_pair(i: int) -> int:
    """Retrieve the color pair for a given index."""
    return _CURRENT_BACKEND.get_color_pair(i)


# --------------------------------------------------------------------------
