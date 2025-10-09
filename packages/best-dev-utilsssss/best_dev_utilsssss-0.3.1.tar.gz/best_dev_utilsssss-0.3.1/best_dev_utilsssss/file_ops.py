import os
import fnmatch
from pathlib import Path
from typing import List, Dict
import datetime


class FileOperations:
    @staticmethod
    def directory_tree(path: str = ".", max_depth: int = 3, show_hidden: bool = False) -> str:
        def build_tree(dir_path: Path, depth: int = 0, prefix: str = "") -> str:
            if depth > max_depth:
                return ""

            tree = ""
            try:
                items = sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

                for i, item in enumerate(items):
                    if not show_hidden and item.name.startswith('.'):
                        continue

                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    next_prefix = "    " if is_last else "│   "

                    if item.is_dir():
                        tree += f"{prefix}{current_prefix}📁 {item.name}/\n"
                        tree += build_tree(item, depth + 1, prefix + next_prefix)
                    else:
                        size = FileOperations._format_file_size(item.stat().st_size)
                        tree += f"{prefix}{current_prefix}📄 {item.name} ({size})\n"

            except PermissionError:
                tree += f"{prefix}└── [Access Denied]\n"

            return tree

        return build_tree(Path(path))

    @staticmethod
    def _format_file_size(size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @staticmethod
    def find_files(pattern: str, path: str = ".", recursive: bool = True) -> List[str]:
        path_obj = Path(path)

        if recursive:
            files = [str(p) for p in path_obj.rglob('*') if p.is_file() and fnmatch.fnmatch(p.name, pattern)]
        else:
            files = [str(p) for p in path_obj.glob('*') if p.is_file() and fnmatch.fnmatch(p.name, pattern)]

        return files

    @staticmethod
    def get_file_info(filepath: str) -> Dict:
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        stat = path.stat()

        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": FileOperations._format_file_size(stat.st_size),
            "size_bytes": stat.st_size,
            "created": datetime.datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "extension": path.suffix.lower(),
            "parent": str(path.parent)
        }

    @staticmethod
    def count_files_by_type(path: str = ".") -> Dict[str, int]:
        path_obj = Path(path)
        extensions = {}

        for file_path in path_obj.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower() or 'no extension'
                extensions[ext] = extensions.get(ext, 0) + 1

        return dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True))