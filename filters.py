# -*- coding: utf-8 -*-
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

def to_grayscale(image):
    """Перетворює зображення у відтінки сірого"""
    # Конвертуємо через L (Grayscale), потім назад в RGBA
    return image.convert('L').convert('RGBA')

def blur_image(image, radius=2):
    """Розмиває зображення"""
    return image.filter(ImageFilter.GaussianBlur(radius))

def adjust_sharpness(image, factor=1.0):
    """Змінює різкість. factor < 1.0 -> Розмиття; factor > 1.0 -> Різкість"""
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)

def adjust_brightness(image, factor=1.0):
    """Гамма-корекція яскравості (зберігає деталі)"""
    if factor == 0: return image
    gamma = 1.0 / factor
    table = [int(255 * (i / 255.0) ** gamma) for i in range(256)] * 3
    
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        adjusted_rgb = rgb_image.point(table)
        return Image.merge('RGBA', (*adjusted_rgb.split(), a))
    else:
        return image.point(table)

def adjust_contrast(image, factor=1.3):
    """Змінює контрастність"""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def adjust_saturation(image, factor=1.0):
    """Змінює насиченість кольорів"""
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def adjust_color_balance(image, r=1.0, g=1.0, b=1.0):
    """Баланс кольорів (множники для каналів)"""
    if image.mode == 'RGBA':
        source = image.split()
        r_c, g_c, b_c = source[0], source[1], source[2]
        a = source[3]
    else:
        r_c, g_c, b_c = image.split()
        a = None

    r_c = r_c.point(lambda i: i * r)
    g_c = g_c.point(lambda i: i * g)
    b_c = b_c.point(lambda i: i * b)

    if a:
        return Image.merge('RGBA', (r_c, g_c, b_c, a))
    return Image.merge('RGB', (r_c, g_c, b_c))

def auto_levels(image):
    """Автоматичне вирівнювання гістограми (Levels)"""
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        rgb = Image.merge('RGB', (r, g, b))
        rgb = ImageOps.autocontrast(rgb)
        return Image.merge('RGBA', (*rgb.split(), a))
    return ImageOps.autocontrast(image)