import os
import platform
from pathlib import Path

DEFAULT_SCAN_PATHS = {
    "Windows": str(Path.home()),
    "Darwin": str(Path.home() / "Documents"),
    "Linux": "/sdcard" if ("ANDROID_ROOT" in os.environ or "com.termux" in os.environ.get("PREFIX", "")) else str(Path.home())
}

COLOR_CODES = {
    'header': '\033[1;35m',
    'item': '\033[1;32m',
    'size': '\033[33m',
    'total': '\033[1;36m',
    'reset': '\033[0m'
}
