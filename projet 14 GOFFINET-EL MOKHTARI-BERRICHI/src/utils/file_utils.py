import os

def ensure_dir(path: str):
    """Create directory if it does not exist"""
    os.makedirs(path, exist_ok=True)
