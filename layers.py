# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw

class LayerManager:
    def __init__(self, base_image: Image.Image):
        self.base_image = base_image.copy()
        self.layers = []
        self.active_layer_index = None
        self.current_color = (255, 0, 0, 255)  # Текущий цвет рисования (по умолчанию красный)
        self.brush_radius = 5  # Размер кисти
    
    def set_drawing_color(self, color):
        """
        Установить цвет для рисования
        
        Args:
            color: tuple (R, G, B, A) - цвет в формате RGBA
        """
        self.current_color = color
    
    def get_drawing_color(self):
        """Получить текущий цвет рисования"""
        return self.current_color
    
    def add_layer(self):
        """Додає новий прозорий шар"""
        layer = Image.new("RGBA", self.base_image.size, (0, 0, 0, 0))
        self.layers.append(layer)
        self.active_layer_index = len(self.layers) - 1
    
    def remove_layer(self):
        """Видаляє останній шар"""
        if self.layers:
            self.layers.pop()
            self.active_layer_index = len(self.layers) - 1 if self.layers else None
    
    def draw_on_active_layer(self, position, color=None, radius=None):
        """
        Малює точку на активному шарі
        
        Args:
            position: tuple (x, y) - координаты
            color: tuple (R, G, B, A) - цвет (если None, используется текущий)
            radius: int - радиус кисти (если None, используется текущий)
        """
        if self.active_layer_index is None:
            return
        
        layer = self.layers[self.active_layer_index]
        draw = ImageDraw.Draw(layer)
        x, y = position
        
        # Используем переданный цвет или текущий
        draw_color = color if color else self.current_color
        draw_radius = radius if radius else self.brush_radius
        
        draw.ellipse([x-draw_radius, y-draw_radius, x+draw_radius, y+draw_radius], 
                     fill=draw_color)
    
    def draw_on_active_layer_line(self, start, end, color=None, radius=None):
        """
        Малює лінію між двома точками на активному шарі
        
        Args:
            start: tuple (x, y) - начальная точка
            end: tuple (x, y) - конечная точка
            color: tuple (R, G, B, A) - цвет (если None, используется текущий)
            radius: int - радиус кисти (если None, используется текущий)
        """
        if self.active_layer_index is None:
            return
        
        layer = self.layers[self.active_layer_index]
        draw = ImageDraw.Draw(layer)
        
        # Используем переданный цвет или текущий
        draw_color = color if color else self.current_color
        draw_radius = radius if radius else self.brush_radius
        
        draw.line([start, end], fill=draw_color, width=draw_radius*2)
    
    def get_composite(self):
        """Повертає підсумкове зображення з базовим шаром і всіма додатковими"""
        composite = self.base_image.convert("RGBA")
        for layer in self.layers:
            composite = Image.alpha_composite(composite, layer)
        return composite