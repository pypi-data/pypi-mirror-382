# -*- coding: utf-8 -*-
"""*widget_image_display.py* file.

*images* file, from supop_images directory,
that contains functions to process images.

.. module:: supop_images.images
   :synopsis: To complete

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""
import sys
import cv2
import numpy as np
from PyQt6.QtGui import QImage


def zoom_array(im_array: np.ndarray, zoom_factor: int = 1):
    """Zoom inside an array in 2D.
    :param im_array: Array to change.
    :param zoom_factor: Zoom factor.
    :return: Modified array.
    """
    return np.repeat(np.repeat(im_array, zoom_factor, axis=0), zoom_factor, axis=1)


def find_mask_limits(mask: np.ndarray) -> tuple[int, int]:
    """Find bounding box of a mask.
    :param mask: Mask to process.
    :return: Boundaries of the mask. (y1, x1) and (y2, x2)
    """
    active_positions = np.argwhere(mask)
    if active_positions.size == 0:
        return None

    top_left = active_positions.min(axis=0)
    bottom_right = active_positions.max(axis=0)

    return top_left, bottom_right


def crop_images(images, crop_size: tuple[int, int] = (256, 256),
                crop_position: tuple[int, int] = (0, 0)):
    """Crop a list of images.
    :param images: List of images to crop.
    :param crop_size: Size in the image to crop.
    :param crop_position: Position of the crop. Top left corner of the crop (x, y).
    :return: List of cropped images.
    """
    cropped_images = []

    for img in images:
        crop_height, crop_width = crop_size
        crop_x, crop_y = crop_position

        end_x = crop_x + crop_width
        end_y = crop_y + crop_height
        cropped_img = img[crop_y:end_y, crop_x:end_x]
        cropped_images.append(cropped_img)

    return cropped_images



def resize_image(im_array: np.ndarray,
                 new_width: int,
                 new_height: int) -> np.ndarray:
    """Resize array containing image at a new size.

    :param im_array: Initial array to resize.
    :type im_array: numpy.ndarray
    :param new_width: Width of the new array.
    :type new_width: int
    :param new_height: Height of the new array.
    :type new_height: int
    :return: Resized array.
    :rtype: numpy.ndarray

    """
    image_rows, image_cols = im_array.shape[:2]
    row_ratio = new_width / float(image_rows)
    col_ratio = new_height / float(image_cols)
    ratio = min(row_ratio, col_ratio)
    resized_image = cv2.resize(im_array,
                               dsize=(new_width, new_height),
                               fx=ratio, fy=ratio,
                               interpolation=cv2.INTER_CUBIC)
    return resized_image

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

def array_to_qimage(array: np.ndarray) -> QImage:
    """Transcode an array to a QImage.
    :param array: Array containing image data.
    :type array: numpy.ndarray
    :return: Image to display.
    :rtype: QImage
    """
    shape_size = len(array.shape)
    if shape_size == 2:
        height, width = array.shape
        bytes_per_line = width  # only in 8 bits gray
        return QImage(array, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
    else:
        height, width, _ = array.shape
        bytes_per_line = 3 * width  # only in 8 bits gray
        return QImage(array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)


def quantize_image(image: np.ndarray, bits_depth: int, init_depth: int = 8):
    """Change the quantization of an array.
    The initial bits depth of the image must be 8 bits.
    :param image: Array containing the image.
    :param bits_depth: Final bits depth.
    :param init_depth: Initial bits depth.
    :return: Array with the result, shape is the same as the initial array.
    """
    quantized_image = (image >> (init_depth - bits_depth))
    return quantized_image


def downsample_and_upscale(image, factor):
    """
    Downsample an image.
    :param image: Array containing the image.
    :param factor: Factor of downsampling.
    :return: 2 arrays: Small image, Same size image but with interpolation.
    """
    original_size = (image.shape[1], image.shape[0])
    # Downsample
    small_image = cv2.resize(image, (original_size[0] // factor, original_size[1] // factor), interpolation=cv2.INTER_AREA)
    # Upscale back to original size
    upscaled_image = cv2.resize(small_image, original_size, interpolation=cv2.INTER_NEAREST)
    return small_image, upscaled_image


def zoom_image(image: np.ndarray, zoom_factor: float) -> np.ndarray:
    """
    Return a zoomed image.
    :param image: Image to display with a zoom.
    :param zoom_factor: Value of the zoom.
    :return: Zoomed image.
    """
    return np.repeat(np.repeat(image, zoom_factor, axis=0), zoom_factor, axis=1)