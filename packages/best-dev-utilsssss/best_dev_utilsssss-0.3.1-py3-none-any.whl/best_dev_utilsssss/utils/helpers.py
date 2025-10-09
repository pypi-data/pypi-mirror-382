def format_bytes(size: int) -> str:
    try:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    except Exception:
        return f"{size}"

def validate_path(path: str) -> bool:
    from pathlib import Path
    try:
        Path(path)
        return True
    except:
        return False