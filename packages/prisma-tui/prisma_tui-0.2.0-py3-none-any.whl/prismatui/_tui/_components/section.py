from typing import Generator

import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class Section:
    """A Section is a container for layers and child sections.
    It can be used to create a hierarchical structure of sections, each with its own layers.
    Each section has a size and position relative to its parent section
    (or the terminal, in case of the root section)."""
    def __init__(self):
        self._parent: "Section" = None

        self.h: int; self.w: int
        self.y: int; self.x: int
        self.hrel: int|float = 1.0
        self.wrel: int|float = 1.0
        self.yrel: int|float = 0
        self.xrel: int|float = 0
        self._update_dimensions()

        self._children: list["Section"] = []
        self._layers = [pr.Layer(self.h, self.w)]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_parent(self, parent: "Section") -> None:
        """Set the parent section of this section."""
        self._parent = parent
        parent._children.append(self)
        self._update_dimensions()

    # --------------------------------------------------------------------------
    def create_child(self,
        hrel: int|float, wrel: int|float,
        yrel: int|float, xrel: int|float
    ) -> "Section":
        """Create a child section with the specified relative dimensions and position."""
        child = Section()
        child.hrel = hrel
        child.wrel = wrel
        child.yrel = yrel
        child.xrel = xrel
        child.set_parent(self)
        return child

    # --------------------------------------------------------------------------
    def create_layer(self) -> "pr.Layer":
        """Create a new layer in this section."""
        layer = pr.Layer(self.h, self.w)
        self._layers.append(layer)
        return layer

    # --------------------------------------------------------------------------
    def create_mosaic(self, layout: str, divider = '\n') -> dict:
        """Create a mosaic of sections based on the provided 'mosaic' layout
        string, where each character represents a section. Takes inspiration
        from matplotlib's `subplot_mosaic` function."""
        section_dict = {}
        for char, hwyx in pr.mosaic_parser(layout, divider).items():
            section = self.create_child(*hwyx)
            section_dict[char] = section
        return section_dict


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def get_size(self) -> tuple[int, int]:
        """Get the size of this section."""
        return self.h, self.w

    # --------------------------------------------------------------------------
    def get_position(self) -> tuple[int, int]:
        """Get the position of this section relative to its parent."""
        return self.y, self.x

    # --------------------------------------------------------------------------
    def get_bottom_layer(self) -> "pr.Layer":
        """Get the bottom layer of this section."""
        return self._layers[0]

    # --------------------------------------------------------------------------
    def get_top_layer(self) -> "pr.Layer":
        """Get the top layer of this section."""
        return self._layers[-1]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def iter_children(self) -> Generator["Section", None, None]:
        """Iterate over the child sections of this section."""
        return iter(self._children)

    # --------------------------------------------------------------------------
    def iter_layers(self) -> Generator["pr.Layer", None, None]:
        """Iterate over the layers of this section."""
        return iter(self._layers)

    # --------------------------------------------------------------------------
    def clear(self) -> None:
        """Clear all layers and child sections in this section."""
        for layer in self.iter_layers():
            layer.clear()

        for child in self.iter_children():
            child.clear()

    # --------------------------------------------------------------------------
    def aggregate_layers(self, agg_layer: "pr.Layer") -> None:
        """Aggregate all layers and child sections into the provided aggregate layer."""
        for layer in self.iter_layers():
            agg_layer.draw_layer(self.y, self.x, layer)

        for child in self.iter_children():
            child.aggregate_layers(agg_layer)

    # --------------------------------------------------------------------------
    def update_size(self) -> None:
        """Update the size of this section and its layers, as well as of children sections, based on the relative dimensions."""
        self._update_dimensions()

        for layer in self.iter_layers():
            layer.set_size(self.h, self.w)

        for child in self.iter_children():
            child.update_size()


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def draw_layer(self, y: int | str, x: int | str, layer: "pr.Layer") -> None:
        """Draw another layer onto the top layer of this section, at the specified coordinates."""
        self.get_top_layer().draw_layer(y, x, layer)


    # --------------------------------------------------------------------------
    def draw_matrix(self, y: int | str, x: int | str, chars: list[str], attrs: list[list[int]], blend = pr.BlendMode.OVERLAY) -> None:
        self.get_top_layer().draw_matrix(y, x, chars, attrs, blend)

    # --------------------------------------------------------------------------
    def draw_text(self,
        y: int | str, x: int | str, string,
        attr: int = None, blend = pr.BlendMode.OVERLAY,
        cut: dict[str, str] = {}
    ) -> None:
        """Draw a string on the top layer of this section, at the specified coordinates with optional attributes and blending mode."""
        self.get_top_layer().draw_text(y, x, string, attr, blend, cut)

    # --------------------------------------------------------------------------
    def draw_border(self,
        ls = '│', rs = '│', ts = '─', bs = '─',
        tl = '┌', tr = '┐', bl = '└', br = '┘',
        attr = None, blend = pr.BlendMode.OVERLAY
    ) -> None:
        """Draw a border around the top layer of this section with specified characters and attribute."""
        self.get_top_layer().draw_border(ls, rs, ts, bs, tl, tr, bl, br, attr, blend)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _update_dimensions(self) -> None:
        """Update the dimensions of this section based on its relative size and position."""
        if self._parent is None: # root section
            self.h, self.w = pr._CURRENT_BACKEND.get_size()
            self.y, self.x = 0, 0
            return

        h = self.hrel; w = self.wrel
        y = self.yrel; x = self.xrel

        if isinstance(h, float):
            self.h = round(h * self._parent.h)
        elif isinstance(h, int):
            if h < 0: h += self._parent.h
            self.h = min(h, self._parent.h)

        if isinstance(w, float):
            self.w = round(w * self._parent.w)
        elif isinstance(w, int):
            if w < 0: w += self._parent.w
            self.w = min(w, self._parent.w)

        if isinstance(y, float):
            self.y = self._parent.y + round(y * self._parent.h)
        elif isinstance(y, int):
            if y < 0: y += self._parent.h
            self.y = y + self._parent.y

        if isinstance(x, float):
            self.x = self._parent.x + round(x * self._parent.w)
        elif isinstance(x, int):
            if x < 0: x += self._parent.w
            self.x = x + self._parent.x

        y_outbounds = (self.y + self.h) - (self._parent.y + self._parent.h)
        x_outbounds = (self.x + self.w) - (self._parent.x + self._parent.w)

        if y_outbounds > 0: self.y -= y_outbounds
        if x_outbounds > 0: self.x -= x_outbounds


# //////////////////////////////////////////////////////////////////////////////
