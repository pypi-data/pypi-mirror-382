import re
from copy import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class SpaceMode(Enum):
    NORMAL = "NORMAL"
    PRE = "PRE"


@dataclass
class CanvasState:
    position: int = 0
    text_transform: Callable[[str], str] = lambda s: s
    bold: bool = False
    italic: bool = False
    underline: bool = False
    space_mode: SpaceMode = SpaceMode.NORMAL


# carriage return, line feed, tab and space
NORMAL_SPACES = re.compile("[\x0d\x0a\x09\x20]+")
NORMAL_SPACES_START = re.compile("^[\x0d\x0a\x09\x20]+")


def fix_text_normal(text: str) -> str:
    text = " ".join(NORMAL_SPACES.split(text))
    return text


def fix_text_pre(text: str) -> str:
    return text


@dataclass
class Canvas:
    text: str = ""
    position: int = 0
    states: list[CanvasState] = field(default_factory=lambda: [CanvasState()])

    bold_started: int | None = None
    italic_started: int | None = None
    underline_started: int | None = None

    def enter_state(
            self,
            text_transformation: Callable[[str], str] | None,
            bold: bool | None = None,
            italic: bool | None = None,
            underline: bool | None = None,
            space_mode: SpaceMode | None = None,
    ) -> None:
        new_state = copy(self.states[-1])
        new_state.position = self.position
        if text_transformation is not None:
            new_state.text_transformation = text_transformation
        if bold is not None:
            new_state.bold = bold
        if italic is not None:
            new_state.italic = italic
        if underline is not None:
            new_state.underline = underline
        if space_mode is not None:
            new_state.space_mode = space_mode

    @property
    def text_transform(self) -> Callable[[str], str]:
        return self.states[-1].text_transform

    @property
    def space_transform(self) -> Callable[[str], str]:
        mode = self.states[-1].space_mode
        if mode is SpaceMode.NORMAL:
            return fix_text_normal
        if mode is SpaceMode.PRE:
            return fix_text_pre
        raise ValueError(f"Unknown text_mode: {mode}")

    def _add_text_raw(self, text: str) -> None:
        if not text:
            return
        self.text += text
        self.position += len(text.encode("utf-16-le")) // 2

    def add_text(self, text):
        text = self.text_transform(text)
        text = self.space_transform(text)
        self._add_text_raw(text)
