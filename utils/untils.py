# 动态获取资源
import os
import sys


def get_path(relative_path: str) -> str:
    """兼容 PyInstaller 的资源路径获取方法"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包环境下
        base_path = sys._MEIPASS
    else:
        # 开发环境下
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
