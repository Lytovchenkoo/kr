# -*- coding: utf-8 -*-
"""
Модуль для выделения области изображения и экспорта её в файл (Slice Tool)
Аналог инструмента Slice в Figma
"""

from PIL import Image
import PySimpleGUI as sg


class SliceTool:
    """
    Инструмент для выделения прямоугольной области 
    и экспорта её как отдельного изображения
    """
    
    def __init__(self):
        self.start_point = None      # Начальная точка выделения (x, y)
        self.end_point = None        # Конечная точка выделения (x, y)
        self.active = False          # Активен ли инструмент выделения
        self.rect_id = None          # ID прямоугольника на графе
        self.selecting = False       # Идёт ли процесс выделения
    
    def start_selection(self, point):
        """
        Начало выделения области
        
        Args:
            point: tuple (x, y) - координаты начальной точки
        """
        self.start_point = point
        self.end_point = point
        self.selecting = True
    
    def update_selection(self, point, graph):
        """
        Обновление выделенной области при движении мыши
        
        Args:
            point: tuple (x, y) - текущие координаты мыши
            graph: PySimpleGUI Graph элемент для отрисовки
        """
        if not self.selecting or not self.start_point:
            return
        
        self.end_point = point
        
        # Удаляем старый прямоугольник
        if self.rect_id:
            graph.delete_figure(self.rect_id)
        
        # Рисуем новый прямоугольник выделения
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        self.rect_id = graph.draw_rectangle(
            (x1, y1), (x2, y2),
            line_color='red',
            line_width=2
        )
    
    def finish_selection(self, graph):
        """
        Завершение выделения
        
        Args:
            graph: PySimpleGUI Graph элемент
        """
        self.selecting = False
        # Не удаляем прямоугольник, чтобы пользователь видел что выделено
    
    def clear_selection(self, graph):
        """
        Очистка выделения
        
        Args:
            graph: PySimpleGUI Graph элемент
        """
        if self.rect_id:
            graph.delete_figure(self.rect_id)
            self.rect_id = None
        self.start_point = None
        self.end_point = None
        self.selecting = False
        self.active = False
    
    def has_selection(self):
        """
        Проверка, есть ли выделенная область
        
        Returns:
            bool: True если область выделена
        """
        return (self.start_point is not None and 
                self.end_point is not None and 
                self.start_point != self.end_point)
    
    def get_selection_bounds(self):
        """
        Получить границы выделенной области
        
        Returns:
            tuple: (x1, y1, x2, y2) - координаты прямоугольника
                   или None если нет выделения
        """
        if not self.has_selection():
            return None
        
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        # Нормализуем координаты (на случай если тянули справа налево или снизу вверх)
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        return (left, top, right, bottom)
    
    def export_slice(self, image):
        """
        Экспорт выделенной области в файл
        
        Args:
            image: PIL.Image.Image - исходное изображение
        
        Returns:
            bool: True если экспорт успешен, False иначе
        """
        bounds = self.get_selection_bounds()
        
        if not bounds:
            sg.popup_error("Не виділено область для експорту!", title="Помилка")
            return False
        
        left, top, right, bottom = bounds
        
        # Проверяем, что координаты в пределах изображения
        img_width, img_height = image.size
        
        if left < 0 or top < 0 or right > img_width or bottom > img_height:
            sg.popup_error(
                "Виділена область виходить за межі зображення!",
                title="Помилка"
            )
            return False
        
        # Вырезаем область
        try:
            cropped_image = image.crop((left, top, right, bottom))
            
            # Диалог сохранения файла
            save_path = sg.popup_get_file(
                "Оберіть місце для збереження виділеної області",
                save_as=True,
                no_window=True,
                default_extension=".png",
                default_path="slice_export.png",
                file_types=(
                    ("PNG файли", "*.png"),
                    ("JPEG файли", "*.jpg"),
                    ("Всі файли", "*.*")
                )
            )
            
            if save_path:
                cropped_image.save(save_path)
                sg.popup(
                    f"✅ Виділену область успішно збережено!\n"
                    f"Розмір: {cropped_image.size[0]}x{cropped_image.size[1]} пікселів",
                    title="Експорт успішний"
                )
                return True
            
        except Exception as e:
            sg.popup_error(
                f"Помилка під час експорту:\n{e}",
                title="Помилка"
            )
            return False
        
        return False