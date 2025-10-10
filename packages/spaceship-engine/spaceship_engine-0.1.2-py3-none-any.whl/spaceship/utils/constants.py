# --- Global settings ---

# Logical grid size (in character cells)
# WIDTH  x  HEIGHT
SIZE_X, SIZE_Y = 150, 40

# Number of terminal columns used to display one cell horizontally.
# For monospace terminals this is 1; increase if you render spacing between cells.
CELL_WIDTH = 1

# Padding around the grid, in terminal columns/rows.
# LEFT/RIGHT affect the starting column for each drawn cell,
# TOP/BOTTOM can be used by a HUD or spacing above/below the grid.
LEFT_MARGIN = 2
RIGHT_MARGIN = 1
TOP_MARGIN = 0

# Character cell aspect ratio (height / width).
# 1.0 means square cells in your rendering math.
# If you detect real console font metrics, override this.
CHAR_ASPECT = 2

def configure(
    *,
    size_x=None, size_y=None,
    cell_width=None,
    left_margin=None, right_margin=None, top_margin=None,
    char_aspect=None,
):
    """Override settings at runtime."""
    globals().update({
        "SIZE_X": size_x if size_x is not None else globals()["SIZE_X"],
        "SIZE_Y": size_y if size_y is not None else globals()["SIZE_Y"],
        "CELL_WIDTH": cell_width if cell_width is not None else globals()["CELL_WIDTH"],
        "LEFT_MARGIN": left_margin if left_margin is not None else globals()["LEFT_MARGIN"],
        "RIGHT_MARGIN": right_margin if right_margin is not None else globals()["RIGHT_MARGIN"],
        "TOP_MARGIN": top_margin if top_margin is not None else globals()["TOP_MARGIN"],
        "CHAR_ASPECT": char_aspect if char_aspect is not None else globals()["CHAR_ASPECT"],
    })