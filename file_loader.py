# -*- coding: utf-8 -*-
from PIL import Image
import PySimpleGUI as sg

def load_image():
    filename = sg.popup_get_file(
        'Оберіть зображення для відкриття',
        title='Відкриття файлу',
        file_types=(("Зображення", "*.png;*.jpg;*.jpeg;*.bmp"),)
    )
    if filename:
        image = Image.open(filename)
        return image
    return None
