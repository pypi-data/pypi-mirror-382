FILE_CATEGORIES = {
    '.mp3': 'Music', '.m4a': 'Hidden Music', '.wav': 'WAV Audio', '.flac': 'FLAC Audio',
    '.aac': 'AAC Audio', '.ogg': 'OGG Audio', '.wma': 'Windows Media Audio',
    '.mp4': 'Video', '.avi': 'AVI Video', '.mkv': 'MKV Video', '.mov': 'MOV Video',
    '.wmv': 'Windows Media Video', '.flv': 'FLV Video', '.webm': 'WebM Video',
    '.3gp': '3GP Mobile Video', '.mpeg': 'MPEG Video', '.mpg': 'MPG Video',
    '.jpg': 'Images', '.jpeg': 'JPEG Images', '.png': 'Transparent Images',
    '.gif': 'GIF Images', '.bmp': 'Bitmap Images', '.tiff': 'TIFF Images',
    '.svg': 'SVG Vector Images', '.webp': 'WebP Images', '.ico': 'Icon Files',
    '.raw': 'RAW Camera Images', '.pdf': 'PDF Documents', '.doc': 'Word Documents',
    '.docx': 'Word Documents', '.xls': 'Excel Spreadsheets', '.xlsx': 'Excel Spreadsheets',
    '.ppt': 'PowerPoint Presentations', '.pptx': 'PowerPoint Presentations',
    '.txt': 'Text Files', '.rtf': 'Rich Text Files', '.odt': 'OpenDocument Text',
    '.zip': 'ZIP Archives', '.rar': 'RAR Archives', '.7z': '7-Zip Archives',
    '.tar': 'TAR Archives', '.gz': 'GZ Compressed', '.iso': 'Disk Images',
    '.py': 'Python Files', '.java': 'Java Files', '.cpp': 'C++ Files', '.c': 'C Files',
    '.h': 'Header Files', '.cs': 'C# Files', '.php': 'PHP Files', '.html': 'HTML Files',
    '.htm': 'HTML Files', '.css': 'CSS Files', '.js': 'JavaScript Files',
    '.ts': 'TypeScript Files', '.json': 'JSON Files', '.xml': 'XML Files',
    '.sql': 'SQL Files', '.swift': 'Swift Files', '.kt': 'Kotlin Files',
    '.rb': 'Ruby Files', '.go': 'Go Files', '.rs': 'Rust Files',
    '.exe': 'Windows Executables', '.apk': 'Android Applications',
    '.deb': 'Debian Packages', '.rpm': 'RPM Packages', '.dmg': 'Mac Disk Images',
    '.msi': 'Windows Installers', '.bat': 'Batch Files', '.sh': 'Shell Scripts',
    '.ps1': 'PowerShell Scripts', '.db': 'Database Files', '.sqlite': 'SQLite Databases',
    '.mdb': 'Access Databases', '.ttf': 'TrueType Fonts', '.otf': 'OpenType Fonts',
    '.woff': 'Web Fonts', '.woff2': 'Web Fonts 2', '.epub': 'EPUB E-books',
    '.mobi': 'Mobi E-books', '.azw': 'Amazon Kindle', '.ini': 'Configuration Files',
    '.cfg': 'Config Files', '.conf': 'Config Files', '.yml': 'YAML Files',
    '.yaml': 'YAML Files', '.torrent': 'Torrent Files', '.log': 'Log Files',
    '.csv': 'CSV Data Files', '.dll': 'Dynamic Libraries', '.lib': 'Static Libraries'
}

CATEGORY_TO_EXTS = {
    'audio': ['.mp3', '.m4a', '.wav', '.flac', '.aac', '.ogg', '.wma'],
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.3gp', '.mpeg', '.mpg'],
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico', '.raw'],
    'docs': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt'],
    'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.iso'],
    'code': ['.py', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.html', '.htm', '.css',
             '.js', '.ts', '.json', '.xml', '.sql', '.swift', '.kt', '.rb', '.go', '.rs'],
    'system': ['.exe', '.apk', '.deb', '.rpm', '.dmg', '.msi', '.bat', '.sh', '.ps1'],
}

KNOWN_EXTS = set(ext for exts in CATEGORY_TO_EXTS.values() for ext in exts)

def get_other_extensions(all_extensions):
    return [ext for ext in all_extensions if ext not in KNOWN_EXTS]
