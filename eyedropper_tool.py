# -*- coding: utf-8 -*-
"""
Модуль инструмента "Пипетка" (Eyedropper) для выбора цвета из изображения
"""

from PIL import Image
import PySimpleGUI as sg


class EyedropperTool:
    """
    Инструмент пипетки для выбора цвета пикселя из изображения
    """
    
    def __init__(self):
        self.active = False
        self.selected_color = (255, 0, 0, 255)  # По умолчанию красный (R, G, B, A)
    
    def activate(self):
        """Активировать инструмент пипетки"""
        self.active = True
    
    def deactivate(self):
        """Деактивировать инструмент пипетки"""
        self.active = False
    
    def pick_color(self, image: Image.Image, position: tuple):
        """
        Выбрать цвет пикселя из изображения
        
        Args:
            image: PIL.Image - изображение
            position: tuple (x, y) - координаты клика
        
        Returns:
            tuple: (R, G, B, A) - выбранный цвет или None если не удалось
        """
        if not image:
            return None
        
        x, y = position
        img_width, img_height = image.size
        
        # Проверяем, что координаты в пределах изображения
        if x < 0 or y < 0 or x >= img_width or y >= img_height:
            sg.popup_error(
                "Координати поза межами зображення!",
                title="Помилка"
            )
            return None
        
        try:
            # Конвертируем изображение в RGBA для единообразия
            rgba_image = image.convert("RGBA")
            
            # Получаем цвет пикселя
            pixel_color = rgba_image.getpixel((int(x), int(y)))
            
            # Если цвет в формате RGB, добавляем альфа-канал
            if len(pixel_color) == 3:
                pixel_color = (*pixel_color, 255)
            
            self.selected_color = pixel_color
            
            # Показываем уведомление с выбранным цветом
            color_hex = "#{:02x}{:02x}{:02x}".format(*pixel_color[:3])
            sg.popup(
                f"✅ Колір обрано!\n\n"
                f"RGB: {pixel_color[:3]}\n"
                f"HEX: {color_hex}",
                title="Піпетка",
                auto_close=True,
                auto_close_duration=2
            )
            
            return self.selected_color
            
        except Exception as e:
            sg.popup_error(
                f"Помилка при виборі кольору:\n{e}",
                title="Помилка"
            )
            return None
    
    def get_current_color(self):
        """
        Получить текущий выбранный цвет
        
        Returns:
            tuple: (R, G, B, A)
        """
        return self.selected_color
    
    def get_color_preview_text(self):
        """
        Получить текстовое представление цвета для отображения
        
        Returns:
            str: HEX представление цвета
        """
        r, g, b, a = self.selected_color
        return "#{:02x}{:02x}{:02x}".format(r, g, b)