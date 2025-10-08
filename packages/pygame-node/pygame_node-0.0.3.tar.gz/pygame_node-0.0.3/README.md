# PygameNode
[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat-square&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/Mogui-Hao/PygameNode)

使用 [`Node`](docs/Node.md) 结构管理Pygame资源, 以便快速制作/管理游戏.

还未开发完成
## 1. 快速开始
使用 `pip install pygame_node` 安装这个库.

接着导入库并写一个简单的示例
```python
# 导入 pygame 和 pygame_node 库
import pygame
from pygame_node import *

# 定义作为屏幕大小的变量
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700

# 创建一个场景
class MainScene(BaseScene):
    def __init__(self):
        # 初始化场景, 名称为Main
        super().__init__("Main")

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
```

### 1.1 场景
可在场景对象里添加初始化函数

```python
from pygame_node import *
from pygame.math import Vector3


class MainScene(BaseScene):
    def __init__(self):
        super().__init__("Main")

    # 定义初始化函数
    def init(self, params: 'BaseScene' = None):
        super().init(params)
        # 创建一个文本 "It's a Text Node." 的 TextNode
        # 位置在Vector3(200, 200, 0)
        text = TextNode("It's a Text Node.", position=Vector3(200, 200, 0), font=Font(size=72))

        # 添加到场景中
        self.addNode(text)
```

`font` 参数如果在 `pygame.init()`后定义了全局字体就可以不传

```python
import pygame
from pygame_node import *

pygame.init()
Node.font = Font(size=72)   # 定义全局字体默认字体
```

运行后文字和背景是一个色的, 所以要修改背景色或文字颜色后才能看到.
```python
# 在MainScene中添加, 修改背景色为绿色
def draw(self, screen: Surface):
    screen.fill((0x84, 0xC6, 0x69))
    super().draw(screen)
```
文字颜色可以通过以下代码更改
```python
# 修改文本颜色为白色
text.style.color = Color(255, 255, 255)
```
可以通过设置文字的 `style` 不同值达到不同效果
```python
text.style.shadow.enable = True                 # 启用影子
text.style.shadow.color = Color(64, 128, 255)   # 修改影子颜色

text.style.stroke.enable = True                 # 启用边缘
text.style.stroke.size = 0.5                    # 修改边缘大小
```
文本样式不止这些, [`详情`](pygame_node/attribute/style.py).不同效果可以同时使用
