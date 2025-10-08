from __future__ import annotations

import os
import platform
import shutil
import sys


def get_terminal_size() -> tuple[int, int]:
    """获取 Console 的宽高

    ### Refs

    - https://github.com/willmcgugan/rich/blob/e5246436cd75de32f3436cc88d6e4fdebe13bd8d/rich/console.py#L918-L951
    """

    width: int | None = None
    height: int | None = None
    if platform.system() == "Windows":
        width, height = shutil.get_terminal_size()
    else:
        try:
            width, height = os.get_terminal_size(sys.stdin.fileno())
        except (AttributeError, ValueError, OSError):
            try:
                width, height = os.get_terminal_size(sys.stdout.fileno())
            except (AttributeError, ValueError, OSError):
                pass

    width = width or 80
    height = height or 25
    return (width, height)
