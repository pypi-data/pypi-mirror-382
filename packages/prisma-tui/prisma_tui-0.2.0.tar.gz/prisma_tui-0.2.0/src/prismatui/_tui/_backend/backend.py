from abc import ABC, abstractmethod

# //////////////////////////////////////////////////////////////////////////////
class Backend(ABC):
    """Abstract base class for terminal backends.
    This class defines the interface for terminal operations, such as writing text,
    handling colors, and managing terminal size and key input.
    Subclasses must implement these methods to provide specific terminal functionality."""

    @abstractmethod
    def set_nodelay(self, boolean: bool) -> None:
        """Set the nodelay mode for the backend. When enabled, get_key() will not block the terminal."""
        raise NotImplementedError

    @abstractmethod
    def sleep(self, ms: int) -> None:
        """Sleep for a given number of milliseconds."""
        raise NotImplementedError

    @abstractmethod
    def write_text(self, y: int, x: int, chars: str, attr: int = 0) -> None:
        """Write text to the terminal at a specific position."""
        raise NotImplementedError

    @abstractmethod
    def get_size(self, update = False) -> tuple[int,int]:
        """Get the size of the terminal, as (COLS, LINES).
        If update is True, a backend method will be called to update the current COLS and LINES values."""
        raise NotImplementedError

    @abstractmethod
    def supports_color(self) -> bool:
        """Check if the backend supports color."""
        raise NotImplementedError

    @abstractmethod
    def init_color(self, i: int, r: int, g: int, b: int) -> None:
        """Initialize a color with index 'i' and values 'r','g','b' to be used in color pairs by the terminal."""
        raise NotImplementedError

    @abstractmethod
    def init_pair(self, i: int, fg: int, bg: int) -> None:
        """Initialize a color pair (fg,bg) which can be accessed with index 'i'."""
        raise NotImplementedError

    @abstractmethod
    def get_color_pair(self, i: int) -> int:
        """Retrieve the color pair for a given index."""
        raise NotImplementedError

    @abstractmethod
    def _start(self) -> None:
        """Initialize the backend, setting up the terminal."""
        raise NotImplementedError

    @abstractmethod
    def _end(self) -> None:
        """Clean up the backend, restoring the terminal to its original state."""
        raise NotImplementedError

    @abstractmethod
    def _refresh(self) -> None:
        """Refresh the terminal display."""
        raise NotImplementedError

    @abstractmethod
    def _get_key(self) -> int:
        """Get a key press from the terminal."""
        raise NotImplementedError

    @abstractmethod
    def _resize(self, h: int, w: int) -> None:
        """Resize the terminal to the given height and width."""
        raise NotImplementedError


# //////////////////////////////////////////////////////////////////////////////
