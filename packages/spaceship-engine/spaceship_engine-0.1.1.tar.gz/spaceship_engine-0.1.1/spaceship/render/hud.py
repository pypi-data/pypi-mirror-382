from enum import Enum
import re

from ..utils.constants import SIZE_X, RIGHT_MARGIN

class HUDAlignment(Enum):
    RIGHT = 0
    CENTER = 1
    LEFT = 2

class HUDElement():
    def __init__(self, template: str = '', values: dict[str, str] = dict(), align: HUDAlignment = HUDAlignment.CENTER) -> None:
        self._template = template
        self._values = values
        self.compiled_text = ''
        self.alignment = align

        self.resolve_template()

    @property
    def template(self) -> str:
        return self._template
    @template.setter
    def template(self, value: str):
        self._template = value
        self.resolve_template()
    
    @property
    def values(self) -> dict[str, str]:
        return self._values
    @values.setter
    def values(self, value: dict[str, str]):
        self._values = value
        self.resolve_template()
    
    def set_value(self, key: str, value: str):
        """
        Set a single value in the values dictionary and recompile the template.
        """
        self.values[key] = value
        self.resolve_template()

    def resolve_template(self):
        """
        Compile the template string with current values.
        This replaces all occurrences of `key` in the template with the corresponding value from `values`.
        """
        params = self.values.keys()
        regex_pattern = re.compile('`' + '`|`'.join(re.escape(param) for param in params) + '`')

        self.compiled_text = (regex_pattern.sub(lambda match: self.values.get(match.group(0)[1:-1], ''), self.template))[:SIZE_X]

class HUD():
    def __init__(self, top_huds: list[HUDElement] = list(), bottom_huds: list[HUDElement] = list()):
        self._top_huds = top_huds
        self._bottom_huds = bottom_huds
        self.top_buffer = self.get_top_height()

    def get_top_height(self) -> int:
        """
        Calculate the total height of the top HUD elements.
        This is used to determine how many rows to reserve at the top of the terminal.
        """
        R, L, C = 0, 0, 0
        for hud in self.top_huds:
            if hud.alignment == HUDAlignment.RIGHT:
                R += 1
            elif hud.alignment == HUDAlignment.LEFT:
                L += 1
            elif hud.alignment == HUDAlignment.CENTER:
                C += 1

        # Return the maximum of right, left, and center aligned elements
        return max(R, L, C)
    
    def render_top(self) -> list[list[str]]:
        """
        Render the top HUD elements into a list of strings.
        Each string represents a row in the terminal.
        """
        rendered = [[' '] * SIZE_X for _ in range(self.top_buffer)]
        R, L, C = 0, 0, 0
        for hud in self.top_huds:
            if hud.alignment == HUDAlignment.LEFT:
                for i, char in enumerate(hud.compiled_text):
                    rendered[R][i] = char
                R += 1
            elif hud.alignment == HUDAlignment.RIGHT:
                for i, char in enumerate(hud.compiled_text):
                    rendered[L][SIZE_X - RIGHT_MARGIN - len(hud.compiled_text) + i] = char
                L += 1
            elif hud.alignment == HUDAlignment.CENTER:
                for i, char in enumerate(hud.compiled_text):
                    rendered[C][(((SIZE_X - RIGHT_MARGIN) // 2)  - (len(hud.compiled_text)) // 2) + i] = char
                C += 1
        
        return rendered
    
    def render_bottom(self) -> list[list[str]]:
        """
        Render the bottom HUD elements into a list of strings.
        Each string represents a row in the terminal.
        """
        rendered = [[" "] * SIZE_X for _ in range(len(self.bottom_huds))]
        R, L, C = 0, 0, 0
        for hud in self.bottom_huds:
            if hud.alignment == HUDAlignment.LEFT:
                for i, char in enumerate(hud.compiled_text):
                    rendered[R][i] = char
                R += 1
            elif hud.alignment == HUDAlignment.RIGHT:
                for i, char in enumerate(hud.compiled_text):
                    rendered[L][SIZE_X - RIGHT_MARGIN - len(hud.compiled_text) + i] = char
                L += 1
            elif hud.alignment == HUDAlignment.CENTER:
                for i, char in enumerate(hud.compiled_text):
                    rendered[C][(((SIZE_X - RIGHT_MARGIN) // 2)  - (len(hud.compiled_text)) // 2) + i] = char
                C += 1

        return rendered
    
    def add_top_hud(self, hud: HUDElement):
        """
        Add a new HUD element to the top HUD list and update the top buffer height.
        """
        self._top_huds.append(hud)
        self.top_buffer = self.get_top_height()
    
    def add_bottom_hud(self, hud: HUDElement):
        """
        Add a new HUD element to the bottom HUD list.
        """
        self._bottom_huds.append(hud)
    
    @property
    def top_huds(self) -> list[HUDElement]:
        return self._top_huds
    @top_huds.setter
    def top_huds(self, value: list[HUDElement]):
        self._top_huds = value
        self.top_buffer = self.get_top_height()
    
    @property
    def bottom_huds(self) -> list[HUDElement]:
        return self._bottom_huds
    @bottom_huds.setter
    def bottom_huds(self, value: list[HUDElement]):
        self._bottom_huds = value