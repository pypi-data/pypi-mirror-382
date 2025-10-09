import os
import platform
import shutil
from pathlib import Path
from config import DEFAULT_SCAN_PATHS

def human_size(bytes_val):
    if bytes_val == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes_val >= 1024.0 and i < len(units) - 1:
        bytes_val /= 1024.0
        i += 1
    return f"{bytes_val:.1f} {units[i]}"

def get_default_scan_path():
    system = platform.system()
    return DEFAULT_SCAN_PATHS.get(system, ".")

def get_disk_usage(path):
    try:
        disk = shutil.disk_usage(path)
        return {
            'total': disk.total,
            'used': disk.total - disk.free,
            'free': disk.free
        }
    except Exception:
        return None
