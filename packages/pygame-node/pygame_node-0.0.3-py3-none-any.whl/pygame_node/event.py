import functools
import inspect
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Optional

from pygame_node.data.event import Event


class EventPriority(Enum):
    LOWEST = auto()
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    HIGHEST = auto()
    MONITOR = auto()

@dataclass(slots=True)
class EventFunction:
    func: Callable
    priority: EventPriority
    event: Event

class EventHandler:
    def __init__(self):
        self.events: list[EventFunction] = []

    def __call__(self, func: Optional[Callable] = None, *, priority: EventPriority = EventPriority.NORMAL) -> Callable:
        # 如果直接传递了函数(不带括号的用法 @event)
        if func is not None:
            return self._register_function(func, priority)

        # 如果传递了参数(带括号的用法 @event(priority=...)
        def decorator(f: Callable) -> Callable:
            return self._register_function(f, priority)

        return decorator

    def _register_function(self, func: Callable, priority: EventPriority) -> Callable:
        """注册函数到事件列表并返回包装函数"""
        params = list(inspect.signature(func).parameters.values())
        if not len(params) > 0: raise TypeError("EventHandler() missing 1 required positional argument: 'event'")
        for param in params:
            if issubclass(param.annotation, Event):
                self.events.append(EventFunction(func, priority, param.annotation))
                break
        else:
            raise TypeError("EventHandler() missing 1 required positional argument: 'event'")

        # if issubclass(params[-1].annotation, Event):
        #     self.events.append(EventFunction(func, priority, params[-1].annotation))
        # else:
        #     raise TypeError("EventHandler() missing 1 required positional argument: 'event'")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def call_function(self, event: Event) -> None:
        for e in self.events:
            if isinstance(event, e.event):
                e.func(event)
