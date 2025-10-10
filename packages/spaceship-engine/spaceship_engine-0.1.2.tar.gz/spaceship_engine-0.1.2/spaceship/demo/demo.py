from spaceship.render.entity import Entity
from spaceship.game import Game
from spaceship.render.hud import HUDAlignment, HUDElement
from spaceship.render.camera import CameraMode
from spaceship.utils.math import Vector
from spaceship.utils.constants import SIZE_Y

class Rock(Entity):
	
	def __init__(self, game: Game, bounce_hook, velocity_hud: HUDElement, position: Vector = Vector()):
		super().__init__(game, position)
		self.vel_hud = velocity_hud
		self.bounce_hook = bounce_hook
		self.sprite.load((
"""
⢀⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆ 
⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠁⠸⣼⡿ 
⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀⠀ 
⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿\t⠿⠿⠿⠛⠉
"""
))		
		self.position = Vector(10, 0)
		self.velocity = Vector()

	def update(self, dt):
		
		held_keys = self.game.input.keys_held

		speed = 2

		if 's' in held_keys:
			self.velocity += Vector(0, 1) * speed
		if 'w' in held_keys:
			self.velocity += Vector(0, -1) * speed
		if 'a' in held_keys:
			self.velocity += Vector(-1, 0) * speed
		if 'd' in held_keys:
			self.velocity += Vector(1, 0) * speed

		self.velocity += Vector(0, 20) * dt
		if self.position.y >= SIZE_Y - 2:
			self.position.y = SIZE_Y - 2
			self.velocity.y *= -1
			self.bounce_hook()

		self.vel_hud.set_value('x', str(int(self.velocity.x)))
		self.vel_hud.set_value('y', str(int(self.velocity.y)))

		self.position += self.velocity * dt

		return super().update(dt)

class SpaceInveders():
	def __init__(self):
		self.game = Game(init_hook = self.init, update_hook = self.update, border = True)
		self.game.run()

	def init(self):
		vel_hud = HUDElement(template='Velocity: (`x`,`y`)', values={'x': '0', 'y': '0'}, align=HUDAlignment.LEFT)
		self.shrek = Rock(self.game, self.shrek_bounced, vel_hud, Vector(10, 10))
		self.game.add_entity(self.shrek)

		self.game.camera.mode = CameraMode.CENTER

		self.game.hud.add_bottom_hud(vel_hud)
		self.game.hud.add_top_hud(
			HUDElement(
				template='Shrek Bounce',
				values={},
				align=HUDAlignment.CENTER
			))
		self.bottom_hud = HUDElement(
				template='Number of bounces: `score`',
				values={'score': '0'},
				align=HUDAlignment.RIGHT
		)
		self.game.hud.add_bottom_hud(self.bottom_hud)

	def shrek_bounced(self):
		self.bottom_hud.set_value('score', str(int(self.bottom_hud.values['score']) + 1))

	def update(self, dt: float):
		held_keys = self.game.input.keys_held

		if 'q' in held_keys:
			exit()
if __name__ == '__main__':
	SpaceInveders()