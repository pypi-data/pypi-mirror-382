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
