import os
import platform
from collections import defaultdict
from pathlib import Path

from categories import FILE_CATEGORIES, KNOWN_EXTS, get_other_extensions
from utils import human_size, get_disk_usage

class FileScanner:
    def __init__(self):
        self.results = defaultdict(lambda: {'count': 0, 'size': 0})
        self.all_paths = []
        self.total_scanned = 0
        self.total_bytes = 0

    def scan(self, root_path):
        self.results.clear()
        self.all_paths.clear()
        self.total_scanned = 0
        self.total_bytes = 0

        self._scan_recursive(Path(root_path))
        return dict(self.results), self.total_scanned, self.total_bytes, self.all_paths.copy()

    def _scan_recursive(self, current_path):
        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            self._process_file(entry)
                        elif entry.is_dir(follow_symlinks=False):
                            self._scan_recursive(entry.path)
                    except (OSError, ValueError):
                        continue
        except (OSError, PermissionError):
            pass

    def _process_file(self, entry):
        self.total_scanned += 1
        _, ext = os.path.splitext(entry.name)
        ext = ext.lower()

        try:
            stat = entry.stat()
            size = stat.st_size
            self.results[ext]['count'] += 1
            self.results[ext]['size'] += size
            self.total_bytes += size
            self.all_paths.append((entry.path, ext))
        except (OSError, ValueError):
            pass

    def get_category_stats(self, category_exts, results=None):
        if results is None:
            results = self.results

        count = 0
        size = 0
        for ext in category_exts:
            data = results.get(ext, {'count': 0, 'size': 0})
            count += data['count']
            size += data['size']
        return count, size

class DisplayManager:
    def __init__(self, use_color=True):
        self.use_color = use_color

    def display_category(self, category_name, extensions, results, total_scanned_size):
        if self.use_color:
            header = f"\n\033[1;35m{'='*60}\n📁 {category_name.upper()}\n{'='*60}\033[0m"
            item_prefix = "\033[1;32m• "
            size_color = "\033[33m"
            total_line = "\033[1;36m"
            reset = "\033[0m"
        else:
            header = f"\n{'='*60}\n📁 {category_name.upper()}\n{'='*60}"
            item_prefix = "• "
            size_color = ""
            total_line = ""
            reset = ""

        print(header)

        cat_count = 0
        cat_size = 0
        for ext in extensions:
            data = results.get(ext, {'count': 0, 'size': 0})
            if data['count'] > 0:
                cat_count += data['count']
                cat_size += data['size']
                desc = FILE_CATEGORIES.get(ext, f"Unknown ({ext})")
                pct_of_scanned = (data['size'] / total_scanned_size * 100) if total_scanned_size > 0 else 0
                print(f"{item_prefix}{desc:<25} {size_color}[{data['count']:>8} files | {human_size(data['size']):>8} | {pct_of_scanned:>5.1f}%]{reset}")

        if cat_count > 0:
            pct_cat = (cat_size / total_scanned_size * 100) if total_scanned_size > 0 else 0
            print(f"{total_line}{'─'*50}")
            print(f"Total: {cat_count:>35} files | {human_size(cat_size):>8} | {pct_cat:>5.1f}%{reset}")

    def display_header(self, scan_path, disk_info):
        if self.use_color:
            print(f"\033[1;34m{'='*70}")
            print(f"🖥️  OS: {platform.system()}")
            print(f"📂 Scanning: {scan_path}")
            if disk_info:
                print(f"💽 Partition: {human_size(disk_info['total'])} total")
            print('='*70 + '\033[0m')

    def display_summary(self, classified_files, classified_size, total_files, total_scanned_size, disk_info):
        if self.use_color:
            bar = "\033[1;34m" + "="*70 + "\033[0m"
        else:
            bar = "="*70

        print(f"\n{bar}")
        print(f"📊 CLASSIFIED FILES: {classified_files:>12} | {human_size(classified_size)}")
        print(f"📁 TOTAL SCANNED:    {total_files:>12} | {human_size(total_scanned_size)}")
        if total_scanned_size > 0:
            pct = classified_size / total_scanned_size * 100
            print(f"🎯 CLASSIFIED:       {pct:>5.1f}% of scanned data")
        if disk_info:
            print(f"💽 PARTITION TOTAL:  {human_size(disk_info['total'])}")
        print(bar)
