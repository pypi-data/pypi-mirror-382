from setuptools import setup, find_packages
from pygame_node import __version__

setup(
    name="pygame_node",  # 这是将来pip install时使用的名字，确保在PyPI上唯一
    version=__version__,        # 遵循语义化版本规范
    author="MoGui-Hao",
    author_email="mogui_hao@outlook.com",
    description="Use Node structures to manage Pygame resources for rapid game creation and management.",
    long_description=open("README.md", encoding="utf-8").read(),  # 将README内容作为长描述
    long_description_content_type="text/markdown",
    url="https://github.com/Mogui-Hao/PygameNode",  # 项目主页，如GitHub地址
    packages=find_packages(),  # 自动发现你的包，无需手动列出
    classifiers=[  # 分类器，帮助用户在PyPI上找到你的库
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Buildout :: Extension",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.10",  # 指定支持的Python版本
    install_requires=[  # 列出你的库所依赖的第三方包
        "pygame~=2.6.1",
    ],
    # 如果库包含可执行命令，可以这样配置
    entry_points={},
)