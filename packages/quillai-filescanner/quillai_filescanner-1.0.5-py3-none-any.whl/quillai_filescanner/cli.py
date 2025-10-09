import argparse
import sys
import platform

from .scanner import FileScanner, DisplayManager
from .categories import CATEGORY_TO_EXTS, get_other_extensions
from .utils import get_default_scan_path, get_disk_usage

def main():
    parser = create_parser()
    args = parser.parse_args()

    scan_path = args.path or get_default_scan_path()
    use_color = not (args.plain or args.list) and sys.stdout.isatty()

    scanner = FileScanner()
    display = DisplayManager(use_color=use_color)

    results, total_files, total_scanned_size, all_paths = scanner.scan(scan_path)
    disk_info = get_disk_usage(scan_path)

    target_exts = get_target_extensions(args.type, results)
    category_name = get_category_name(args.type)

    if args.list:
        handle_list_mode(all_paths, target_exts)
        return

    handle_display_mode(args, results, total_scanned_size, target_exts, category_name,
                       display, scan_path, disk_info, total_files)

def create_parser():
    parser = argparse.ArgumentParser(
        description="Unix-style file scanner. Use -l to list paths, -t to filter by type.",
        epilog="Categories: audio, video, images, docs, archives, code, system, other, all"
    )
    parser.add_argument("path", nargs="?", default=None, help="Path to scan")
    parser.add_argument("-t", "--type", choices=[
        'audio', 'video', 'images', 'docs', 'archives', 'code', 'system', 'other', 'all'
    ], default='all', help="Filter by file category (default: all)")
    parser.add_argument("-l", "--list", action="store_true", help="List file paths (respects -t)")
    parser.add_argument("--plain", action="store_true", help="Plain text output (no colors)")
    return parser

def get_target_extensions(scan_type, results):
    if scan_type == 'all':
        return set(results.keys())
    elif scan_type == 'other':
        return set(get_other_extensions(results.keys()))
    else:
        return set(CATEGORY_TO_EXTS[scan_type])

def get_category_name(scan_type):
    names = {
        'all': "ALL FILES",
        'other': "OTHER FILES"
    }
    return names.get(scan_type, f"{scan_type.upper()} FILES")

def handle_list_mode(all_paths, target_exts):
    for path, ext in all_paths:
        if ext in target_exts:
            print(path)

def handle_display_mode(args, results, total_scanned_size, target_exts, category_name,
                       display, scan_path, disk_info, total_files):
    display.display_header(scan_path, disk_info)

    if args.type == 'all':
        display_all_categories(results, total_scanned_size, display)
    elif args.type == 'other':
        display_other_category(results, total_scanned_size, display)
    else:
        display.display_category(category_name, CATEGORY_TO_EXTS[args.type],
                               results, total_scanned_size)

    classified_files, classified_size = calculate_classified_stats(args.type, results, target_exts)
    display.display_summary(classified_files, classified_size, total_files,
                          total_scanned_size, disk_info)

def display_all_categories(results, total_scanned_size, display):
    display.display_category("🎵 AUDIO FILES", CATEGORY_TO_EXTS['audio'], results, total_scanned_size)
    display.display_category("🎬 VIDEO FILES", CATEGORY_TO_EXTS['video'], results, total_scanned_size)
    display.display_category("🖼️  IMAGES", CATEGORY_TO_EXTS['images'], results, total_scanned_size)
    display.display_category("📄 DOCUMENTS", CATEGORY_TO_EXTS['docs'], results, total_scanned_size)
    display.display_category("📦 ARCHIVES", CATEGORY_TO_EXTS['archives'], results, total_scanned_size)
    display.display_category("💻 CODE & SCRIPTS", CATEGORY_TO_EXTS['code'], results, total_scanned_size)
    display.display_category("⚙️  SYSTEM & APPS", CATEGORY_TO_EXTS['system'], results, total_scanned_size)

    from .categories import get_other_extensions
    other_exts = get_other_extensions(results.keys())
    if other_exts:
        display.display_category("📋 OTHER FILES", other_exts, results, total_scanned_size)

def display_other_category(results, total_scanned_size, display):
    from .categories import get_other_extensions
    other_exts = get_other_extensions(results.keys())
    if other_exts:
        display.display_category("📋 OTHER FILES", other_exts, results, total_scanned_size)
    else:
        print("\nNo unknown file types found.")

def calculate_classified_stats(scan_type, results, target_exts):
    if scan_type == 'all':
        classified_files = sum(data['count'] for data in results.values())
        classified_size = sum(data['size'] for data in results.values())
    elif scan_type == 'other':
        classified_files = sum(results.get(ext, {'count': 0})['count'] for ext in target_exts)
        classified_size = sum(results.get(ext, {'size': 0})['size'] for ext in target_exts)
    else:
        classified_files = sum(results.get(ext, {'count': 0})['count'] for ext in target_exts)
        classified_size = sum(results.get(ext, {'size': 0})['size'] for ext in target_exts)

    return classified_files, classified_size

if __name__ == "__main__":
    main()
