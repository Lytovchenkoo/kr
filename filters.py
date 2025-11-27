# -*- coding: utf-8 -*-
from PIL import Image, ImageEnhance, ImageFilter

def to_grayscale(image):
    """Перетворює зображення у відтінки сірого"""
    return image.convert('L').convert('RGB')

def blur_image(image, radius=2):
    """Розмиває зображення"""
    return image.filter(ImageFilter.GaussianBlur(radius))

def adjust_brightness(image, factor=1.2):
    """Змінює яскравість (factor > 1 — яскравіше, < 1 — темніше)"""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def adjust_contrast(image, factor=1.3):
    """Змінює контрастність"""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def sharpen_image(image):
    """Підвищує різкість зображення"""
    return image.filter(ImageFilter.SHARPEN)
