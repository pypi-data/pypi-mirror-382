# Spaceship

spaceship is a terminal based game-engine.
It has a lot of features that making developing games that run on the terminal very easy.

#### Basic game loop

The barebones for a spaceship game is this:

```python
from spaceship.game import Game

game = Game()

def init():
	#Do all initialization logic here

def update():
	#This function will be called every update loop before the entities' update
	#function is called

if __name__ == '__main__':
	game.register_hooks(init = init, update = update)
	game.run()
```

the Game class is the entry-point for the engine.

Before running the game 2 functions are passed to the engine:
- `init` - This function is called after the engine has finished setting up, and can be used to set up things before the update loop is called. This internally assigns the function to variables `init_hook` and `update_hook` respectively.
- `update` - This function is called every 0.05 seconds. This is where the core logic of the game exists

An example Space Invaders game is included.
Run space.py or run.bat to start the example game.
