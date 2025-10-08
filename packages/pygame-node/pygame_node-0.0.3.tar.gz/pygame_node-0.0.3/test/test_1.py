"""
A simple demo.
"""

import os
from typing import List

from pygame import Surface
from pygame.math import Vector3
import pygame

from pygame_node import *

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700
BgColor = (0x84, 0xC6, 0x69)
# BgColor = (0, 255, 0)

ROOT_PATH = os.path.dirname(__file__)
RESOURCES_PATH = os.path.join(ROOT_PATH, "resources")

class MainScene(BaseScene):
    def __init__(self):
        super().__init__("Main")
        self._n = TextButtonNode("Text", position=Vector3(200, 200, 0), antialias=True)

    def init(self, params: 'BaseScene' = None):
        super().init(params)
        self._n.style.color = Color(255, 255, 255)
        self._n.style.shadow.enable = True
        self._n.style.shadow.color = Color(64, 128, 255)

        self.addNode(self._n)
        # self.addNode(self._n1)

    def events(self, events: List[pygame.event.Event]):
        super().events(events)
        # if len(events): print(events)

    def draw(self, screen: Surface):
        screen.fill(BgColor)
        super().draw(screen)

    def update(self, dt: float):
        super().update(dt)

def init(title: str = "Test"):
    pygame.init()
    pygame.display.set_caption(title)
    manager = SceneManager()

    BaseScene.font = pygame.font.Font(os.path.join(RESOURCES_PATH, "font", "Minecraft AE.ttf"), 72)

    Node.font = BaseScene.font

    manager.add_scene(MainScene())

    print(pygame.HWSURFACE | pygame.DOUBLEBUF)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=True)
    clock = pygame.time.Clock()
    manager.switch("Main")

    running = True
    while running:
        events = pygame.event.get()
        # print(events)
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.DROPFILE:
                print(event, event.file, type(event.file))
                ...

        manager.events(events)
        manager.update(clock.tick(0) / 1000.0)

        manager.draw(screen)
        pygame.display.flip()
        print(f"FPS: {clock.get_fps()}", end="\r")

    pygame.quit()


if __name__ == '__main__':
    init()
