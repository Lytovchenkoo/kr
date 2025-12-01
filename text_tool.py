# -*- coding: utf-8 -*-
from PIL import ImageDraw, ImageFont
import PySimpleGUI as sg
import platform

class TextTool:
    def add_text(self, image, position, default_color):
        
        r, g, b, a = default_color
        hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        fonts = ['Arial', 'Times New Roman', 'Verdana', 'Courier New', 'Segoe UI']
        
        layout = [
            [sg.Text("Текст:"), sg.InputText(key='-TEXT-', focus=True)],
            [sg.Text("Розмір:"), sg.Slider((8, 200), default_value=40, orientation='h', key='-SIZE-')],
            [sg.Text("Шрифт:"), sg.Combo(fonts, default_value='Arial', key='-FONT-')],
            [sg.Text("Колір:", size=(6, 1)), sg.Input(default_text=hex_color, size=(10, 1), key='-COLOR-'), 
             sg.ColorChooserButton("🎨", target='-COLOR-', button_color=('white', '#333333'))],
            [sg.HorizontalSeparator()],
            [sg.Button("Додати текст", bind_return_key=True), sg.Button("Скасувати")]
        ]
        
        win = sg.Window("Вставка тексту", layout, modal=True, keep_on_top=True)
        event, values = win.read()
        win.close()
        
        if event == "Додати текст" and values['-TEXT-']:
            text = values['-TEXT-']
            size = int(values['-SIZE-'])
            font_name = values['-FONT-']
            color_hex = values['-COLOR-']
            
            try:
                h = color_hex.lstrip('#')
                color = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)
            except:
                color = default_color

            font = None
            try:
                font_files = {'Arial': 'arial.ttf', 'Times New Roman': 'times.ttf', 
                              'Verdana': 'verdana.ttf', 'Courier New': 'cour.ttf', 'Segoe UI': 'segoeui.ttf'}
                font_file = font_files.get(font_name, 'arial.ttf')
                
                if platform.system() == "Windows":
                    font = ImageFont.truetype(f"C:\\Windows\\Fonts\\{font_file}", size)
                else:
                    font = ImageFont.truetype(font_file, size)
            except:
                font = ImageFont.load_default()
            
            draw = ImageDraw.Draw(image)
            draw.text(position, text, font=font, fill=color)
            return True
        return False