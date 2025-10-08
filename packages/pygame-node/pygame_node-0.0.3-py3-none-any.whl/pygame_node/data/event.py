from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

from pygame import Vector2

from pygame_node.data.keys import MouseButton


@dataclass(slots=True)
class Event:
    ...

@dataclass(slots=True)
class PointerEvent(Event):
    button_index: MouseButton = MouseButton.MOUSE_BUTTON_NONE
    pos: Vector2 = field(default_factory=Vector2(0, 0))

@dataclass(slots=True)
class KeyEvent(Event):
    keycode: int

@dataclass(slots=True)
class WindowEvent(Event):
    window: ...

@dataclass(slots=True)
class WindowDropFileEvent(WindowEvent):
    file: Path

@dataclass(slots=True)
class PointerDownEvent(PointerEvent): ...

@dataclass(slots=True)
class PointerUpEvent(PointerEvent): ...

@dataclass(slots=True)
class PointerClickEvent(PointerEvent): ...

@dataclass(slots=True)
class PointerMoveEvent(Event):
    pos: Vector2 = field(default_factory=Vector2(0, 0))
    rel: Vector2 = field(default_factory=Vector2(0, 0))
    buttons: Tuple[int] = field(default_factory=tuple())

@dataclass(slots=True)
class KeyDownEvent(KeyEvent): ...

@dataclass(slots=True)
class KeyUpEvent(KeyEvent): ...
