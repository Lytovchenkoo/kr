# -*- coding: utf-8 -*-
from PIL import Image
import copy

class History:
    def __init__(self):
        self.states = []
        self.current_index = -1
        self.max_states = 30 

    def add_state(self, image: Image.Image):
        """Зберігає новий стан, обрізає майбутні redo за потреби"""
        # Обмеження історії
        if self.current_index < len(self.states) - 1:
            self.states = self.states[:self.current_index + 1]
        
        if len(self.states) >= self.max_states:
            self.states.pop(0)
            self.current_index -= 1

        # Використовуємо копію, щоб не було посилань на один об'єкт
        self.states.append(image.copy())
        self.current_index += 1

    def undo(self):
        """Повертає попередній стан або None"""
        if self.current_index > 0:
            self.current_index -= 1
            return self.states[self.current_index].copy()
        return None

    def redo(self):
        """Повертає наступний стан або None"""
        if self.current_index < len(self.states) - 1:
            self.current_index += 1
            return self.states[self.current_index].copy()
        return None