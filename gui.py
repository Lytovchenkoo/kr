# -*- coding: utf-8 -*-
import PySimpleGUI as sg

sg.theme('DarkGrey13')

def create_main_window(image_size=(800, 600)):
    icon_font = ("Segoe UI Emoji", 20)
    icon_bg = "#1e293b"
    
    def icon_btn(text, key, tooltip):
        return sg.Text(text, font=icon_font, background_color=icon_bg, 
                       text_color="#e2e8f0", key=key, enable_events=True, 
                       tooltip=tooltip, pad=(5, 5))

    top_panel = [
        icon_btn("📁", "Відкрити файл", "Відкрити"),
        icon_btn("💾", "Зберегти як", "Зберегти"),
        sg.VSeparator(color="#475569"),
        icon_btn("🔄", "Обернути", "Обернути 90°"),
        icon_btn("↔️", "Дзеркало", "Віддзеркалити"),
        icon_btn("📐", "Ресайз", "Змінити розмір"),
        sg.Push(),
        sg.Text("🎨 SUPER EDITOR", font=("Arial", 14, "bold"), text_color="#60a5fa", background_color=icon_bg),
        sg.Push(),
        icon_btn("🚪", "Вихід", "Вихід")
    ]

    left_panel = sg.Column([
        [sg.Text("КОРЕКЦІЯ", font=("Arial", 9, "bold"), background_color=icon_bg, text_color="#94a3b8")],
        [icon_btn("☀️", "Яскравість+", "Більше яскравості"), icon_btn("🌑", "Яскравість-", "Менше яскравості")],
        [icon_btn("🌓", "Контраст+", "Більше контрасту"), icon_btn("🫥", "Контраст-", "Менше контрасту")],
        [icon_btn("✨", "Різкість+", "Більше різкості"), icon_btn("🌫️", "Різкість-", "Розмиття")],
        [icon_btn("🌈", "Насиченість+", "Більше кольору"), icon_btn("🧛", "Насиченість-", "Ч/Б")],
        [icon_btn("⚖️", "БалансКольорів", "Баланс RGB"), icon_btn("📊", "АвтоРівні", "Авто Рівні")],
        
        [sg.HorizontalSeparator(color="#475569")],
        [sg.Text("ШАРИ", font=("Arial", 9, "bold"), background_color=icon_bg, text_color="#94a3b8")],
        [sg.Listbox(values=[], size=(18, 6), key="-LAYER_LIST-", enable_events=True, 
                    font=("Consolas", 10), background_color="#0f172a", text_color="white", no_scrollbar=True)],
        [icon_btn("➕", "Додати шар", "Новий шар"), icon_btn("➖", "Видалити шар", "Видалити активний"), 
         icon_btn("👁️", "ToggleVis", "Сховати/Показати шар")]
    ], background_color=icon_bg, pad=(5, 5))

    right_panel = sg.Column([
        [sg.Text("ІНСТРУМЕНТИ", font=("Arial", 9, "bold"), background_color=icon_bg, text_color="#94a3b8")],
        # ВАЖЛИВО: Кнопки СТАРТ і СТОП для малювання
        [icon_btn("🖌️", "Почати малювання", "Пензлик"), icon_btn("⏹️", "Завершити малювання", "Зберегти фігуру (Стоп)")],
        [icon_btn("🧹", "EraserTool", "Стирачка"), icon_btn("✋", "MoveTool", "Переміщення")],
        
        [sg.Text("Розмір:", font=("Arial", 8), background_color=icon_bg, text_color="white"),
         sg.Slider(range=(1, 50), default_value=5, orientation='h', size=(10, 10), key='-BRUSH_SIZE-', enable_events=True, background_color=icon_bg)],
        
        [icon_btn("💧", "Піпетка", "Піпетка"), 
         sg.Button("🎨", key="ChooseColor", button_color=(icon_bg, icon_bg), border_width=0, font=icon_font, tooltip="Палітра")],

        [icon_btn("🅰️", "Текст", "Текст")],
        [sg.HorizontalSeparator(color="#475569")],
        [sg.Text("ВИДІЛЕННЯ", font=("Arial", 9, "bold"), background_color=icon_bg, text_color="#94a3b8")],
        [icon_btn("⬜", "SelectRect", "Прямокутник"), icon_btn("⭕", "SelectEllipse", "Еліпс")],
        [icon_btn("➰", "SelectLasso", "Ласо"), icon_btn("❌", "Скасувати виділення", "Зняти виділення")],
        
        [sg.HorizontalSeparator(color="#475569")],
        [sg.Text("ОБ'ЄКТИ", font=("Arial", 9, "bold"), background_color=icon_bg, text_color="#94a3b8")],
        [icon_btn("📄", "Copy", "Копіювати"), icon_btn("✂️", "Cut", "Вирізати")],
        [icon_btn("📋", "Paste", "Вставити"), icon_btn("✅", "AnchorObject", "Прикріпити")],
        [icon_btn("🗑️", "DeleteArea", "Видалити"), icon_btn("🖼️", "CropSelection", "Кроп")],
        
        [sg.HorizontalSeparator(color="#475569")],
        [icon_btn("↶", "Undo", "Скасувати"), icon_btn("↷", "Redo", "Повернути")]
    ], background_color=icon_bg, pad=(5, 5))

    # drag_submits=True - ВАЖЛИВО ДЛЯ ПЛАВНОСТІ
    graph = sg.Graph(
        canvas_size=image_size,
        graph_bottom_left=(0, image_size[1]),
        graph_top_right=(image_size[0], 0),
        background_color='#0f172a',
        key='-GRAPH-',
        enable_events=True,
        drag_submits=True,
        motion_events=True,
        pad=(0,0)
    )
    canvas_area = sg.Column([[graph]], background_color=icon_bg, element_justification='center')

    layout = [
        [sg.Column([top_panel], expand_x=True, background_color=icon_bg, element_justification='center')],
        [sg.HorizontalSeparator(color="#475569")],
        [left_panel, sg.VSeparator(color="#475569"), canvas_area, sg.VSeparator(color="#475569"), right_panel]
    ]

    window = sg.Window("Editor Pro", layout, resizable=True, finalize=True, background_color=icon_bg, margins=(0,0))
    return window