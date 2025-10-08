import os
from pathlib import Path
from typing import Dict, List

import pygame
from pygame import Surface
from pygame.math import Vector2

from pygame_node.data.event import PointerDownEvent, PointerUpEvent, KeyDownEvent, KeyUpEvent, PointerMoveEvent, \
    WindowDropFileEvent
from pygame_node.data.keys import MouseButton
from pygame_node.event import EventHandler
from pygame_node.node import Node


class BaseScene:
    """场景基类"""

    ROOT_PATH = os.path.dirname(__file__)
    RESOURCES_PATH = os.path.join(ROOT_PATH, "resources")
    TEXTURES_PATH = os.path.join(RESOURCES_PATH, "textures")
    FONTS_PATH = os.path.join(RESOURCES_PATH, "font")
    AUDIOS_PATH = os.path.join(RESOURCES_PATH, "audio")

    def __init__(self, name: str, params: 'BaseScene' = None) -> None:
        """
        :param name: 场景名称
        """
        self.name = name
        self.params = params
        self.nodes: List[Node] = []
        self.event = EventHandler()

    def events(self, events: List[pygame.event.Event]) -> None:
        """处理场景事件（子类实现）"""
        for n in self.nodes[::-1]:
            if len(n.event.events) == 0:
                continue
            for event in events:
                match event.type:
                    case pygame.MOUSEBUTTONDOWN:
                        if self.__is_hovered(event, n):
                            n.event.call_function(PointerDownEvent(button_index=MouseButton(event.button), pos=Vector2(event.pos)))
                    case pygame.MOUSEBUTTONUP: n.event.call_function(PointerUpEvent(button_index=MouseButton(event.button), pos=Vector2(event.pos)))
                    case pygame.MOUSEMOTION: n.event.call_function(PointerMoveEvent(buttons=event.buttons, pos=Vector2(event.pos), rel=Vector2(event.rel)))
                    case pygame.KEYDOWN: n.event.call_function(KeyDownEvent(keycode=event.key))
                    case pygame.KEYUP: n.event.call_function(KeyUpEvent(keycode=event.key))
                    case pygame.DROPFILE: n.event.call_function(WindowDropFileEvent(file=Path(event.file)))
                    case _: ...

    def __is_hovered(self, event: pygame.event.Event, node: Node) -> bool:
        if node.rect.collidepoint(*event.pos):
            if node.mask.overlap_area(node.mask, (
                event.pos[0] - node.rect.left,
                event.pos[1] - node.rect.top,
            )) > 0:
                return True
        return False

    def update(self, dt: float) -> None:
        """更新场景状态（子类实现）"""
        pass

    def draw(self, screen: Surface) -> None:
        """绘制场景内容（子类实现）"""
        for _node in self.nodes:
            _node.draw(screen)

    def init(self, params: 'BaseScene' = None) -> None:
        """进入场景时触发的初始化操作"""
        self.params = params

    def on_exit(self) -> None:
        """离开场景时触发的清理操作"""
        pass

    def addNode(self, node: Node) -> None:
        """添加节点"""
        self.nodes.append(node)

class SceneManager:
    """场景管理模块"""

    def __init__(self, *scenes: BaseScene) -> None:
        """
        场景管理初始化
        :param scenes: 场景对象
        """
        self.scenes: Dict[str, BaseScene] = {}
        self.current_scene: BaseScene = None
        self.add_scene(*scenes)

    def add_scene(self, *scene: BaseScene) -> None:
        """添加多个场景对象"""
        for scene in scene:
            self.scenes[scene.name] = scene

    def switch(self, name: str):
        """切换场景"""
        if name in self.scenes:
            if self.current_scene is not None:
                self.current_scene.on_exit()
            self.current_scene = self.scenes[name]
            self.current_scene.init()

    def update(self, dt: float) -> None:
        """场景更新"""
        self.current_scene.update(dt)

    def events(self, event: List[pygame.event.Event]) -> None:
        """场景事件调用"""
        self.current_scene.events(event)

    def draw(self, screen: Surface) -> None:
        """场景绘制窗口"""
        self.current_scene.draw(screen)


    def __getitem__(self, item: int | str) -> BaseScene:
        if isinstance(item, str):
            return self.scenes[str]
        elif isinstance(item, int):
            return list(self.scenes.values())[item]
