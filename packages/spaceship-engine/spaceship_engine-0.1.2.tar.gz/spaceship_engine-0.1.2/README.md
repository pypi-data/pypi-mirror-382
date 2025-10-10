# Spaceship Engine: Comprehensive User Guide

This guide explains how to build terminal/ASCII games with the Spaceship Engine. It covers architecture, APIs, workflows, patterns, performance considerations, and a complete tutorial that develops a basic top‑down exploration game.

---

## 1. Introduction

The Spaceship Engine is a lightweight framework for building real‑time ASCII games in the terminal. It provides:

- A main loop that handles initialization, per‑frame updates, input polling, and rendering.
- A camera and renderer that compose entities into a frame buffer and draw an efficient terminal diff.
- An `Entity` base class with a built‑in `Sprite` for ASCII art and z‑ordering.
- A simple HUD system with templated values and alignment.
- Keystroke polling that exposes the set of keys currently held.
- Math and constants utilities for grid size, character aspect ratio, and vectors.

---
## 2. Project Structure

A recommended layout for a game project using the engine is the following:

```
spaceship/# the engine (as provided)
  game.py
  render/
	camera.py
	entity.py
	hud.py
	render.py
	sprite.py
  input/
	input.py
  utils/
	constants.py
	math.py

my_game/  # your game code
  main.py
```

Place the engine directory on the Python path (same parent folder as your game) so you can `import spaceship...` modules directly.

---

## 3. Engine Architecture Overview

### 3.1 Game

`Game` owns the lifecycle of your program.

- Construct with `Game(init_hook, update_hook, [border=True/False, border_template])`.
- Call `run()` to enter the loop.
- Use `add_entity(entity)` and `remove_entity(entity)` to manage scene content.
- Exposes `HUD`, `camera`, `input`, and the current `entities` list.

### 3.2 Entity

`Entity` represents a world object with:

- `position: Vector` — world coordinates.
- `sprite: Sprite` — ASCII art, with optional center marker and priority.
- `update(dt: float)` — override in subclasses; return `super().update(dt)`.
- `kill()` — mark for removal.

### 3.3 Sprite

`Sprite` renders multi‑line ASCII art:

- Call `load(raw: str | tuple[str, ...], priority: int = 1)`.
- A single tab character `\t` inside the art defines the visual center. This aids alignment and camera transforms.
- `priority` (z‑order): larger values render on top of smaller values.
- An few examples for a raw string would be:
```python
"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡴⣆⠀⠀⠀⠀⠀⣠⡀ ᶻ 𝗓 𐰁 .ᐟ ⣼⣿⡗⠀⠀⠀⠀
⠀⠀⠀⣠⠟⠀⠘⠷⠶⠶⠶⠾⠉⢳⡄⠀⠀⠀⠀⠀⣧⣿⠀⠀⠀⠀⠀
⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣤⣤⣤⣤⣤⣿⢿⣄⠀⠀⠀⠀
⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\t⣧⠀⠀⠀⠀⠀⠀⠙⣷⡴⠶⣦
⠀⠀⢱⡀⠀⠉⠉⠀⠀⠀⠀⠛⠃⠀⢠⡟⠀⠀⠀⢀⣀⣠⣤⠿⠞⠛⠋
⣠⠾⠋⠙⣶⣤⣤⣤⣤⣤⣀⣠⣤⣾⣿⠴⠶⠚⠋⠉⠁⠀⠀⠀⠀⠀⠀
⠛⠒⠛⠉⠉⠀⠀⠀⣴⠟⢃⡴⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠛⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

"""
 ╱|、
(˚ˎ。7  
 |、\t˜〵          
 じしˍ,)ノ
"""
```

### 3.4 Camera

The camera converts world space to screen space and applies character‑aspect compensation. You can:

- Set `camera.position` to pan or follow an entity.
- Switch `camera.mode` (e.g., centered vs top‑left origin) depending on how you want coordinates interpreted.

### 3.5 Renderer

The renderer composes entity sprites into a frame buffer, compares against the previous frame, and prints only the differences using ANSI cursor control. It also draws HUD layers before and after the world.

### 3.6 HUD

The HUD prints formatted text rows at the top and bottom of the screen.

- Use `HUDElement(template: str, values: dict, align: HUDAlignment)`.
- Add elements with `game.HUD.add_top_hud(...)` or `add_bottom_hud(...)`.
- Update dynamic values via `HUDElement.set_value(key, value)`.

### 3.7 Input

The input subsystem polls the keyboard and exposes `game.input.keys_held`, a set of keys currently pressed during the frame. Read it inside your `update(dt)` methods.

### 3.8 Math and Constants

- `Vector(x: float = 0, y: float = 0)` supports addition, subtraction, float scaling (`v * 1.0`), and dot product (`v * v2`). Prefer floating‑point for speed/time scaling.
- Global constants cover grid size and character aspect ratio. Adjust character aspect to match your terminal’s font proportions.


---

## 4. Development Workflow

1. Create your `Game` with `init` and `update` hooks.
2. In `init`, add entities, set camera mode/position, and register HUD elements.
3. Implement entity subclasses and override `update(dt)`.
4. Poll input in `update(dt)` to move entities, trigger actions, and modify state.
5. Update HUD values as state changes.
6. Run and iterate.

---

## 5. Core API Reference (Practical)

### 5.1 Game

- `Game(init_hook: Callable, update_hook: Callable)`
- `run()` — starts loop
- `add_entity(e: Entity) -> Entity` — registers and returns the entity
- `remove_entity(e: Entity)` — detaches from the scene
- Properties: `hud`, `camera`, `input`, `entities`

### 5.2 Entity

- Constructor: `Entity(game: Game, position: Vector)`
- Methods: `update(dt: float)`, `kill()`
- Fields: `position: Vector`, `sprite: Sprite`

### 5.3 Sprite

- `load(raw, priority=1)` where `raw` is either a string or a tuple containing a single triple‑quoted string
- `priority: int` — z‑layer order
- Optional center marker: single in the art

### 5.4 HUD

- `HUDElement(template, values, align)`
- `HUD.add_top_hud(elem)`, `HUD.add_bottom_hud(elem)`
- `HUDElement.set_value(key, value)`

### 5.5 Input

- `game.input.keys_held` — read‑only set of keys for the current frame

### 5.6 Camera

- `camera.position: Vector`
- `camera.mode` — origin mode (center, top‑left, etc.)

---

## 6. Patterns and Best Practices

- Always call `super().update(dt)` at the end of your overridden `update` method unless you have a specific reason not to. This preserves any base‑class housekeeping.
- Use floating‑point speeds (e.g., `60.0`), then scale displacement by `dt` each frame.
- Keep ASCII sprites rectangular with consistent line widths.
- Use sprite `priority` to layer HUD‑like in‑world indicators (arrows, bullets, effects) above background sprites.
- Centralize frequently updated HUD elements by keeping references to their `HUDElement` instances.
- If vertical motion appears distorted, adjust the `CHAR_ASPECT` constant in `constants.py`.
- For portability, ensure the keyboard polling library has the necessary permissions on your OS (mainly for Linux).

---

## 7. Debugging Checklist

- Nothing draws: ensure the sprite was loaded with non‑empty art and that your entity is added to the game.
- Input is unresponsive: verify OS permissions and that you read `keys_held` inside `update`.
- Misalignment: use the tab center marker in sprites or choose an appropriate camera mode.
- Flicker or unexpected redraws: check that your terminal supports ANSI cursor movement and that you are not printing elsewhere.
