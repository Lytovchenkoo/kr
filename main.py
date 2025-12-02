# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import io
from PIL import Image, ImageOps

from gui import create_main_window
from file_loader import load_image
from layers import LayerManager
from history import History
from eyedropper_tool import EyedropperTool
from selection_tool import SelectionTool
from text_tool import TextTool
from filters import *

# --- ФУНКЦІЇ ---
def image_to_data(image: Image.Image):
    bio = io.BytesIO()
    image.save(bio, format="PNG") 
    return bio.getvalue()

def update_ui_layers():
    if layer_manager:
        names = layer_manager.get_layer_names()
        window["-LAYER_LIST-"].update(names)

def get_display_image():
    if not layer_manager: return None
    base = layer_manager.get_composite()
    if floating_object and floating_object['image']:
        temp = Image.new("RGBA", base.size, (0,0,0,0))
        temp.paste(floating_object['image'], (floating_object['x'], floating_object['y']))
        base = Image.alpha_composite(base, temp)
    return base

def update_canvas():
    """Повне оновлення екрану"""
    try:
        img = get_display_image()
        if img:
            window['-GRAPH-'].erase()
            window['-GRAPH-'].draw_image(data=image_to_data(img), location=(0, 0))
    except: pass

def commit_floating_object():
    global floating_object
    if floating_object and layer_manager:
        layer_manager.add_layer_with_content(floating_object['image'], 
                                           (floating_object['x'], floating_object['y']))
        floating_object = None
        update_ui_layers()

def save_state():
    if floating_object: commit_floating_object()
    if not layer_manager: return
    final = layer_manager.get_composite()
    history.add_state(final)
    update_ui_layers()

def apply_layer_filter(func, **kwargs):
    global floating_object
    try:
        if floating_object:
            floating_object['image'] = func(floating_object['image'], **kwargs)
            update_canvas()
        elif layer_manager:
            layer = layer_manager.get_active_layer()
            if layer:
                processed = func(layer['image'], **kwargs)
                if selection_tool.has_selection():
                    mask = selection_tool.create_mask(layer['image'].size)
                    layer['image'] = Image.composite(processed, layer['image'], mask)
                else:
                    layer['image'] = processed
                save_state(); update_canvas()
    except: pass

def get_valid_float(prompt, default, min_val=0.0, max_val=10.0):
    while True:
        txt = sg.popup_get_text(f"{prompt} ({min_val}-{max_val})", default_text=str(default), keep_on_top=True)
        if txt is None: return None
        try:
            val = float(txt.replace(',', '.'))
            if min_val <= val <= max_val: return val
            else: sg.popup_error("Число поза діапазоном", keep_on_top=True)
        except: sg.popup_error("Введіть число", keep_on_top=True)

def get_valid_int(prompt, default):
    txt = sg.popup_get_text(prompt, default_text=str(default), keep_on_top=True)
    try: return int(txt)
    except: return None

def hex_to_rgba(hex_color):
    if not hex_color: return (0, 0, 0, 255)
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)

# --- ЗАПУСК ---
window = create_main_window()
layer_manager = None
history = History()
selection_tool = SelectionTool()
text_tool = TextTool()
eyedropper_tool = EyedropperTool()

tool_mode = None
last_pos = None
clipboard = None
floating_object = None 
drag_start = None

