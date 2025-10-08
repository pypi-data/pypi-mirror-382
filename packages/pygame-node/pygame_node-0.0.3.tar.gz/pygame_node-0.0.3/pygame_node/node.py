import math
from copy import deepcopy
from typing import Tuple, List

import pygame
from pygame import Rect, Vector3, Surface, Mask

from pygame_node.data.font import Font
from pygame_node.attribute.style import Style, TextStyle
from pygame_node.data.event import PointerDownEvent
from pygame_node.event import EventHandler


class Node:
    font: Font = None

    def __init__(self,
                 name: str,                                 # 名字
                 parent: 'Node' = None,                     # 父对象
                 *,                                         # 后面必须位置传参
                 position: Vector3 = None,                  # 坐标
                 visible: bool = True,                      # 是否显示
                 rotation: float = 0.0,                     # 旋转
                 size: Tuple[int, int] = None,              # 大小
                 style: Style = None) -> None:
        self._name = name
        self._parent = parent
        self._style = style or Style()
        self.children: List['Node'] = []
        self._visible = visible
        self._rotation = rotation
        self._size = size or (0, 0)
        self._position = position or Vector3(0, 0, 0)
        self._event = EventHandler()
        self._surface: Surface = Surface(size, pygame.SRCALPHA)
        self.__style__ = deepcopy(self.style)
        self.rect
        # self._surface = Surface((self.width, self.height), pygame.SRCALPHA)

    @property
    def name(self) -> str:
        """获取名字"""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def parent(self) -> 'Node':
        """获取父节点"""
        return self._parent

    @parent.setter
    def parent(self, parent: 'Node'):
        self._parent = parent
        parent.children.append(self)

    @property
    def style(self) -> Style:
        """获取样式"""
        return self._style

    @style.setter
    def style(self, style: Style):
        self._style = style
        self.reload_render()

    @property
    def size(self) -> Tuple[int, int]:
        """获取大小"""
        return self._size

    @property
    def rect(self) -> Rect:
        """获取矩形区域"""
        return Rect(self._position.xy, self.size)

    @property
    def x(self) -> int:
        """获取 x 坐标"""
        return self._position.x

    @x.setter
    def x(self, x: int):
        offset = x - self.x
        for child in self.children:
            child.x += offset
        self._position.x = x

    @property
    def y(self) -> int:
        """获取 y 坐标"""
        return self._position.y

    @y.setter
    def y(self, y: int):
        offset = y - self.y
        for child in self.children:
            child.y += offset
        self._position.y = y

    @property
    def width(self) -> int:
        """获取宽"""
        return self.size[0]

    @property
    def height(self) -> int:
        """获取高"""
        return self.size[1]

    @property
    def visible(self) -> bool:
        """是否显示"""
        return self._visible

    @property
    def rotation(self) -> float:
        """获取旋转角度"""
        return self._rotation % 360

    @rotation.setter
    def rotation(self, rotation: float):
        self._rotation = rotation
        self.reload_render()

    @property
    def surface(self) -> Surface:
        """获取区域"""
        return self._surface

    @property
    def mask(self):
        """获取实际内容区域"""
        return pygame.mask.from_surface(self.surface)

    @property
    def event(self) -> EventHandler:
        return self._event

    def draw(self, scene: Surface) -> None:
        if not self.visible:
            return
        if self.style.background.color is not None:
            res = Surface(self.size, pygame.SRCALPHA)
            pygame.draw.rect(res, self.style.background.color.rgba, (0, 0, self.width, self.height),
                             border_radius=self.style.background.border_radius)
            scene.blit(res, (self.x, self.y))

    def update(self, dt: float) -> None:
        """更新状态"""
        for _node in self.children:
            _node.update(dt)

    def reload_render(self) -> None:
        ...

