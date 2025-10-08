import json

import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class Palette:
    """Class to manage colors and palette files."""
    def __init__(self):
        self.palette: dict = {"colors": [], "pairs":  []}


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_colors(self, colors) -> None:
        """Update the color palette with a list of (r,g,b) colors.
        RBG values should be in the range 0-1000."""
        self.palette["colors"] = [[int(c) for c in color] for color in colors]

    # --------------------------------------------------------------------------
    def set_pairs(self, pairs) -> None:
        """Update the color pairs with a list of (fg, bg) pairs."""
        self.palette["pairs"] = [[int(p) for p in pair] for pair in pairs]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def save_pal(self, path_pal: str) -> None:
        """Save the current palette to a JSON file."""
        with open(path_pal, 'w') as file:
            json.dump(self.palette, file)

    # --------------------------------------------------------------------------
    def load_pal(self, path_pal: str) -> None:
        """Load a palette from a JSON file."""
        with open(path_pal, 'r') as file:
            self.palette = json.load(file)

        colors = self.palette["colors"]
        pairs  = self.palette["pairs"]

        assert len(colors) <= pr.MAX_PALETTE_COLORS, \
            f"Palette has {len(colors)} colors, max is {pr.MAX_PALETTE_COLORS}."

        assert len(pairs) <= pr.MAX_PALETTE_PAIRS, \
            f"Palette has {len(pairs)} pairs, max is {pr.MAX_PALETTE_PAIRS}."

        if not pr._CURRENT_BACKEND.supports_color(): return

        for i,color in enumerate(colors):
            pr._CURRENT_BACKEND.init_color(i, *color)

        for i,(fg,bg) in enumerate(pairs):
            pr._CURRENT_BACKEND.init_pair(i, fg, bg)


# //////////////////////////////////////////////////////////////////////////////
