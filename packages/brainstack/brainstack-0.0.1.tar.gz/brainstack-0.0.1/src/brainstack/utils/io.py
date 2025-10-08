import hashlib
import os
from pathlib import Path
from typing import Union, Callable
import numpy as np
from PIL import Image
from functools import lru_cache, wraps

def load_text(s: Union[str, Path]) -> str:
    """Load text from a file path or return the input string as-is.

    Args:
        s: File path (str or Path) or raw text string.

    Returns:
        Text content as a string.
    """
    if isinstance(s, (str, Path)) and os.path.exists(s):
        with open(s, 'r', encoding='utf-8') as f:
            return f.read()
    return str(s)

def load_image(path: Union[str, Path]) -> np.ndarray:
    """Load an image from a path and return as a numpy array (H,W,3) in RGB.

    Args:
        path: Path to the image file.

    Returns:
        Numpy array of shape (height, width, 3) with dtype uint8.

    Raises:
        FileNotFoundError: If the image path does not exist.
        ValueError: If the image cannot be converted to RGB.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at {path}")
    img = Image.open(path).convert('RGB')
    return np.array(img, dtype=np.uint8)

def file_sha1(path: Union[str, Path]) -> str:
    """Compute SHA1 hash of a file's contents.

    Args:
        path: Path to the file.

    Returns:
        Hexadecimal SHA1 hash string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found at {path}")
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def lru_cache_bytes(maxsize: int = 64) -> Callable:
    """Decorator to cache functions returning bytes, with LRU eviction.

    Args:
        maxsize: Maximum number of results to cache.

    Returns:
        Decorator that caches function outputs.
    """
    def decorator(func: Callable) -> Callable:
        @lru_cache(maxsize=maxsize)
        def wrapper(*args, **kwargs) -> bytes:
            result = func(*args, **kwargs)
            if not isinstance(result, bytes):
                raise ValueError(f"Function {func.__name__} must return bytes")
            return result
        return wraps(func)(wrapper)
    return decorator

def ensure_dir(path: Union[str, Path]) -> None:
    """Create directory if it does not exist.

    Args:
        path: Directory path to ensure.
    """
    Path(path).mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    # Test IO utilities
    import tempfile

    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write("Hello, brainstack!")
        temp_file = f.name

    # Test load_text and file_sha1
    text = load_text(temp_file)
    sha1 = file_sha1(temp_file)
    print(f"Loaded text: {text}")
    print(f"SHA1: {sha1}")

    # Create a dummy image (1x1 RGB)
    dummy_img = np.array([[[255, 0, 0]]], dtype=np.uint8)
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.png') as f:
        Image.fromarray(dummy_img).save(f.name)
        temp_img = f.name

    # Test load_image
    img_array = load_image(temp_img)
    print(f"Image shape: {img_array.shape}")

    # Clean up
    os.unlink(temp_file)
    os.unlink(temp_img)