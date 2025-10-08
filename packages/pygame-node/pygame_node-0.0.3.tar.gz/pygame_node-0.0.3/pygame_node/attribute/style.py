
from pygame_node.data.types import Color
from dataclasses import dataclass, field
from typing import Optional

@dataclass(slots=True)
class Style:
    """基础样式"""
    background: 'Style.Background' = field(default_factory=lambda: Style.Background())
    stroke: 'Style.Stroke' = field(default_factory=lambda: Style.Stroke())
    shadow: 'Style.Shadow' = field(default_factory=lambda: Style.Shadow())

    @dataclass(slots=True)
    class Background:
        """背景"""
        color: Optional[Color] = None   # 颜色
        border_radius: int = 0          # 圆角(8)

    @dataclass(slots=True)
    class Stroke:
        """边缘"""
        enable: bool = False            # 是否启用
        color: Color = field(
            default_factory=lambda: Color(0, 0, 0)
        )                               # 颜色
        size: int = 1                   # 边缘大小

    @dataclass(slots=True)
    class Shadow:
        """阴影"""
        enable: bool = False            # 是否启用
        color: Color = field(
            default_factory=lambda: Color(0, 0, 0)
        )                               # 颜色
        opacity: float = 0.5            # 不透明度
        ambiguity: float = 0.1          # 模糊度
        distance: float = 8             # 距离
        angle: float = -45              # 角度

@dataclass(slots=True)
class TextStyle(Style):
    """文本样式"""
    color: Color = field(default_factory=lambda: Color(0, 0, 0, 1))
