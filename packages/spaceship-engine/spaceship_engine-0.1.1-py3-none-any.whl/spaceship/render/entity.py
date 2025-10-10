from __future__ import annotations
from abc import ABC, abstractmethod

import typing
if typing.TYPE_CHECKING:
    from ..game import Game   # Forward reference for type hinting only

from ..utils.math import Vector
from ..render.sprite import Sprite


class Entity(ABC):
    """
    Abstract base class for all game entities.
    An Entity represents any object in the game world with:
      - A position (Vector)
      - A visual representation (Sprite)
      - An optional type identifier
      - A link to the main Game instance for management
    """

    def __init__(self, game: "Game", position: Vector = Vector()):
        # Reference to the game object managing this entity
        self.game = game
        # World position of the entity
        self._position = position
        # A string identifier for the entity type (optional, e.g. "enemy", "player")
        # The sprite object representing this entity visually
        self._sprite = Sprite()

    # --- Position Management ---
    @property
    def position(self) -> Vector:
        """Return the entity’s world position."""
        return self._position

    @position.setter
    def position(self, value: Vector):
        """
        Update the entity’s world position and also update
        its sprite’s position to match.
        """
        self._position = value
        self._sprite.position = value

    # --- Sprite Management ---
    @property
    def sprite(self) -> Sprite:
        """Return the entity’s sprite."""
        return self._sprite

    @sprite.setter
    def sprite(self, value: Sprite):
        """
        Assign a new sprite to the entity,
        ensuring its position is synced with the entity’s position.
        """
        self._sprite = value
        self._sprite.position = self.position

    # --- Entity Lifecycle ---
    def kill(self):
        """Remove this entity from the game."""
        self.game.remove_entity(self)

    # --- Abstract Methods ---
    @abstractmethod
    def update(self, dt: float):
        """
        Update the entity state.
        Must be implemented by subclasses.
        
        Args:
            dt (float): Time delta since the last update.
        """
        pass

    # --- Rendering ---
    def render(self) -> Sprite:
        """
        Return the sprite for rendering.
        Subclasses may override this if needed.
        """
        return self.sprite
