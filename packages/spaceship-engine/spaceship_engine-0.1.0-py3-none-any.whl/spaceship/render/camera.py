from ..render.entity import Entity
from ..utils.math import Vector
from ..utils.constants import SIZE_X, SIZE_Y, CHAR_ASPECT

from enum import Enum
from math import floor

# Camera positioning modes
class CameraMode(Enum):
    CENTER = 0     # Camera is centered on the target
    TOP_LEFT = 1   # Origin is top-left corner
    TOP_RIGHT = 2  # Origin is top-right corner
    BOT_LEFT = 3   # Origin is bottom-left corner
    BOT_RIGHT = 4  # Origin is bottom-right corner

class Camera:
    def __init__(self, position: Vector = Vector(), cameraMode: CameraMode = CameraMode.CENTER):
        # Current camera position in world space
        self.position = position
        # How the camera interprets origin offset (center, corners, etc.)
        self.mode = cameraMode
        # Camera viewport size (width, height)
        self.size = Vector(SIZE_X, SIZE_Y)
        # Adjust for character aspect ratio (since characters are usually taller than wide)
        self.aspect_adjustment_factor = 1.0 / CHAR_ASPECT

    def get_transformed_vector(self, vector: Vector) -> Vector:
        """
        Transforms a world position into camera space by:
        1. Subtracting camera position
        2. Applying aspect ratio scaling
        3. Offsetting based on the camera mode
        """

        # Default offset: center of the screen
        offset = Vector(SIZE_X / 2, SIZE_Y / 2)

        # Adjust based on camera mode
        if self.mode == CameraMode.TOP_LEFT:
            offset = Vector()
        elif self.mode == CameraMode.TOP_RIGHT:
            offset = Vector(SIZE_X - 1, 0)
        elif self.mode == CameraMode.BOT_LEFT:
            offset = Vector(0, SIZE_Y - 1)
        elif self.mode == CameraMode.BOT_RIGHT:
            offset = Vector(SIZE_X - 1, SIZE_Y - 1)

        # Translate world → camera coordinates
        # Scale Y by 0.5 to compensate for char aspect
        return (vector - self.position).vectorScale(Vector(1, self.aspect_adjustment_factor)) + offset
    
    def get_render(self, display_size: Vector, entities: list[Entity]) -> list[str]:
        """
        Render all entities into a text buffer, considering their positions,
        sprite characters, and render priority.
        """
        width, height = int(display_size.x), int(display_size.y)

        # Each buffer cell holds a character and its z-priority
        buffer = [{'display': ' ', 'priority': 0} for _ in range(width * height)]

        # Draw each entity onto the buffer
        for entity in entities:
            sprite = entity.render()  # Get entity sprite (char grid + metadata)
            center_cam = self.get_transformed_vector(sprite.position).floored()
            center_floored = sprite.center.floored()

            # Iterate sprite pixel grid
            for y, line in enumerate(sprite.decoded_string):
                for x, pixel in enumerate(line):

                    #Skip transparent pixels
                    if pixel == '\a': continue

                    # Position relative to sprite center
                    rel = Vector(x, y) - center_floored
                    # Transform to world/screen position
                    world_pos = center_cam + rel

                    # Skip anything outside of viewport
                    if not (0 <= world_pos.x < width and 0 <= world_pos.y < height):
                        continue

                    # Flatten 2D → 1D index in buffer
                    idx = get_index(world_pos, display_size)

                    # Only overwrite if this sprite has higher or equal priority
                    if sprite.priority >= buffer[idx]['priority']:
                        buffer[idx] = {'display': pixel, 'priority': sprite.priority}

        # Convert buffer into a flat list of characters (ready for joining/printing)
        return [cell['display'] for cell in buffer]

def get_index(position: Vector, size: Vector) -> int:
    """
    Converts a 2D (x, y) coordinate into a 1D index in the buffer.
    """
    xi = floor(position.x)
    yi = floor(position.y)
    return xi + yi * int(size.x)
