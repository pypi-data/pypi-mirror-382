import keyboard

class Input:
    def __init__(self) -> None:
        # Cache stores the last checked keys
        self._cache = []
        # Dirty flag indicates whether the cache needs refreshing
        self._dirty = True

    def get_keys_held(self):
        """
        Returns a list of all currently pressed keys.
        This method checks every printable ASCII character (32–126)
        as well as all modifier keys (shift, ctrl, alt, etc.).
        """

        held = []
        keys_to_check = (
            [chr(i) for i in range(32, 127)] +  # Generate all printable ASCII characters
            list(keyboard.all_modifiers)        # Add modifier keys
        )

        for key in keys_to_check:
            try:
                if keyboard.is_pressed(key):
                    held.append(key)
            except:
                # Ignore errors from invalid/unrecognized keys
                pass

        return held
    
    @property
    def keys_held(self):
        """
        Returns cached keys that are currently held down.
        Refreshes the cache only if the 'dirty' flag is set.
        """
        if self._dirty:
            self._cache = self.get_keys_held()
            self._dirty = False
        
        return self._cache

    def make_dirty(self):
        """
        Marks the cache as 'dirty', so the next call
        to keys_held will re-check pressed keys.
        """
        self._dirty = True
