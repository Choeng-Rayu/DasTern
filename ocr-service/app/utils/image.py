"""
Image Utilities
Helper functions for image loading and processing
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Union, Tuple
import io
from ..core.logger import logger


def load_image_from_path(path: Union[str, Path]) -> np.ndarray:
    """
    Load image from file path
    
    Args:
        path: Path to image file
        
    Returns:
        Image as numpy array (BGR format)
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image can't be loaded
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    
    image = cv2.imread(str(path))
    
    if image is None:
        raise ValueError(f"Failed to load image: {path}")
    
    logger.debug(f"Loaded image: {path}, shape: {image.shape}")
    
    return image


def load_image_from_bytes(data: bytes) -> np.ndarray:
    """
    Load image from bytes
    
    Args:
        data: Image data as bytes
        
    Returns:
        Image as numpy array (BGR format)
        
    Raises:
        ValueError: If image can't be decoded
    """
    nparr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Failed to decode image from bytes")
    
    logger.debug(f"Decoded image from bytes, shape: {image.shape}")
    
    return image


def save_image(image: np.ndarray, path: Union[str, Path]) -> bool:
    """
    Save image to file
    
    Args:
        image: Image to save
        path: Output path
        
    Returns:
        True if successful
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    success = cv2.imwrite(str(path), image)
    
    if success:
        logger.debug(f"Saved image to: {path}")
    else:
        logger.error(f"Failed to save image to: {path}")
    
    return success


def get_image_info(image: np.ndarray) -> dict:
    """
    Get basic image information
    
    Args:
        image: Input image
        
    Returns:
        Dictionary with image info
    """
    if len(image.shape) == 3:
        height, width, channels = image.shape
    else:
        height, width = image.shape
        channels = 1
    
    return {
        "width": width,
        "height": height,
        "channels": channels,
        "dtype": str(image.dtype),
        "size_bytes": image.nbytes
    }


def resize_image(
    image: np.ndarray,
    max_width: int = 2000,
    max_height: int = 2000
) -> Tuple[np.ndarray, float]:
    """
    Resize image if too large
    
    Args:
        image: Input image
        max_width: Maximum width
        max_height: Maximum height
        
    Returns:
        Tuple of (resized image, scale factor)
    """
    height, width = image.shape[:2]
    
    scale = 1.0
    
    if width > max_width:
        scale = max_width / width
    if height > max_height:
        scale = min(scale, max_height / height)
    
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        logger.debug(f"Resized image from {width}x{height} to {new_width}x{new_height}")
    
    return image, scale


def image_to_bytes(image: np.ndarray, format: str = ".png") -> bytes:
    """
    Convert image to bytes
    
    Args:
        image: Input image
        format: Image format (e.g., ".png", ".jpg")
        
    Returns:
        Image as bytes
    """
    success, buffer = cv2.imencode(format, image)
    if not success:
        raise ValueError(f"Failed to encode image as {format}")
    return buffer.tobytes()