class TextNode(Node):
    def __init__(self,
                 text: str,                 # 文本
                 font: Font = None,         # 字体
                 antialias: bool = False,   # 抗锯齿
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 copy_font: bool = True,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Tuple[int, int] = (0, 0),
                 style: Style = None):
        super().__init__(name or "TextNode", parent, position=position, visible=visible, rotation=rotation, size=size, style=style or TextStyle())
        self._rect = None
        self._text = text
        if copy_font:
            self._font = deepcopy(font or Node.font)
        else:
            self._font = font or Node.font
        self.__font__ = deepcopy(self._font)
        self._antialias = antialias
        self.reload_render()

    @property
    def text(self) -> str:
        """获取文本"""
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self.reload_render()

    @property
    def font(self) -> Font:
        """获取字体"""
        return self._font

    @font.setter
    def font(self, font: Font):
        self._font = font
        self.reload_render()

    @property
    def style(self) -> TextStyle: return Node.style.fget(self)

    @property
    def antialias(self) -> bool:
        """获取抗锯齿"""
        return self._antialias

    @antialias.setter
    def antialias(self, antialias: bool) -> None:
        self._antialias = antialias
        self.reload_render()

    @property
    def render(self) -> Surface:
        """获取渲染"""
        return self._surface

    @property
    def mask(self) -> Mask:
        return pygame.mask.from_surface(self.render)

    @property
    def size(self) -> Tuple[int, int]:
        return self.render.get_size()

    def draw(self, scene: Surface) -> None:
        super().draw(scene)
        if self.__style__ != self.style or self.__font__ != self.font:
            self.reload_render()
        scene.blit(self.render, (self.x, self.y))

    def text_stroke(self, text_surface: Surface) -> Surface:
        """绘制带描边的文本"""
        stroke_size = self.style.stroke.size

        # 计算描边需要扩展的空间
        stroke_width = text_surface.get_width() + 2 * stroke_size
        stroke_height = text_surface.get_height() + 2 * stroke_size
        stroke_surface = pygame.Surface((stroke_width, stroke_height), pygame.SRCALPHA)

        # 在8个方向上绘制描边颜色
        offsets = [(-1, -1), (0, -1), (1, -1),
                   (-1,  0),          (1,  0),
                   (-1,  1), (0,  1), (1,  1)]

        for ox, oy in offsets:
            offset_x = stroke_size + ox * stroke_size
            offset_y = stroke_size + oy * stroke_size
            # 绘制描边颜色
            stroke_surface.blit(text_surface, (offset_x, offset_y))

        # 用描边颜色填充所有绘制过的区域
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if stroke_surface.get_at((x, y))[3] > 0:  # 如果有像素存在
                    stroke_surface.set_at((x, y), self.style.stroke.color.rgb)

        # 在描边Surface上绘制原始文本（覆盖中心部分）
        stroke_surface.blit(text_surface, (stroke_size, stroke_size))

        # 将带描边的文本绘制到场景
        return stroke_surface

    def text_shadow(self, text_surface: Surface) -> Surface:
        """绘制带阴影和旋转的文本，返回拼接后的Surface"""
        angle_rad = math.radians(self.style.shadow.angle)
        shadow_offset_x = self.style.shadow.distance * math.cos(angle_rad)
        shadow_offset_y = self.style.shadow.distance * math.sin(angle_rad)

        shadow_surf = Surface(text_surface.get_size(), pygame.SRCALPHA)
        shadow_surf.fill((*self.style.shadow.color.rgb, int(255 * self.style.shadow.opacity)))

        text_surface_alpha = text_surface.copy().convert_alpha()
        shadow_surf.blit(text_surface_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        shadow_x = self.x + int(shadow_offset_x)
        shadow_y = self.y + int(shadow_offset_y)

        # 计算文本和阴影的边界矩形
        text_bound = text_surface.get_rect(topleft=(self.x, self.y))
        shadow_bound = shadow_surf.get_rect(topleft=(shadow_x, shadow_y))

        # 计算能同时包含文本和阴影的最小矩形
        bounding_rect = text_bound.union(shadow_bound)

        # 创建新的Surface（支持透明通道）
        combined_surface = Surface(bounding_rect.size, pygame.SRCALPHA)
        combined_surface.fill((0, 0, 0, 0))  # 填充透明背景

        # 先绘制阴影（在底层）
        shadow_pos = (shadow_bound.x - bounding_rect.x, shadow_bound.y - bounding_rect.y)
        combined_surface.blit(shadow_surf, shadow_pos)

        # 再绘制文本（在顶层）
        text_pos = (text_bound.x - bounding_rect.x, text_bound.y - bounding_rect.y)
        combined_surface.blit(text_surface, text_pos)

        return combined_surface

    def reload_render(self) -> None:
        # 处理换行符：按行分割文本
        lines = self.text.split('\n')

        # 计算文本总高度（行数 × 行高）
        line_height = self.font.get_sized_height(self.font.size)  # 获取字体高度
        total_height = len(lines) * line_height

        # 计算最大宽度
        max_width = 0
        line_surfaces = []

        for line in lines:
            if line:  # 非空行
                line_surface, line_rect = self.font.render(
                    line,
                    fgcolor=self.style.color.rgb,
                    size=self.font.size
                )
                max_width = max(max_width, line_rect.width)
                line_surfaces.append(line_surface)
            else:
                # 空行也保留位置
                line_surfaces.append(pygame.Surface((0, line_height), pygame.SRCALPHA))

        # 创建总Surface容纳所有行
        text_surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))  # 透明背景

        # 逐行渲染到总Surface
        y_offset = 0
        for line_surface in line_surfaces:
            if line_surface.get_size() != (0, 0):  # 非空行
                text_surface.blit(line_surface, (0, y_offset))
            y_offset += line_height

        # 后续处理保持不变
        if self.rotation != 0:
            text_surface = pygame.transform.rotozoom(text_surface, self.rotation, 1.0)

        self.__style__ = deepcopy(self.style)

        if self.__style__.stroke.enable:
            text_surface = self.text_stroke(text_surface)
        if self.__style__.shadow.enable:
            text_surface = self.text_shadow(text_surface)

        self._surface = text_surface

class TextButtonNode(TextNode):
    def __init__(self,
                 text: str,
                 font: Font = None,
                 antialias: bool = False,
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Tuple[int, int] = (0, 0),
                 style: Style = TextStyle()):
        super().__init__(text, font, antialias, name, parent, position=position, visible=visible, rotation=rotation,
                         size=size, style=style)

        self.event(self.on_click)

    def on_click(self, event: PointerDownEvent):
        print(event)
