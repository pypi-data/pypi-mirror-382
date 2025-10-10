import time
from typing import Callable

from .utils.constants import SIZE_X, SIZE_Y
from .render.camera import Camera
from .input.input import Input
from .utils.math import Vector
from .render.render import Renderer
from .render.entity import Entity
from .render.hud import HUD

class Game:
    """Main game loop and entity manager."""

    def __init__(self, init_hook: Callable[[], None] = lambda: None, update_hook: Callable[[float], None] = lambda dt: None, border = False, border_template = '╔═╗\n║ ║\n╚═╝'):
        # Active game entities
        self.entities: list[Entity] = []

        # User-defined hooks
        self.init_hook: Callable[[], None]   = init_hook
        self.update_hook: Callable[[float], None] = update_hook

        # Initialize Core subsystems
        self.renderer = Renderer()
        self.input    = Input()
        self.camera   = Camera()
        self.hud = HUD()

        # Initial terminal setup
        self.renderer.update_full()

        # Fixed timestep state
        self.fixed_dt = 1.0 / 60.0          # 60 Hz logic updates
        self._acc     = 0.0                 # accumulated time
        self._prev_t  = time.perf_counter() # high-resolution clock
        self._max_frame = 0.25              # clamp huge spikes (seconds)
        self._max_updates_per_frame = 10    # avoid spiral of death

        if border:
            self.add_entity(Border(self, border_template=border_template))

    # --- Main Loop ---

    def _fixed_update(self, dt: float) -> None:
        """Fixed update for logic and physics"""
        # Refresh input cache every logic step
        self.input.make_dirty()

        self.update_hook(dt)

        # Loop over a hard copy of entities
        for entity in list(self.entities):
            entity.update(dt)

    def _render(self) -> None:
        """As fast as possible render for drawing"""
        self.renderer.check_resize()
        
        rendered_top_hud = self.hud.render_top()
        self.renderer.draw_hud_top(rendered_top_hud)

        rendered_grid = self.camera.get_render(Vector(SIZE_X, SIZE_Y), self.entities)
        self.renderer.draw_diff(self.hud.top_buffer, rendered_grid)

        rendered_bottom_hud = self.hud.render_bottom()
        self.renderer.draw_hud_bottom(self.hud.top_buffer, rendered_bottom_hud)

    # --- Entity Management ---
    def add_entity(self, entity: Entity) -> Entity:
        """Add a new entity to the game world."""
        self.entities.append(entity)
        return entity

    def remove_entity(self, entity: Entity):
        """Remove an entity from the game world."""
        self.entities.remove(entity)
        
    def run(self):
        """Run the main game loop until interrupted."""
        # Clear screen and call init_hook
        self.renderer.update_full()
        self.init_hook()

        try:
            while True:
                
                #Fixed timestep logic
                now = time.perf_counter()
                frame_time = now - self._prev_t
                self._prev_t = now

                # Clamp to avoid huge catch-ups (e.g., after a debugger pause)
                if frame_time > self._max_frame:
                    frame_time = self._max_frame

                # Accumulate elapsed time
                self._acc += frame_time

                # Do as many fixed updates as needed this frame (but not too many)
                updates = 0
                while self._acc >= self.fixed_dt and updates < self._max_updates_per_frame:
                    self._fixed_update(self.fixed_dt)
                    self._acc -= self.fixed_dt
                    updates += 1

                # Rendering is done always
                self._render()

                #To prevent overuse of resources
                time.sleep(0.001)
        except KeyboardInterrupt:
            pass
        finally:
            self.renderer.clear_screen()
            print("Shutting down…")

class Border(Entity):
	def __init__(self, game: Game, border_template = '╔═╗\n║ ║\n╚═╝'):
		super().__init__(game, Vector())
		


		r = f'\t{border_template[0]}' + f'{border_template[1]}' * (SIZE_X-2) + f'{border_template[2]}\n'
		r += (f'{border_template[4]}' + f'\a' * (SIZE_X - 2) + f"{border_template[6]}\n") * (SIZE_Y - 3)
		r += f'{border_template[8]}' + f'{border_template[9]}' * (SIZE_X-2) + f'{border_template[10]}'

		self.sprite.load(r)
		self.sprite.priority = 100
		self.position = Vector(- SIZE_X / 2, -SIZE_Y)

	def update(self, dt):
		return super().update(dt)