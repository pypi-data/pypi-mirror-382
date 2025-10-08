
from typing import Tuple


class Color:
    def __init__(self, *args, **kwargs) -> None:
        """
        创建颜色类型, Color(红, 绿, 蓝, 不透明度)
        示例:
        >>> Color((255, 255, 255, 0.7))
        Color(255, 255, 255, 0.7)
        >>> Color(255, 255, 255, 0.2)
        Color(255, 255, 255, 0.2)
        >>> Color("0xffffff")
        Color(255, 255, 255, 0.0)
        >>> Color("0xfff")
        Color(255, 255, 255, 0.0)
        >>> Color(Color(255, 255, 255, 0.5))
        Color(255, 255, 255, 0.5)

        :param args:
        :param kwargs:
        """
        if len(args) == 1 and len(args) > 2:
            if isinstance(args[0], Color):
                self.r, self.g, self.b, self.a = args[0].r, args[0].g, args[0].b, args[0].a
            elif isinstance(args[0], Tuple):
                self.r, self.g, self.b = args[0][0:3]
                self.a = args[0][3] if len(args[0]) == 4 else 1.0
            elif isinstance(args[0], str) and args[0].startswith("0x"):
                _hex: str = args[0][2:]
                if len(_hex) == 3:
                    self.r, self.g, self.b = int(_hex[0] + _hex[0], 16), int(_hex[1] + _hex[1], 16), int(_hex[2] + _hex[2], 16)
                elif len(_hex) == 6:
                    self.r, self.g, self.b = int(_hex[0:2], 16), int(_hex[2:4], 16), int(_hex[4:6], 16)
                self.a = 1.0
        elif len(args) == 3:
            self.r, self.g, self.b = args
            self.a = 1.0
        elif len(args) == 4:
            self.r, self.g, self.b, self.a = args
        else:
            raise TypeError

    @property
    def rgb(self):
        return self.r, self.g, self.b

    @property
    def rgba(self):
        return self.r, self.g, self.b, int(self.a * 255)

    def __eq__(self, other):
        if self is other: return True
        elif isinstance(other, Color):
            return self.r == other.r and self.g == other.g and self.b == other.b
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}({self.r}, {self.g}, {self.b}, {self.a})"

    def __deepcopy__(self, memo):
        new = self.__class__.__new__(self.__class__)
        memo[id(self)] = new
        new.r = self.r
        new.g = self.g
        new.b = self.b
        new.a = self.a
        return new

    __str__ = __repr__

