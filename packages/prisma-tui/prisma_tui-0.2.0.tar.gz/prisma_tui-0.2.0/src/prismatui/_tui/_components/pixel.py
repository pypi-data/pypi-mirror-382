import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class Pixel:
    """A Pixel objects is a container for a single character with an associated attribute."""
    def __init__(self, char = pr.BLANK_CHAR, attr = pr.BLANK_ATTR):
        self._char = char
        self._attr = attr


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def overwrite(self, other: "Pixel") -> "Pixel":
        """The other pixel replaces this pixel unconditionally."""
        return other

    # --------------------------------------------------------------------------
    def overlay(self, other: "Pixel") -> "Pixel":
        """If the other pixel is not blank, it replaces this pixel.
        Blank pixels are therefore "transparent" and don't affect the pixels under them."""
        return self if other._is_blank() else other

    # --------------------------------------------------------------------------
    def merge_attr(self, other: "Pixel") -> "Pixel":
        """The other pixel's attribute is merged with this pixel's attribute,
        by applying a bitwise OR operation."""
        self._attr |= other._attr
        return self


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _is_blank(self) -> bool:
        """A pixel is considered to be "blank" when BOTH its character and attribute
        are set to their blank values."""
        return (self._char == pr.BLANK_CHAR) and (self._attr == pr.BLANK_ATTR)


# //////////////////////////////////////////////////////////////////////////////
