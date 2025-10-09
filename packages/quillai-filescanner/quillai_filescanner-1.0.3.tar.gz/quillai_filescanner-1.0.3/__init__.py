__version__ = "1.0.0"
__author__ = "File Scanner Team"

from scanner import FileScanner
from categories import FILE_CATEGORIES, CATEGORY_TO_EXTS
from utils import human_size, get_default_scan_path

__all__ = ['FileScanner', 'FILE_CATEGORIES', 'CATEGORY_TO_EXTS', 'human_size', 'get_default_scan_path']
