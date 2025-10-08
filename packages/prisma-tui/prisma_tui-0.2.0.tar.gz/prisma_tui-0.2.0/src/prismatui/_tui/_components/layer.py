from typing import Generator

import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    """Layer class for managing pixel data in a 2D grid."""
    def __init__(self,
        h: int, w: int,
        chars: list[str] = None,
        attrs: list[list[int]] = None,
        blend = pr.BlendMode.OVERLAY
    ):
        if chars is None: chars = ((pr.BLANK_CHAR for _ in range(w)) for _ in range(h))
        if attrs is None: attrs = ((pr.BLANK_ATTR for _ in range(w)) for _ in range(h))
        self.h: int = h
        self.w: int = w
        self._data: list[list[pr.Pixel]] = self.get_pixel_mat(chars, attrs)
        self.blend_mode: pr.BlendMode = blend


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @classmethod
    def get_pixel_mat(cls, chars: list[str], attrs: list[list[int]]) -> list[list["pr.Pixel"]]:
        """Create a pixel matrix from a matrix of characters and a matrix of attributes."""
        return [
            [pr.Pixel(c,a) for c,a in zip(row_chars, row_attrs)]
            for row_chars, row_attrs in zip(chars, attrs)
        ]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_size(self, h: int, w: int) -> None:
        """Set the size of the layer, adjusting the pixel matrix accordingly."""
        if   h < self.h: self._remove_rows(h)
        elif h > self.h: self._add_rows(h - self.h)
        self.h = h

        if   w < self.w: self._remove_cols(w)
        elif w > self.w: self._add_cols(w - self.w)
        self.w = w

    # --------------------------------------------------------------------------
    def get_chars(self) -> list[list[str]]:
        """Get the characters of the layer as a 2D list of chars."""
        return [[pixel._char for pixel in row] for row in self._data]

    # --------------------------------------------------------------------------
    def get_chars_row_as_strs(self) -> list[str]:
        """Get the characters of the layer as a list of strings, one for each row."""
        return [''.join(pixel._char for pixel in row) for row in self._data]

    # --------------------------------------------------------------------------
    def get_attrs(self) -> list[list[int]]:
        """Get the attributes of the layer as a 2D list of ints."""
        return [[pixel._attr for pixel in row] for row in self._data]

    # --------------------------------------------------------------------------
    def copy(self) -> "Layer":
        """Create a copy of the layer."""
        return Layer(self.h, self.w, self.get_chars(), self.get_attrs(), self.blend_mode)

    # --------------------------------------------------------------------------
    def clear(self) -> None:
        """Clear the layer, resetting all pixels to blank."""
        self._data = [self._create_row(self.w) for _ in range(self.h)]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def draw_layer(self, y: int | str, x: int | str, layer: "Layer") -> None:
        """Draw another layer onto this layer at the specified coordinates."""
        h = min(layer.h, self.h)
        w = min(layer.w, self.w)
        layer = layer.copy()
        layer.set_size(h, w)
        y, x = self._parse_coords(h, w, y, x)
        self._stamp(y, x, layer._data, layer.blend_mode)

    # --------------------------------------------------------------------------
    def draw_matrix(self, y: int | str, x: int | str, chars: list[str], attrs: list[list[int]], blend = pr.BlendMode.OVERLAY) -> None:
        data = self.get_pixel_mat(chars, attrs)
        self._stamp(y, x, data, blend)

    # --------------------------------------------------------------------------
    def draw_text(self,
        y: int | str,  # Can be an integer or a string indicating position (e.g., 'T', 'C', 'B')
        x: int | str,  # Can be an integer or a string indicating position (e.g., 'L', 'C', 'R')
        string, # Accepts any object that can be converted to a string
        attr: int = None,
        blend = pr.BlendMode.OVERLAY,
        cut: dict[str, str] = {} # Cut dictionary to specify which edges to cut (e.g., {'T': 1, 'B': 2})
    ) -> None:
        """Draw a string at the specified coordinates with optional attributes and blending mode."""
        if attr is None: attr = pr.BLANK_ATTR

        rows = str(string).split('\n')
        h = min(len(rows), self.h)
        w = min(max(map(len, rows)), self.w)

        y, x = self._parse_coords(h, w, y, x)
        if (x >= self.w) or (y >= self.h): return

        chars = [row.ljust(w, pr.BLANK_CHAR)[:w] for row in rows[:h]]
        chars = self._parse_cut(y, x, cut, chars)
        attrs = [[attr for _ in row] for row in chars]
        data = self.get_pixel_mat(chars, attrs)
        self._stamp(y, x, data, blend)

    # --------------------------------------------------------------------------
    def draw_border(self,
        ls = '│', rs = '│', ts = '─', bs = '─',
        tl = '┌', tr = '┐', bl = '└', br = '┘',
        attr = None, blend = pr.BlendMode.OVERLAY
    ) -> None:
        """Draw a border around the layer with specified characters and attribute."""
        if attr is None: attr = pr.BLANK_ATTR

        h = self.h - 2
        w = self.w - 2
        BC = pr.BLANK_CHAR
        BA = pr.BLANK_ATTR
        data = self.get_pixel_mat(
            chars = \
                [tl + ts*w + tr]   +\
                [ls + BC*w + rs]*h +\
                [bl + bs*w + br],
            attrs = \
                [[attr] + [attr]*w + [attr]]   +\
                [[attr] + [ BA ]*w + [attr]]*h +\
                [[attr] + [attr]*w + [attr]]
        )
        self._stamp(0, 0, data, blend)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def yield_render_data(self) -> Generator[tuple[str, int], None, None]:
        """Yield characters and their attributes ready for rendering."""
        flat_chars = ''.join(''.join(pixel._char for pixel in row) for row in self._data)
        flat_attrs = [pixel._attr for row in self._data for pixel in row]

        attrs_offset_0 = flat_attrs[:-1]
        attrs_offset_1 = flat_attrs[1:]

        attrs_mask = (a != b for a,b in zip(attrs_offset_0, attrs_offset_1))
        border_idxs = [0] + [i for i,a in enumerate(attrs_mask, start = 1) if a] + [len(flat_chars)]

        for i0,i1 in zip(border_idxs[:-1], border_idxs[1:]):
            yield flat_chars[i0:i1], flat_attrs[i0]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _parse_coords(self, h: int, w: int, y: int | str, x : int | str) -> tuple[int, int]:
        """Parse the coordinates for drawing, allowing for string-based positioning."""
        if isinstance(y, str):
            match y[0].upper():
                case 'T': yval = 0
                case 'C': yval = (self.h - h) // 2
                case 'B': yval = self.h - h
                case  _ : raise ValueError(f"Invalid y value: '{y}'")
            modifier = y[1:]
            if modifier: yval += int(modifier)
        else: yval = y

        if isinstance(x, str):
            match x[0].upper():
                case 'L': xval = 0
                case 'C': xval = (self.w - w) // 2
                case 'R': xval = self.w - w
                case  _ : raise ValueError(f"Invalid x value: '{y}'")
            modifier = x[1:]
            if modifier: xval += int(modifier)
        else: xval = x

        return yval, xval


    # --------------------------------------------------------------------------
    def _parse_cut(self, y: int, x: int, cut: dict[str, str], chars: list[str]) -> list[str]:
        """Parse a cut dictionary to adjust the characters matrix."""
        for k,v in cut.items():
            match k.upper():
                case 'T': chars = chars[v:]
                case 'B': chars = chars[:self.h-y-v]
                case 'L': chars = tuple(map(lambda row: row[v:], chars))
                case 'R': chars = tuple(map(lambda row: row[:self.w-x-v], chars))
                case  _ : raise ValueError(f"Invalid cut key: '{k}'")
        return chars


    # --------------------------------------------------------------------------
    def _stamp(self,
        y: int, x: int,
        data: list[list["pr.Pixel"]],
        blend = pr.BlendMode.OVERLAY
    ) -> None:
        """Stamp a matrix of pixels onto the layer at the specified coordinates."""
        if (y >= self.h) or (x >= self.w): return
        if not len(data): return

        match blend:
            case pr.BlendMode.OVERLAY:    func = pr.Pixel.overlay
            case pr.BlendMode.OVERWRITE:  func = pr.Pixel.overwrite
            case pr.BlendMode.MERGE_ATTR: func = pr.Pixel.merge_attr
            case _ : raise ValueError(f"Unknown blend_mode: {blend}")

        h = len(data)
        w = len(data[0])

        y0 = y; x0 = x
        y1 = min(y + h, self.h)
        x1 = min(x + w, self.w)

        mat_orig = self._data[y0:y1]
        mat_modf = data[:y1-y]

        self._data[y0:y1] = [
            row_orig[:x0] + [
                func(o,m) for o,m in zip(row_orig[x0:x1], row_modf[:x1-x])
            ] + row_orig[x1:]
            for row_orig, row_modf in zip(mat_orig, mat_modf)
        ]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _create_row(self, length: int) -> list["pr.Pixel"]:
        """Create a row of pixels with the specified length, initialized to blank."""
        return [pr.Pixel() for _ in range(length)]

    # --------------------------------------------------------------------------
    def _add_rows(self, n: int) -> None:
        """Add 'n' rows to the layer, initializing them with blank pixels."""
        self._data += [self._create_row(self.w) for _ in range(n)]

    # --------------------------------------------------------------------------
    def _add_cols(self, n: int) -> None:
        """Add 'n' columns to each row in the layer, initializing them with blank pixels."""
        self._data = [row + self._create_row(n) for row in self._data]

    # --------------------------------------------------------------------------
    def _remove_rows(self, n: int) -> None:
        """Remove rows after the first 'n' rows."""
        self._data = self._data[:n]

    # --------------------------------------------------------------------------
    def _remove_cols(self, n: int) -> None:
        """Remove columns after the first 'n' columns."""
        self._data = [row[:n] for row in self._data]


# //////////////////////////////////////////////////////////////////////////////
