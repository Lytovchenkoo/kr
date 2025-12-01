# -*- coding: utf-8 -*-
from PIL import Image
import PySimpleGUI as sg

class EyedropperTool:
    def __init__(self):
        self.active = False
        self.selected_color = (255, 0, 0, 255)
    
    def activate(self):
        self.active = True
    
    def deactivate(self):
        self.active = False
    
    def pick_color(self, image: Image.Image, position: tuple):
        if not image:
            return None
        
        x, y = position
        img_width, img_height = image.size
        
        if x < 0 or y < 0 or x >= img_width or y >= img_height:
            sg.popup_error("Координати поза межами зображення!", title="Помилка", keep_on_top=True)
            return None
        
        try:
            rgba_image = image.convert("RGBA")
            pixel_color = rgba_image.getpixel((int(x), int(y)))
            
            if len(pixel_color) == 3:
                pixel_color = (*pixel_color, 255)
            
            self.selected_color = pixel_color
            
            color_hex = "#{:02x}{:02x}{:02x}".format(*pixel_color[:3])
            sg.popup(
                f"✅ Колір обрано!\nRGB: {pixel_color[:3]}\nHEX: {color_hex}",
                title="Піпетка",
                auto_close=True,
                auto_close_duration=2,
                keep_on_top=True
            )
            
            return self.selected_color
            
        except Exception as e:
            sg.popup_error(f"Помилка при виборі кольору:\n{e}", title="Помилка", keep_on_top=True)
            return None