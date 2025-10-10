from ..utils.math import Vector

class Sprite:
    """Represents an ASCII sprite with a position, size, center, and z-priority."""

    def __init__(self):
        # Original (raw) multi-line string used to create the sprite
        self.raw_string = ''
        # 2D character grid as a list of strings (each entry = one row)
        self.decoded_string = []
        # Sprite dimensions in characters: x = width, y = height
        self.size = Vector()
        # Center of the sprite in local coords; may be set via a tab marker
        self.center = Vector()
        # Z-order priority: higher numbers render on top of lower ones
        self.priority = 1

        # World-space position of the sprite (updated by owning Entity/Camera)
        self.position = Vector()

    def load(self, raw_string, priority=1):
        """
        Initialize the sprite from a raw ASCII string.

        Conventions:
          - The sprite may include a single tab character ('\t') to mark its
            visual center. The tab is removed from the final grid and its
            (x, y) position becomes self.center.
          - If no tab is present, center defaults to (0, 0).
        """
        # Split raw ASCII art into lines (rows)
        lines = raw_string.split('\n')

        centerDefined = False
        for i, line in enumerate(lines):
            # If a tab appears in this line, treat its position as the center
            if '\t' in line:
                if centerDefined: raise ValueError("Too many \\t characters in sprite.")
                centerDefined = True
                # Center is the first tab's column (x) and current row (y)
                self.center = Vector(line.index('\t'), i)
                # Remove the tab from the visible data
                lines[i] = line[:self.center.x] + line[self.center.x + 1:]
        
        # If no explicit center marker was found, default to (0, 0)
        if centerDefined == False:
            self.center = Vector()
        
        # Store values for rendering
        self.raw_string = raw_string
        self.decoded_string = lines
        self.size = Vector(max(len(line) for line in lines), len(lines))
        self.priority = priority
