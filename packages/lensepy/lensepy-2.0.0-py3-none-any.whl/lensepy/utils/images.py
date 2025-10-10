import cv2
import numpy as np

def resize_image_ratio(pixels: np.ndarray, new_height: int, new_width: int) -> np.ndarray:
    """Create a new array with a different size, with the same aspect ratio.

    :param pixels: Array of pixels to resize
    :type pixels: np.ndarray
    :param new_height: New height of the image.
    :type new_height: int
    :param new_width: New width of the image.
    :type new_width: int

    :return: A resized image.
    :rtype: np.ndarray
    """
    height, width = pixels.shape[:2]
    aspect_ratio = width / height

    # Calculate new size with same aspect_ratio
    n_width = new_width
    n_height = int(n_width / aspect_ratio)
    if n_height > new_height:
        n_height = new_height
        n_width = int(n_height * aspect_ratio)
    else:
        n_width = new_width
        n_height = int(n_width / aspect_ratio)
    resized_array = cv2.resize(pixels, (n_width, n_height))
    return resized_array

def imread_rgb(path: str):
    """
    Open an image from a file, after RGB conversion.
    :param path:    Path to image.
    :return:        np.ndarray RGB image.
    """
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    bits_depth = img.dtype.itemsize * 8
    if img is None:
        raise ValueError(f"Invalid path : {path}")
    if img.ndim == 2:
        # Déjà en gris → on garde tel quel
        return img, bits_depth
    if img.ndim == 3:
        if img.shape[2] == 3:
            # Conversion BGR → RGB
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 8
        elif img.shape[2] == 4:
            # Conversion BGRA → RGBA
            return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA), 8
    return img, bits_depth