while True:
    event, values = window.read(timeout=20)
    if event in (sg.WIN_CLOSED, "Вихід"): break

    # Безпечне отримання миші
    mouse = values['-GRAPH-'] if values and '-GRAPH-' in values else (None, None)

    # === МАЛЮВАННЯ ТА РУХ ===
    if event == '-GRAPH-' and mouse != (None, None):
        x, y = mouse
        
        # ПЕРЕМІЩЕННЯ
        if tool_mode == 'MoveTool' and floating_object:
            if not drag_start:
                drag_start = mouse; obj_start = (floating_object['x'], floating_object['y'])
            else:
                dx, dy = x - drag_start[0], y - drag_start[1]
                floating_object['x'] = obj_start[0] + dx
                floating_object['y'] = obj_start[1] + dy
                update_canvas()

        # МАЛЮВАННЯ (Гібридний метод: Швидко на екрані + В пам'ять)
        elif tool_mode in ['DRAW', 'ERASER'] and layer_manager:
            is_eraser = (tool_mode == 'ERASER')
            
            if last_pos:
                # 1. Малюємо лінію в пам'яті
                layer_manager.draw_on_active_layer_line(last_pos, (x, y), erase=is_eraser)
                
                if is_eraser:
                    # Стирачка вимагає повного оновлення (відновлення фону)
                    update_canvas()
                else:
                    # Пензель: малюємо лінію на екрані (ДУЖЕ ШВИДКО, НЕМАЄ КРАПОК)
                    c = layer_manager.get_drawing_color(); hex_c = "#{:02x}{:02x}{:02x}".format(*c[:3])
                    r = layer_manager.brush_radius
                    window['-GRAPH-'].draw_line(last_pos, (x, y), color=hex_c, width=r*2)
                    window['-GRAPH-'].draw_circle((x, y), r, fill_color=hex_c, line_color=hex_c)
            else:
                # Перша точка
                layer_manager.draw_on_active_layer((x, y), erase=is_eraser)
                if is_eraser: update_canvas()
            
            last_pos = (x, y)

        # ВИДІЛЕННЯ
        elif tool_mode in ['RECT', 'ELLIPSE', 'LASSO']:
            if not selection_tool.selecting: selection_tool.start_selection(mouse, tool_mode)
            else: selection_tool.update_selection(mouse, window['-GRAPH-'])

    # === ЯКЩО МИША НЕ РУХАЄТЬСЯ (АБО ВІДПУЩЕНА) ===
    elif event != '-GRAPH-':
        # Скидаємо лінію (щоб не з'єднувалась)
        last_pos = None
        drag_start = None
        
        # Завершуємо виділення
        if tool_mode in ['RECT', 'ELLIPSE', 'LASSO'] and selection_tool.selecting:
            selection_tool.finish_selection(window['-GRAPH-'])

    # === ІНСТРУМЕНТИ ===
    if event == "Почати малювання": 
        if floating_object: save_state()
        
        # Автоматично додаємо шар, якщо на фоні (Ваша ідея)
        if layer_manager and layer_manager.active_index == 0:
             layer_manager.add_layer(name="Малювання")
             update_ui_layers()
             sg.popup_quick_message("Створено шар для малювання")
        
        tool_mode = 'DRAW'
        last_pos = None

    if event == "Завершити малювання":
        tool_mode = None
        last_pos = None
        update_canvas() # Фіксуємо малюнок
        save_state()    # Зберігаємо в історію

    if event == "MoveTool": tool_mode = 'MoveTool'
    elif event == "EraserTool":
        if floating_object: save_state()
        tool_mode = 'ERASER'; sg.popup_quick_message("Стирачка")
    elif event == "Піпетка": tool_mode = 'EYEDROPPER'; eyedropper_tool.activate()
    elif event == "Текст": tool_mode = 'TEXT'
    
    # Клік для Тексту/Піпетки (перевіряємо окремо, бо drag_submits=True може не дати клік)
    # Тут ми використовуємо простий трюк: якщо натиснули кнопку, а drag не почався
    
    # ... (Інші події стандартні) ...

    if event == "ChooseColor" and layer_manager:
        picked = sg.askcolor()
        if picked and picked[0]:
            rgba = picked[0] + (255,)
            layer_manager.set_drawing_color(rgba)

    if event == "Відкрити файл":
        img = load_image()
        if img:
            cw, ch = 800, 600
            if img.width > cw or img.height > ch:
                ratio = min(cw/img.width, ch/img.height)
                img = img.resize((int(img.width*ratio), int(img.height*ratio)), Image.Resampling.LANCZOS)
            layer_manager = LayerManager(img)
            history = History(); history.add_state(img.convert("RGBA"))
            floating_object = None; update_ui_layers(); update_canvas()

    if event == "-BRUSH_SIZE-" and layer_manager:
        layer_manager.set_brush_size(int(values['-BRUSH_SIZE-']))

    if event == "Додати шар" and layer_manager: layer_manager.add_layer(); update_ui_layers()
    elif event == "Видалити шар" and layer_manager: layer_manager.remove_active_layer(); save_state(); update_canvas()
    elif event == "ToggleVis" and layer_manager:
        l = layer_manager.get_active_layer()
        if l: l['visible'] = not l['visible']; update_ui_layers(); update_canvas()
    elif event == "-LAYER_LIST-" and layer_manager:
        idxs = window["-LAYER_LIST-"].get_indexes()
        if idxs: layer_manager.select_layer_by_gui_index(idxs[0]); update_ui_layers()

    if event == "Copy" and selection_tool.has_selection() and layer_manager:
        l = layer_manager.get_active_layer()
        if l:
            mask = selection_tool.create_mask(l['image'].size)
            bbox = mask.getbbox()
            if bbox: clipboard = l['image'].crop(bbox); clipboard.putalpha(mask.crop(bbox)); sg.popup_quick_message("Скопійовано!")

    elif event == "Cut" and selection_tool.has_selection() and layer_manager:
        l = layer_manager.get_active_layer()
        if l:
            mask = selection_tool.create_mask(l['image'].size)
            bbox = mask.getbbox()
            if bbox:
                clipboard = l['image'].crop(bbox); clipboard.putalpha(mask.crop(bbox))
                empty = Image.new("RGBA", l['image'].size, (0,0,0,0))
                l['image'] = Image.composite(empty, l['image'], mask)
                selection_tool.clear_selection(window['-GRAPH-'])
                save_state(); update_canvas(); sg.popup_quick_message("Вирізано!")

    elif event == "Paste" and clipboard and layer_manager:
        if floating_object: commit_floating_object()
        w, h = layer_manager.layers[0]['image'].size
        floating_object = {'image': clipboard.copy(), 'x': (w-clipboard.width)//2, 'y': (h-clipboard.height)//2}
        tool_mode = 'MoveTool'; selection_tool.clear_selection(window['-GRAPH-'])
        update_canvas(); sg.popup_quick_message("Вставлено!")

    elif event == "AnchorObject":
        if floating_object: save_state(); update_canvas(); sg.popup_quick_message("Зафіксовано")

    if event in ["SelectRect", "SelectEllipse", "SelectLasso"]:
        tool_mode = {'SelectRect':'RECT', 'SelectEllipse':'ELLIPSE', 'SelectLasso':'LASSO'}[event]; selection_tool.active = True
    elif event == "Скасувати виділення": selection_tool.clear_selection(window['-GRAPH-']); update_canvas()
    elif event == "DeleteArea" and layer_manager:
        if floating_object: floating_object = None; update_canvas()
        elif selection_tool.has_selection():
            l = layer_manager.get_active_layer()
            mask = selection_tool.create_mask(l['image'].size)
            empty = Image.new("RGBA", l['image'].size, (0,0,0,0))
            l['image'] = Image.composite(empty, l['image'], mask)
            selection_tool.clear_selection(window['-GRAPH-']); save_state(); update_canvas()

    if layer_manager:
        if event == "Яскравість+": apply_layer_filter(adjust_brightness, factor=1.1)
        elif event == "Яскравість-": apply_layer_filter(adjust_brightness, factor=0.9)
        elif event == "Контраст+": apply_layer_filter(adjust_contrast, factor=1.1)
        elif event == "Контраст-": apply_layer_filter(adjust_contrast, factor=0.9)
        elif event == "Різкість+": apply_layer_filter(adjust_sharpness, factor=1.5)
        elif event == "Різкість-": apply_layer_filter(adjust_sharpness, factor=0.5)
        elif event == "Насиченість+": apply_layer_filter(adjust_saturation, factor=1.2)
        elif event == "Насиченість-": apply_layer_filter(adjust_saturation, factor=0.0)
        elif event == "АвтоРівні": apply_layer_filter(auto_levels)
        elif event == "БалансКольорів":
            r = get_valid_float("Червоний канал", 1.0); b = get_valid_float("Синій", 1.0)
            if r and b: apply_layer_filter(adjust_color_balance, r=r, g=1.0, b=b)

    if event == "Обернути" and layer_manager:
        if floating_object: floating_object['image'] = floating_object['image'].rotate(-90, expand=True); update_canvas()
        else: layer_manager.rotate_all(-90, expand=True); save_state(); update_canvas()
    elif event == "Дзеркало" and layer_manager:
        if floating_object: floating_object['image'] = ImageOps.mirror(floating_object['image']); update_canvas()
        else: layer_manager.mirror_all(); save_state(); update_canvas()
    elif event == "Ресайз" and layer_manager:
        t = layer_manager.layers[0]['image']
        w = get_valid_int(f"Ширина ({t.width}):", t.width)
        if w:
            ratio = w/t.width; h=int(t.height*ratio)
            layer_manager.resize_all(w, h, Image.Resampling.LANCZOS); save_state(); update_canvas()

    if event == "Undo":
        img = history.undo()
        if img: layer_manager = LayerManager(img); floating_object = None; update_ui_layers(); update_canvas()
    elif event == "Redo":
        img = history.redo()
        if img: layer_manager = LayerManager(img); floating_object = None; update_ui_layers(); update_canvas()

    if event == "Зберегти як" and layer_manager:
        if floating_object: commit_floating_object()
        path = sg.popup_get_file("Зберегти", save_as=True, no_window=True, file_types=(("PNG", "*.png"), ("JPG", "*.jpg")))
        if path:
            try: layer_manager.get_composite().save(path); sg.popup_quick_message("Збережено!")
            except: pass

window.close()