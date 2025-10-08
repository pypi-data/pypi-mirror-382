from enum import Enum

class MouseButton(Enum):
    # 与任何鼠标按钮都不对应的枚举值. 这用于初始化具有通用状态的 MouseButton 属性.
    MOUSE_BUTTON_NONE = 0
    # 鼠标主键, 通常分配给左键.
    MOUSE_BUTTON_LEFT = 1
    # 鼠标次键, 通常分配给右键.
    MOUSE_BUTTON_RIGHT = 3
    # 鼠标中键.
    MOUSE_BUTTON_MIDDLE = 2
    # 鼠标滚轮向上滚动.
    MOUSE_BUTTON_WHEEL_UP = 4
    # 鼠标滚轮向下滚动.
    MOUSE_BUTTON_WHEEL_DOWN = 5
    # 鼠标滚轮左键（仅在某些鼠标上有实现）.
    MOUSE_BUTTON_WHEEL_LEFT = 6
    # 鼠标滚轮右键（仅在某些鼠标上有实现）.
    MOUSE_BUTTON_WHEEL_RIGHT = 7
    # 鼠标额外键 1. 有时会出现, 通常位于鼠标的两侧.
    MOUSE_BUTTON_XBUTTON1 = 8
    # 鼠标额外键 2. 有时会出现, 通常位于鼠标的两侧.
    MOUSE_BUTTON_XBUTTON2 = 9

