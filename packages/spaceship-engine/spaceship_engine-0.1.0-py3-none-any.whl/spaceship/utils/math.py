import math

"""
A class representing a 2D vector with basic operations.

Attributes:
    x (float): The x-coordinate of the vector.
    y (float): The y-coordinate of the vector.
"""
class Vector:  
    def __init__(self, x: float = 0, y: float = 0):
        # Store private attributes internally
        self._x = x
        self._y = y

    # --- X property ---
    @property
    def x(self):
        """Get the x-coordinate."""
        return self._x

    @x.setter
    def x(self, new_x):
        """Set the x-coordinate."""
        self._x = new_x
    
    # --- Y property ---
    @property
    def y(self):
        """Get the y-coordinate."""
        return self._y

    @y.setter
    def y(self, new_y):
        """Set the y-coordinate."""
        self._y = new_y
    
    # --- Magnitude ---
    def length(self):
        """Return the Euclidean length of the vector."""
        return math.sqrt(self.length_squared())
    
    def length_squared(self):
        """Return the squared length (avoids sqrt for performance)."""
        return self.x**2 + self.y**2
    
    # --- Products ---
    def dot(self, other):
        """
        Return the dot product between the two vectors.
        """
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        """
        Return the 2D scalar cross product (determinant).
        Equivalent to (x1*y2 - y1*x2).
        """
        return self.x * other.y - self.y * other.x

    def scale(self, factor):
        """Return a new vector scaled by a scalar factor."""
        return Vector(self.x * factor, self.y * factor)
    
    def vectorScale(self, factor):
        """Return a new vector scaled by a scalar factor."""
        return Vector(self.x * factor.x, self.y * factor.y)

    def floored(self):
        """Return a new vector rounded to the nearest integer"""
        return Vector(math.floor(self.x), math.floor(self.y))

    # --- Arithmetic Operators ---
    def __add__(self, other):
        """Vector addition (self + other)."""
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """Vector subtraction (self - other)."""
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        """Return the negated vector (-self)."""
        return Vector(-self.x, -self.y)
    
    # --- Multiplication ---
    def __mul__(self, other):
        """
        Overloaded multiplication:
          - If multiplied by a float → return scaled Vector.
          - If multiplied by another Vector → return dot() result.
        """
        if isinstance(other, (int, float)):
            return self.scale(other)
        elif isinstance(other, Vector):
            return self.dot(other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        """Support scalar * Vector (reverses __mul__)."""
        return self.__mul__(other)
    
    def __matmul__(self, other):
        """Use '@' operator to compute cross product magnitude."""
        return self.cross(other)
    
    # --- Comparison ---
    def __eq__(self, other):
        """Check if two vectors are exactly equal (x and y)."""
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False

    # --- String Representations ---
    def __str__(self) -> str:
        """Return a user-friendly string (e.g., 'X:1 Y:2')."""
        return f"X:{self.x} Y:{self.y}"
    
    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"X:{self.x} Y:{self.y}"
