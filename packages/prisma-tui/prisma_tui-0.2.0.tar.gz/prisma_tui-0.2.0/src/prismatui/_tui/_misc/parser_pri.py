import prismatui as pr

# --------------------------------------------------------------------------
def save_layer(path_pri: str, layer: "pr.Layer") -> None:
    """Save a layer to a PRI file"""
    chars: list[str] = layer.get_chars_row_as_strs()
    pairs: list[list[int]] = layer.get_attrs()

    h = len(chars)
    w = len(chars[0]) if h > 0 else 0

    assert all(len(row) == w for row in chars), "All rows in 'chars' must have the same width."
    assert all(len(row) == w for row in pairs), "All rows in 'pairs' must have the same width as 'chars'."
    assert len(pairs) == h , "'pairs' must have the same height as 'chars'."

    with open(path_pri, "wb") as file:
        file.write(h.to_bytes(2, byteorder="little"))
        file.write(w.to_bytes(2, byteorder="little"))
        file.write(b'\n')
        file.write('\n'.join(chars).encode("utf-8"))
        file.write(b'\n')
        for row in pairs: file.write(bytes(int(x) for x in row))


# --------------------------------------------------------------------------
def load_layer(path_pri: str) -> "pr.Layer":
    """Load a layer from a PRI file."""
    with open(path_pri, "rb") as file:
        h = int.from_bytes(file.read(2), byteorder="little")
        w = int.from_bytes(file.read(2), byteorder="little")
        nchars = h * (w + 1) - 1 # +1 for breaklines (except the last one)

        file.read(1) # skip a breakline character
        chars = file.read(nchars).decode("utf-8")
        file.read(1) # skip a breakline character

        pairs = [[int(file.read(1)[0]) for _ in range(w)] for _ in range(h)]
        attrs = [[pr._CURRENT_BACKEND.get_color_pair(i) for i in row] for row in pairs]
    return pr.Layer(h, w, chars.split('\n'), attrs)


# --------------------------------------------------------------------------
