# 导入 pygame 和 pygame_node 库
import pygame
from pygame import Vector3, Surface

from pygame_node import *

# 定义作为屏幕大小的变量
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700


# 创建一个场景
class MainScene(BaseScene):
    def __init__(self):
        super().__init__("Main")

    # 定义初始化函数
    def init(self, params: 'BaseScene' = None):
        super().init(params)
        # 创建一个文本 "It's a Text Node." 的 TextNode
        # 位置在Vector3(200, 200, 0)
        text = TextNode("It's a Text Node.", position=Vector3(200, 200, 0), font=pygame.font.Font(size=72), antialias=True)
        text.style.color = Color(255, 255, 255)
        text.style.shadow.enable = True
        text.style.shadow.color = Color(64, 128, 255)
        # 添加到场景中
        self.addNode(text)

    def draw(self, screen: Surface):
        screen.fill((0x84, 0xC6, 0x69))
        super().draw(screen)

# pygame 初始化
pygame.init()

# 创建场景管理器, 把场景传入创建管理器里
main_scene = MainScene()
manager = SceneManager(main_scene)

# 创建屏幕对象和时钟对象
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=True)
clock = pygame.time.Clock()

# 切换到 Main 场景
manager.switch("Main")

# 创建运行状态变量
running = True
while running:
    # 获取事件
    events = pygame.event.get()
    for event in events:
        # 程序退出
        if event.type == pygame.QUIT:
            running = False
            break

    # 场景处理事件
    manager.events(events)

    # 场景更新
    manager.update(clock.tick(0) / 1000.0)

    # 绘制场景
    manager.draw(screen)
    pygame.display.flip()

pygame.quit()