"""
quillai_filescanner - A comprehensive file system scanner
"""

from .scanner import FileScanner, DisplayManager
from .categories import FILE_CATEGORIES, CATEGORY_TO_EXTS, get_other_extensions
from .utils import human_size, get_default_scan_path, get_disk_usage
from .config import DEFAULT_SCAN_PATHS, COLOR_CODES

__version__ = "1.0.4"
__author__ = "Quillai Mohammed"

__all__ = [
    'FileScanner',
    'DisplayManager', 
    'FILE_CATEGORIES',
    'CATEGORY_TO_EXTS',
    'get_other_extensions',
    'human_size',
    'get_default_scan_path',
    'get_disk_usage',
    'DEFAULT_SCAN_PATHS',
    'COLOR_CODES'
]
