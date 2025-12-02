# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageOps

class LayerManager:
    def __init__(self, base_image: Image.Image):
        # Конвертуємо в RGBA
        base = base_image.convert("RGBA")
        # Зберігаємо оригінал для відновлення стирачкою
        self.original_background = base.copy()
        
        self.layers = [
            {'name': 'Фон', 'image': base, 'visible': True, 'opacity': 1.0}
        ]
        self.active_index = 0
        self.current_color = (255, 0, 0, 255)
        self.brush_radius = 5
        self.layer_counter = 1

    def add_layer(self, image=None, name=None):
        if image is None:
            w, h = self.layers[0]['image'].size
            image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if name is None:
            name = f"Шар {self.layer_counter}"
            self.layer_counter += 1
        self.layers.append({'name': name, 'image': image, 'visible': True, 'opacity': 1.0})
        self.active_index = len(self.layers) - 1

    def add_layer_with_content(self, content_image, position=(0, 0)):
        w, h = self.layers[0]['image'].size
        layer_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        layer_img.paste(content_image, position, content_image)
        self.add_layer(layer_img, name=f"Вставка {self.layer_counter}")

    def remove_active_layer(self):
        if len(self.layers) > 1 and self.active_index > 0:
            self.layers.pop(self.active_index)
            if self.active_index >= len(self.layers): self.active_index = len(self.layers) - 1

    def get_active_layer(self):
        if 0 <= self.active_index < len(self.layers):
            return self.layers[self.active_index]
        return None

    def get_layer_names(self):
        names = []
        for i, layer in enumerate(self.layers):
            eye = "👁️" if layer['visible'] else "🚫"
            marker = " ➤" if i == self.active_index else ""
            names.append(f"{eye} {layer['name']}{marker}")
        return names[::-1]

    def select_layer_by_gui_index(self, gui_index):
        real_index = len(self.layers) - 1 - gui_index
        if 0 <= real_index < len(self.layers): self.active_index = real_index

    def set_drawing_color(self, color): self.current_color = color
    def get_drawing_color(self): return self.current_color
    def set_brush_size(self, size): self.brush_radius = size

    def resize_all(self, w, h, resample):
        for l in self.layers: l['image'] = l['image'].resize((w, h), resample)
        self.original_background = self.original_background.resize((w, h), resample)

    def rotate_all(self, angle, expand=True):
        for l in self.layers: l['image'] = l['image'].rotate(angle, expand=expand)
        self.original_background = self.original_background.rotate(angle, expand=expand)

    def mirror_all(self):
        for l in self.layers: l['image'] = ImageOps.mirror(l['image'])
        self.original_background = ImageOps.mirror(self.original_background)

    def draw_on_active_layer(self, position, erase=False):
        self.draw_on_active_layer_line(position, position, erase)

    def draw_on_active_layer_line(self, start, end, erase=False):
        layer = self.get_active_layer()
        if not layer or not layer['visible']: return

        r = self.brush_radius
        width = r * 2
        
        if erase:
            if self.active_index == 0:
                # === СТИРАЧКА НА ФОНІ: ВІДНОВЛЮЄМО З ОРИГІНАЛУ ===
                x1, y1 = start; x2, y2 = end
                left = int(max(0, min(x1, x2) - r*2)); top = int(max(0, min(y1, y2) - r*2))
                right = int(min(layer['image'].width, max(x1, x2) + r*2)); bottom = int(min(layer['image'].height, max(y1, y2) + r*2))
                if right <= left or bottom <= top: return

                w_box, h_box = right - left, bottom - top
                mask = Image.new('L', (w_box, h_box), 0)
                draw = ImageDraw.Draw(mask)
                
                draw.line([(x1-left, y1-top), (x2-left, y2-top)], fill=255, width=width)
                draw.ellipse([(x1-left-r, y1-top-r), (x1-left+r, y1-top+r)], fill=255)
                draw.ellipse([(x2-left-r, y2-top-r), (x2-left+r, y2-top+r)], fill=255)

                orig_crop = self.original_background.crop((left, top, right, bottom))
                curr_crop = layer['image'].crop((left, top, right, bottom))
                restored = Image.composite(orig_crop, curr_crop, mask)
                layer['image'].paste(restored, (left, top))
            
            else:
                # === СТИРАЧКА НА ШАРАХ: ПРОЗОРІСТЬ ===
                if layer['image'].mode == 'RGBA':
                    r_ch, g_ch, b_ch, alpha = layer['image'].split()
                    draw = ImageDraw.Draw(alpha)
                    draw.line([start, end], fill=0, width=width)
                    draw.ellipse([start[0]-r, start[1]-r, start[0]+r, start[1]+r], fill=0)
                    draw.ellipse([end[0]-r, end[1]-r, end[0]+r, end[1]+r], fill=0)
                    layer['image'].putalpha(alpha)
        else:
            # === МАЛЮВАННЯ ===
            draw = ImageDraw.Draw(layer['image'])
            draw.line([start, end], fill=self.current_color, width=width)
            draw.ellipse([start[0]-r, start[1]-r, start[0]+r, start[1]+r], fill=self.current_color)
            draw.ellipse([end[0]-r, end[1]-r, end[0]+r, end[1]+r], fill=self.current_color)

    def get_composite(self):
        w, h = self.layers[0]['image'].size
        # Біла підкладка
        composite = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        for layer in self.layers:
            if layer['visible']:
                composite = Image.alpha_composite(composite, layer['image'])
        return composite