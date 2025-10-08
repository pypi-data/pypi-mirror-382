from collections import OrderedDict

# ------------------------------------------------------------------------------
def mosaic_parser(layout: str, divider = '\n') -> dict:
    """Parse a mosaic layout string and return a dictionary with the dimensions
    and positions of each character in the layout."""
    if not layout: return {}

    rows = layout.split(divider)
    cols = tuple(zip(*rows))

    row_lenghts = map(len, rows)
    if len(set(row_lenghts)) != 1:
        raise ValueError("Not all mosaic rows have the same lenght.")

    row_idxs = tuple(range(len(row)) for row in rows)
    col_idxs = tuple(range(len(col)) for col in cols)

    chars = set(layout)
    if divider in chars: chars.remove(divider)

    h_mosaic = len(rows)
    w_mosaic = len(cols)

    data = OrderedDict()
    for char in sorted(chars):
        masked_row_idxs = _apply_mask(row_idxs, rows, char)
        masked_col_idxs = _apply_mask(col_idxs, cols, char)

        err_prefix = "Error parsing mosaic layout:"
        if not _all_elements_equal(masked_row_idxs):
            raise ValueError(f"{err_prefix} Not all rows for char '{char}' have the same length.")

        if not _all_elements_equal(masked_col_idxs):
            raise ValueError(f"{err_prefix} Not all columns for char '{char}' have the same length.")

        if not _is_sequential(masked_row_idxs[0]):
            raise ValueError(f"{err_prefix} Rows of char '{char}' are interrupted.")

        if not _is_sequential(masked_col_idxs[0]):
            raise ValueError(f"{err_prefix} Columns of char '{char}' are interrupted.")

        y_char = masked_col_idxs[0][0] / h_mosaic
        x_char = masked_row_idxs[0][0] / w_mosaic
        h_char = len(masked_col_idxs[0]) / h_mosaic
        w_char = len(masked_row_idxs[0]) / w_mosaic
        data[char] = (h_char, w_char, y_char, x_char)

    return data

# ------------------------------------------------------------------------------
def _apply_mask(idxs: list[list[int]], mat: list[list[str]], char: str) -> tuple[tuple[int]]:
    """Apply a mask to the matrix to filter out elements that match the given character."""
    mat_out = tuple(map(
        lambda idx, arr: tuple(filter(
            lambda tup: tup[1] == char,
            zip(idx, arr)
        )),
        idxs, mat
    ))
    return tuple(tuple(n[0] for n in arr) for arr in mat_out if arr)

# ------------------------------------------------------------------------------
def _all_elements_equal(iterable: iter) -> bool:
    """Check if all elements in the iterable are equal."""
    iterator = iter(iterable)
    try: first = next(iterator)
    except StopIteration: return True
    return all(first == rest for rest in iterator)

# ------------------------------------------------------------------------------
def _is_sequential(iterable: iter) -> bool:
    """Check if the elements in the iterable are sequential, starting from the first element."""
    iterator = iter(iterable)
    try: first = next(iterator)
    except StopIteration: return True
    return all(i == element for i,element in enumerate(iterator, start = first + 1))

# ------------------------------------------------------------------------------

################################################################################
if __name__ == "__main__":
    #### test the parser

    layouts = dict(
        empty = '',
        row_clean = '\n'.join((
            "aaab",
        )),
        row_bad = '\n'.join((
            "axab",
        )),
        col_clean = '\n'.join((
            "a",
            "a",
            "c",
        )),
        col_bad = '\n'.join((
            "a",
            "x",
            "a",
            "c",
        )),
        box_clean = '\n'.join((
            "ltttt",
            "laaab",
            "laaab",
            "lcddd",
        )),
        box_missing_char = '\n'.join((
            "ltttt",
            "laaab",
            "laaa",
            "lcddd",
        )),
        box_bad_corner = '\n'.join((
            "ltttt",
            "laaab",
            "laaxb",
            "lcddd",
        )),
        box_bad_row = '\n'.join((
            "ltttt",
            "laaab",
            "lxxxb",
            "laaab",
            "lcddd",
        )),
        box_bad_col = '\n'.join((
            "ltttt",
            "laxab",
            "laxab",
            "lcddd",
        )),
        box_bad_interior = '\n'.join((
            "ltttt",
            "laaab",
            "laxab",
            "laaab",
            "lcddd",
        )),
    )

    for k, v in layouts.items():
        print("------------------", k)
        print(v); print()
        try:
            hwyx_data = mosaic_parser(v)
        except ValueError as e:
            print("XXX", e)
        else:
            print(*sorted(hwyx_data.items()), sep = '\n')
        print()


################################################################################
