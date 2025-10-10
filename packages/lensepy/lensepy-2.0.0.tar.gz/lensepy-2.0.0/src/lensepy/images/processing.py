# -*- coding: utf-8 -*-
"""*procesing.py* file.

*procesing* file contains image processes.

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""
import sys
import cv2
import numpy as np
from PyQt6.QtGui import QImage

def get_cross_kernel(size: int) -> np.ndarray:
    """
    Return a cross kernel.
    :param size: Size of the kernel.
    :return: Kernel.
    """
    return cv2.getStructuringElement(cv2.MORPH_CROSS, (size, size))


def get_rect_kernel(size: int) -> np.ndarray:
    """
    Return a rectangular kernel.
    :param size: Size of the kernel.
    :return: Kernel.
    """
    return cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))


def get_ellip_kernel(size: int) -> np.ndarray:
    """
    Return a rectangular kernel.
    :param size: Size of the kernel.
    :return: Kernel.
    """
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))


def erode_image(array: np.ndarray, kernel: np.ndarray):
    """
    Return an eroded image.
    :param array: Original image.
    :param kernel: Kernel to use for erosion.
    :return: Modified image.
    """
    return cv2.erode(array, kernel, iterations=1)


def dilate_image(array: np.ndarray, kernel: np.ndarray):
    """
    Return a dilated image.
    :param array: Original image.
    :param kernel: Kernel to use for dilation.
    :return: Modified image.
    """
    return cv2.dilate(array, kernel, iterations=1)


def opening_image(array: np.ndarray, kernel: np.ndarray):
    """
    Return an image after an opening process.
    :param array: Original image.
    :param kernel: Kernel to use for opening.
    :return: Modified image.
    """
    return cv2.morphologyEx(array, cv2.MORPH_OPEN, kernel)


def closing_image(array: np.ndarray, kernel: np.ndarray):
    """
    Return an image after an opening process.
    :param array: Original image.
    :param kernel: Kernel to use for opening.
    :return: Modified image.
    """
    return cv2.morphologyEx(array, cv2.MORPH_CLOSE, kernel)

def contrast_brightness_image(array: np.ndarray, contrast: float = 1, brightness: int = 0):
    """
    Return an image after contrast/brightness modification.
    :param array: Original image.
    :param contrast: Contrast value from 0 to 2.
    :param brightness: Brightness value in pixel.
    :return: Modified image.
    """
    return cv2.convertScaleAbs(array, alpha=contrast, beta=brightness)


def gradient_image(array: np.ndarray, kernel: np.ndarray):
    """
    Return an image after a gradient process.
    :param array: Original image.
    :param kernel: Kernel to use for gradient.
    :return: Modified image.
    """
    return cv2.morphologyEx(array, cv2.MORPH_GRADIENT, kernel)