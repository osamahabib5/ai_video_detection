#!/usr/bin/env python3
"""
Display complete project structure
"""
import os
from pathlib import Path

def print_tree(directory, prefix="", max_depth=5, current_depth=0, exclude_dirs={'.git', '__pycache__', '.pytest_cache', 'venv', 'env', '.venv'}):
    """Print directory tree structure"""
    if current_depth >= max_depth:
        return
    
    try:
        items = sorted(os.listdir(directory))
    except PermissionError:
        return
    
    # Filter directories
    items = [item for item in items if item not in exclude_dirs and not item.startswith('.')]
    
    for i, item in enumerate(items):
        path = os.path.join(directory, item)
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item}")
        
        if os.path.isdir(path) and item not in exclude_dirs:
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(path, next_prefix, max_depth, current_depth + 1, exclude_dirs)


if __name__ == '__main__':
    root = Path(__file__).parent
    print("AI Video Detection System - Project Structure")
    print("=" * 50)
    print(str(root) + "/")
    print_tree(str(root))
