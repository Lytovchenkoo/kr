# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw

class SelectionTool:
    def __init__(self):
        self.mode = 'RECT' # 'RECT', 'ELLIPSE', 'LASSO'
        self.points = []
        self.selecting = False
        self.figure_id = None
        self.active = False # Чи є активне виділення?

    def start_selection(self, point, mode='RECT'):
        self.mode = mode
        self.points = [point]
        self.selecting = True
        self.active = False # Поки виділяємо - воно ще не активне

    def update_selection(self, point, graph):
        if not self.selecting: return
        
        # Видаляємо стару фігуру
        if self.figure_id:
            graph.delete_figure(self.figure_id)

        if self.mode == 'LASSO':
            self.points.append(point)
            if len(self.points) > 1:
                self.figure_id = graph.draw_polygon(self.points, line_color='red', line_width=2, fill_color=None)
        else:
            start = self.points[0]
            self.points = [start, point] # Оновлюємо кінець
            
            if self.mode == 'RECT':
                self.figure_id = graph.draw_rectangle(start, point, line_color='red', line_width=2)
            elif self.mode == 'ELLIPSE':
                self.figure_id = graph.draw_oval(start, point, line_color='red', line_width=2)

    def finish_selection(self, graph):
        self.selecting = False
        # Якщо виділення має хоча б якусь площу - воно стає активним
        if len(self.points) >= 2:
            self.active = True

    def clear_selection(self, graph):
        if self.figure_id:
            graph.delete_figure(self.figure_id)
            self.figure_id = None
        self.points = []
        self.selecting = False
        self.active = False

    def create_mask(self, image_size):
        """Створює маску для вирізання"""
        if not self.active or len(self.points) < 2: return None
        
        mask = Image.new('L', image_size, 0)
        draw = ImageDraw.Draw(mask)
        
        if self.mode == 'RECT':
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            draw.rectangle([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], fill=255)
        elif self.mode == 'ELLIPSE':
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            draw.ellipse([min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)], fill=255)
        elif self.mode == 'LASSO':
            if len(self.points) > 2:
                draw.polygon(self.points, fill=255)
                
        return mask

    def has_selection(self):
        return self.active and len(self.points) >= 2