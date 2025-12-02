# -*- coding: utf-8 -*-
from PIL import Image

class EyedropperTool:
    def __init__(self):
        self.active = False
        self.selected_color = (255, 0, 0, 255)
    
    def activate(self):
        self.active = True
    
    def deactivate(self):
        self.active = False
    
    def pick_color(self, image: Image.Image, position: tuple):
        """Повертає колір пікселя (R, G, B, A) або None"""
        if not image:
            return None
        
        x, y = position
        
        # Перевірка, чи ми в межах зображення
        if 0 <= x < image.width and 0 <= y < image.height:
            # Отримуємо колір пікселя
            color = image.getpixel((int(x), int(y)))
            
            # Якщо зображення в режимі RGB (без прозорості), додаємо альфа-канал 255
            if len(color) == 3:
                color = color + (255,)
            
            self.selected_color = color
            return color
            
        return None