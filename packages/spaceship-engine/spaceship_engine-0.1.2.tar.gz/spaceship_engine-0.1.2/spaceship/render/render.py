import shutil
from sys import stdout

from ..render.hud import HUD

from ..utils.constants import SIZE_X, SIZE_Y, LEFT_MARGIN, TOP_MARGIN, CELL_WIDTH

class Renderer:
    """
    Manages the game grid buffer and efficient terminal redraws.
    """
    def __init__(self):
        # Frame buffer holding the last drawn state (used for diffing)
        self.prev_grid = [' '] * (SIZE_X * SIZE_Y)

        # Track terminal size so we can detect when it changes
        self.prev_terminal_size = shutil.get_terminal_size()
    
    # --- HUD drawing ---
    def draw_hud_top(self, rendered: list[list[str]]):
        """
        Render the top HUD.
        """
        # Hide cursor and move it to top-left corner
        stdout.write("\033[?25l")
        stdout.write("\033[H")

        # Iterate over the rendered HUD and print each line
        for row in rendered:
            stdout.write(' ' * LEFT_MARGIN + ''.join(row) + '\n')
    
        # Show cursor
        stdout.flush()

    def draw_hud_bottom(self, grid_start: int, rendered: list[list[str]]):
        """
        Render the bottom HUD.
        """
        # Hide the cursor and move cursor to the bottom of the terminal
        stdout.write("\033[?25l")
        stdout.write("\033[" + str(SIZE_Y + TOP_MARGIN + grid_start) + ";0H")

        # Iterate over the rendered HUD and print each line
        for row in rendered:
            stdout.write(' ' * LEFT_MARGIN + ''.join(row) + '\n')
        
        # Show cursor
        stdout.flush()
    
    # --- Grid Drawing ---
    def draw_diff(self, grid_start: int, render: list[str]):
        """
        Redraw only the cells that have changed since the last frame.

        Args:
            grid_start (int): Terminal row where the grid begins.
            render (list[str]): Flat list of characters to render.
        """
        # Hide cursor
        stdout.write("\033[?25l")

        # Iterate over the new render and compare with the previous state
        for i, cell in enumerate(render):
            if cell != self.prev_grid[i]:
                # Convert 1D index to 2D grid coordinates
                y, x = divmod(i, SIZE_X)

                # Calculate terminal row and column
                r = TOP_MARGIN + grid_start + y + 1
                c = LEFT_MARGIN + x * CELL_WIDTH

                # Move cursor and draw new character
                stdout.write(self.move_to(r, c) + cell)

                # Update buffer
                self.prev_grid[i] = cell
        
        # Show cursor
        stdout.flush()

    def update_full(self):
        """
        Full clear and redraw of the grid.
        Resets buffer and updates terminal size snapshot.
        """
        # Reset state
        self.prev_grid = [' '] * (SIZE_X * SIZE_Y)
        self.prev_terminal_size = shutil.get_terminal_size()

        # Clear the screen
        self.clear_screen()

    # --- Utility Methods ---
    def move_to(self, r: int, c: int) -> str:
        """
        Return an ANSI escape code to move the cursor to (row, col).
        Terminal cursor positions are 1-based.
        """
        return f"\033[{r};{c}H"
    def clear_screen(self):
        """
        Clear the terminal screen completely and reset cursor to top-left.
        """
        stdout.write("\033[2J\033[H")
        stdout.flush()
    def check_resize(self):
        """
        Detect if the terminal was resized.
        If so, trigger a full redraw to avoid misalignment.
        """
        size = shutil.get_terminal_size()
        if size != self.prev_terminal_size:
            self.update_full()