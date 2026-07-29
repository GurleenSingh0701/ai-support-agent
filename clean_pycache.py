import os
import shutil
import stat
from pathlib import Path


def remove_readonly(func, path, exc_info):
    """Clear the read-only attribute and retry the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clean_pycache(root_dir: str = "."):
    """
    Recursively delete all __pycache__ directories and .pyc/.pyo files
    starting from root_dir.
    """
    root_path = Path(root_dir).resolve()
    print(f"Scanning for pycache files in: {root_path}")

    dirs_removed = 0
    files_removed = 0
    bytes_freed = 0

    # Walk directory tree
    for current_root, dirs, files in os.walk(root_path, topdown=False):
        # 1. Remove .pyc and .pyo files not in __pycache__
        for file in files:
            if file.endswith((".pyc", ".pyo")):
                file_path = Path(current_root) / file
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    files_removed += 1
                    bytes_freed += size
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete file {file_path}: {e}")

        # 2. Remove __pycache__ directories
        for dir_name in dirs:
            if dir_name == "__pycache__":
                dir_path = Path(current_root) / dir_name
                try:
                    # Calculate size before removal
                    for dirpath, _, filenames in os.walk(dir_path):
                        for f in filenames:
                            fp = Path(dirpath) / f
                            if fp.is_file():
                                bytes_freed += fp.stat().st_size
                    
                    shutil.rmtree(dir_path, onerror=remove_readonly)
                    dirs_removed += 1
                    print(f"Deleted directory: {dir_path}")
                except Exception as e:
                    print(f"Failed to delete directory {dir_path}: {e}")

    mb_freed = bytes_freed / (1024 * 1024)
    print("\n--- Cleanup Summary ---")
    print(f"__pycache__ directories removed: {dirs_removed}")
    print(f"Standalone .pyc/.pyo files removed: {files_removed}")
    print(f"Total space freed: {mb_freed:.2f} MB ({bytes_freed} bytes)")


if __name__ == "__main__":
    clean_pycache()
