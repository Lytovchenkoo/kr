# -*- coding: utf-8 -*-
from PIL import Image
import copy

class History:
    def __init__(self):
        self.states = []        # список збережених станів
        self.current_index = -1  # індекс поточного стану

    def add_state(self, image: Image.Image):
        """Зберігає новий стан, обрізає майбутні redo за потреби"""
        # Якщо зроблено undo, а потім нову зміну — видаляємо майбутні стани
        if self.current_index < len(self.states) - 1:
            self.states = self.states[:self.current_index + 1]
        # Зберігаємо копію зображення
        self.states.append(copy.deepcopy(image))
        self.current_index += 1

    def undo(self):
        """Повертає попередній стан або None"""
        if self.current_index > 0:
            self.current_index -= 1
            return copy.deepcopy(self.states[self.current_index])
        return None

    def redo(self):
        """Повертає наступний стан або None"""
        if self.current_index < len(self.states) - 1:
            self.current_index += 1
            return copy.deepcopy(self.states[self.current_index])
        return None

    def get_current(self):
        """Повертає поточний стан"""
        if self.current_index >= 0:
            return copy.deepcopy(self.states[self.current_index])
        return None
