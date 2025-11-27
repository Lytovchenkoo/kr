# -*- coding: utf-8 -*-
import PySimpleGUI as sg

sg.theme('DarkGrey13')

def create_main_window(image_size=(600, 400)):
    """
    Создаёт главное окно редактора с минималистичным интерфейсом
    Только иконки без кнопок
    """
    
    # Стиль для иконок
    icon_font = ("Segoe UI Emoji", 24)
    icon_bg = "#1e293b"
    icon_hover = "#334155"
    
    # === ВЕРХНЯЯ ПАНЕЛЬ (только иконки) ===
    top_panel = [
        sg.Text("📁", font=icon_font, background_color=icon_bg, 
                tooltip="Відкрити файл", key="Відкрити файл",
                enable_events=True, pad=(10, 5)),
        sg.Text("💾", font=icon_font, background_color=icon_bg,
                tooltip="Зберегти зображення", key="Зберегти як",
                enable_events=True, pad=(10, 5)),
        sg.Push(),
        sg.Text("🎨 Редактор зображень", font=("Arial", 14, "bold"), 
                text_color="#60a5fa", background_color=icon_bg),
        sg.Push(),
        sg.Text("🚪", font=icon_font, background_color=icon_bg,
                tooltip="Вийти з програми", key="Вихід",
                enable_events=True, pad=(10, 5))
    ]
    
    # === ЛІВА ПАНЕЛЬ (Фільтри і шари) ===
    left_panel = sg.Column([
        [sg.Text("Фільтри", font=("Arial", 9), justification="center", 
                 background_color=icon_bg, text_color="#94a3b8")],
        [sg.Text("⚫", font=icon_font, background_color=icon_bg,
                 tooltip="Чорно-біле", key="Ч/Б",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("🌫️", font=icon_font, background_color=icon_bg,
                 tooltip="Розмиття", key="Розмиття",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("✨", font=icon_font, background_color=icon_bg,
                 tooltip="Різкість", key="Різкість",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("☀️", font=icon_font, background_color=icon_bg,
                 tooltip="Яскравість", key="Яскравість+",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("🎭", font=icon_font, background_color=icon_bg,
                 tooltip="Контраст", key="Контраст+",
                 enable_events=True, pad=(5, 8))],
        [sg.HorizontalSeparator(color="#475569")],
        [sg.Text("Шари", font=("Arial", 9), justification="center",
                 background_color=icon_bg, text_color="#94a3b8")],
        [sg.Text("➕", font=icon_font, background_color=icon_bg,
                 tooltip="Додати шар", key="Додати шар",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("➖", font=icon_font, background_color=icon_bg,
                 tooltip="Видалити шар", key="Видалити шар",
                 enable_events=True, pad=(5, 8))],
    ], vertical_alignment="top", element_justification="center",
       background_color=icon_bg, pad=(5, 10))
    
    # === ПРАВА ПАНЕЛЬ (Інструменти) ===
    right_panel = sg.Column([
        [sg.Text("Інструменти", font=("Arial", 9), justification="center",
                 background_color=icon_bg, text_color="#94a3b8")],
        [sg.Text("🖌️", font=icon_font, background_color=icon_bg,
                 tooltip="Почати малювання", key="Почати малювання",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("⏹️", font=icon_font, background_color=icon_bg,
                 tooltip="Завершити малювання", key="Завершити малювання",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("💧", font=icon_font, background_color=icon_bg,
                 tooltip="Піпетка - вибрати колір", key="Піпетка",
                 enable_events=True, pad=(5, 8))],
        [sg.HorizontalSeparator(color="#475569")],
        [sg.Text("✂️", font=icon_font, background_color=icon_bg,
                 tooltip="Виділити область", key="Виділити область (Slice)",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("📤", font=icon_font, background_color=icon_bg,
                 tooltip="Експортувати виділення", key="Експортувати виділення",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("❌", font=icon_font, background_color=icon_bg,
                 tooltip="Скасувати виділення", key="Скасувати виділення",
                 enable_events=True, pad=(5, 8))],
        [sg.HorizontalSeparator(color="#475569")],
        [sg.Text("Історія", font=("Arial", 9), justification="center",
                 background_color=icon_bg, text_color="#94a3b8")],
        [sg.Text("↶", font=icon_font, background_color=icon_bg,
                 tooltip="Скасувати дію", key="Undo",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("↷", font=icon_font, background_color=icon_bg,
                 tooltip="Повернути дію", key="Redo",
                 enable_events=True, pad=(5, 8))],
        [sg.Text("🔄", font=icon_font, background_color=icon_bg,
                 tooltip="До оригіналу", key="Назад",
                 enable_events=True, pad=(5, 8))],
    ], vertical_alignment="top", element_justification="center",
       background_color=icon_bg, pad=(5, 10))
    
    # === ЦЕНТРАЛЬНА ОБЛАСТЬ (Canvas) ===
    canvas_area = sg.Column([
        [sg.Graph(
            canvas_size=image_size,
            graph_bottom_left=(0, image_size[1]),
            graph_top_right=(image_size[0], 0),
            background_color='#0f172a',
            key='-GRAPH-',
            enable_events=True,
            drag_submits=True,
            border_width=0,
            pad=(10, 10)
        )]
    ], element_justification="center", vertical_alignment="center",
       background_color=icon_bg)
    
    # === ОСНОВНИЙ LAYOUT ===
    layout = [
        [sg.Column([top_panel], justification="center", expand_x=True, 
                   pad=(10, 10), background_color=icon_bg)],
        [sg.HorizontalSeparator(color="#475569")],
        [
            left_panel,
            sg.VerticalSeparator(color="#475569"),
            canvas_area,
            sg.VerticalSeparator(color="#475569"),
            right_panel
        ]
    ]
    
    return sg.Window(
        "🎨 Редактор зображень",
        layout,
        size=(900, 650),
        resizable=True,
        finalize=True,
        element_justification="center",
        background_color=icon_bg,
        margins=(0, 0)
    )