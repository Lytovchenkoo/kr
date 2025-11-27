# -*- coding: utf-8 -*-
import io
import PySimpleGUI as sg
from gui import create_main_window
from file_loader import load_image
from filters import (
    to_grayscale, blur_image, sharpen_image,
    adjust_brightness, adjust_contrast
)
from history import History
from PIL import Image
from layers import LayerManager
from slice_tool import SliceTool
from eyedropper_tool import EyedropperTool

def image_to_bytes(image: Image.Image):
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    return bio.getvalue()

window = create_main_window()
current_image = None
original_image = None
history = History()
layer_manager = None
drawing = False
last_pos = None
slice_tool = SliceTool()
eyedropper_tool = EyedropperTool()

while True:
    event, values = window.read(timeout=20)
    
    if event in (sg.WIN_CLOSED, "Вихід"):
        break

    if event == "Відкрити файл":
        image = load_image()
        if image:
            original_image = image.copy()
            current_image = image
            history.add_state(current_image)
            layer_manager = LayerManager(base_image=current_image)
            graph = window['-GRAPH-']
            graph.erase()
            graph.draw_image(data=image_to_bytes(current_image), location=(0, 0))

    elif event == "Ч/Б" and current_image:
        current_image = to_grayscale(current_image)
    elif event == "Розмиття" and current_image:
        current_image = blur_image(current_image)
    elif event == "Різкість" and current_image:
        current_image = sharpen_image(current_image)
    elif event == "Яскравість+" and current_image:
        current_image = adjust_brightness(current_image, factor=1.2)
    elif event == "Контраст+" and current_image:
        current_image = adjust_contrast(current_image, factor=1.3)

    if event in ["Ч/Б", "Розмиття", "Різкість", "Яскравість+", "Контраст+"] and current_image:
        history.add_state(current_image)
        window['-GRAPH-'].erase()
        window['-GRAPH-'].draw_image(data=image_to_bytes(current_image), location=(0, 0))

    elif event == "Undo":
        img = history.undo()
        if img:
            current_image = img
    elif event == "Redo":
        img = history.redo()
        if img:
            current_image = img

    if event in ["Undo", "Redo"] and current_image:
        window['-GRAPH-'].erase()
        window['-GRAPH-'].draw_image(data=image_to_bytes(current_image), location=(0, 0))

    elif event == "Назад" and original_image:
        current_image = original_image.copy()
        history.add_state(current_image)
        window['-GRAPH-'].erase()
        window['-GRAPH-'].draw_image(data=image_to_bytes(current_image), location=(0, 0))

    elif event == "Зберегти як" and current_image:
        save_path = sg.popup_get_file(
            "Оберіть місце для збереження",
            save_as=True,
            no_window=True,
            default_extension=".png",
            default_path="image_edited.png",
            file_types=(("PNG файли", "*.png"), ("JPEG файли", "*.jpg"), ("Всі файли", "*.*"))
        )
        if save_path:
            try:
                current_image.save(save_path)
                sg.popup("✅ Зображення успішно збережено!", title="Збереження")
            except Exception as e:
                sg.popup_error(f"Помилка під час збереження файлу:\n{e}")

    elif event == "Додати шар" and layer_manager:
        layer_manager.add_layer()
    elif event == "Видалити шар" and layer_manager:
        layer_manager.remove_layer()

    if event in ["Додати шар", "Видалити шар"] and layer_manager:
        composite = layer_manager.get_composite()
        if composite:
            current_image = composite.convert("RGB")
            window['-GRAPH-'].erase()
            window['-GRAPH-'].draw_image(data=image_to_bytes(current_image), location=(0, 0))

    elif event == "Почати малювання":
        drawing = True
        last_pos = None
        slice_tool.active = False  # Отключаем slice
        eyedropper_tool.deactivate()  # Отключаем пипетку
    elif event == "Завершити малювання":
        drawing = False
        last_pos = None

    # === ОБРАБОТКА ПИПЕТКИ (EYEDROPPER) ===
    elif event == "Піпетка":
        if not current_image:
            sg.popup_error("Спочатку завантажте зображення!", title="Помилка")
        else:
            eyedropper_tool.activate()
            drawing = False  # Отключаем рисование
            slice_tool.active = False  # Отключаем slice
            sg.popup(
                "Піпетка активована!\n\n"
                "Клікніть на зображення для вибору кольору",
                title="Піпетка",
                auto_close=True,
                auto_close_duration=3
            )

    # === ОБРАБОТКА SLICE TOOL ===
    elif event == "Виділити область (Slice)":
        if not current_image:
            sg.popup_error("Спочатку завантажте зображення!", title="Помилка")
        else:
            slice_tool.active = True
            drawing = False  # Отключаем рисование
            eyedropper_tool.deactivate()  # Отключаем пипетку
            sg.popup(
                "Виділення активовано!\n\n"
                "1. Натисніть і утримуйте ліву кнопку миші\n"
                "2. Перетягніть для виділення області\n"
                "3. Відпустіть кнопку миші\n"
                "4. Натисніть 'Експортувати виділення'",
                title="Інструкція",
                auto_close=True,
                auto_close_duration=5
            )
    
    elif event == "Експортувати виділення":
        if slice_tool.has_selection() and current_image:
            success = slice_tool.export_slice(current_image)
            if success:
                slice_tool.clear_selection(window['-GRAPH-'])
        elif not slice_tool.has_selection():
            sg.popup_error("Спочатку виділіть область!", title="Помилка")
    
    elif event == "Скасувати виділення":
        slice_tool.clear_selection(window['-GRAPH-'])

    # === ОБРАБОТКА РИСОВАНИЯ ===
    if drawing and layer_manager and layer_manager.active_layer_index is not None:
        mouse = values.get('-GRAPH-')
        if mouse and mouse[0] is not None and mouse[1] is not None:
            x, y = mouse
            if last_pos:
                layer_manager.draw_on_active_layer_line(last_pos, (x, y))
            else:
                layer_manager.draw_on_active_layer((x, y))
            last_pos = (x, y)
            composite = layer_manager.get_composite()
            current_image = composite.convert("RGB")
            window['-GRAPH-'].erase()
            window['-GRAPH-'].draw_image(data=image_to_bytes(current_image), location=(0, 0))
        else:
            last_pos = None
    
    # === ОБРАБОТКА ПИПЕТКИ (выбор цвета по клику) ===
    elif eyedropper_tool.active:
        mouse = values.get('-GRAPH-')
        
        # Клик для выбора цвета
        if event == '-GRAPH-' and mouse and mouse[0] is not None and current_image:
            picked_color = eyedropper_tool.pick_color(current_image, mouse)
            if picked_color and layer_manager:
                # Устанавливаем выбранный цвет для рисования
                layer_manager.set_drawing_color(picked_color)
            # Деактивируем пипетку после выбора цвета
            eyedropper_tool.deactivate()
    
    # === ОБРАБОТКА SLICE TOOL (выделение области) ===
    elif slice_tool.active:
        mouse = values.get('-GRAPH-')
        
        # Начало выделения (нажатие кнопки мыши)
        if event == '-GRAPH-' and mouse and mouse[0] is not None:
            if not slice_tool.selecting:
                slice_tool.start_selection(mouse)
        
        # Процесс выделения (движение мыши с зажатой кнопкой)
        if slice_tool.selecting and mouse and mouse[0] is not None:
            slice_tool.update_selection(mouse, window['-GRAPH-'])
        
        # Завершение выделения (отпускание кнопки мыши)
        # В PySimpleGUI это определяется когда mouse становится (None, None)
        if slice_tool.selecting and (mouse is None or mouse == (None, None)):
            slice_tool.finish_selection(window['-GRAPH-'])

window.close()