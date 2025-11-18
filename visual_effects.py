# visual_effects.py
import tkinter as tk
import random
import math


class VisualEffects:
    """Клас для візуальних ефектів: тремтіння, частинки, дим"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.particles = []
        self.smoke_effects = []

    def shake_canvas(self, canvas: tk.Canvas, intensity: int = 5, duration: int = 300):
        """Ефект удару - мигання рамки canvas"""
        original_color = canvas.cget('highlightbackground')
        shake_count = 0
        max_flashes = duration // 80

        def flash_step():
            nonlocal shake_count
            if shake_count >= max_flashes:
                # Повертаємо оригінальний колір
                try:
                    canvas.config(highlightbackground=original_color)
                except tk.TclError:
                    pass
                return

            # Чергуємо червоний і оригінальний колір
            try:
                if shake_count % 2 == 0:
                    canvas.config(highlightbackground='#ff0000', highlightthickness=3)
                else:
                    canvas.config(highlightbackground=original_color, highlightthickness=2)
            except tk.TclError:
                return

            shake_count += 1
            self.root.after(80, flash_step)

        flash_step()

    def create_explosion_particles(
        self,
        canvas: tk.Canvas,
        center_x: int,
        center_y: int,
        count: int = 20,
        colors: list = None
    ):
        """Створює частинки вибуху"""
        if colors is None:
            colors = ['#ff6b6b', '#ff9f43', '#ffd166', '#ff4444', '#ffaa00']

        particles_data = []

        for _ in range(count):
            # Випадковий напрямок та швидкість
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            # Розмір частинки
            size = random.randint(3, 8)
            color = random.choice(colors)

            # Створюємо частинку
            particle = canvas.create_oval(
                center_x - size, center_y - size,
                center_x + size, center_y + size,
                fill=color, outline='', tags=('particle',)
            )

            particles_data.append({
                'id': particle,
                'x': center_x,
                'y': center_y,
                'vx': vx,
                'vy': vy,
                'life': 15,  # кількість кадрів життя
                'size': size
            })

        self._animate_particles(canvas, particles_data)

    def _animate_particles(self, canvas: tk.Canvas, particles_data: list, frame: int = 0):
        """Анімує частинки"""
        if frame > 20 or not particles_data:
            # Видаляємо всі частинки
            try:
                canvas.delete('particle')
            except tk.TclError:
                pass
            return

        alive_particles = []

        for particle in particles_data:
            particle['life'] -= 1
            if particle['life'] <= 0:
                try:
                    canvas.delete(particle['id'])
                except tk.TclError:
                    pass
                continue

            # Оновлюємо позицію
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            # Гравітація
            particle['vy'] += 0.3

            # Затухання швидкості
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95

            # Зменшуємо розмір
            particle['size'] *= 0.92

            try:
                # Оновлюємо позицію на canvas
                canvas.coords(
                    particle['id'],
                    particle['x'] - particle['size'],
                    particle['y'] - particle['size'],
                    particle['x'] + particle['size'],
                    particle['y'] + particle['size']
                )
                alive_particles.append(particle)
            except tk.TclError:
                pass

        if alive_particles:
            self.root.after(30, lambda: self._animate_particles(canvas, alive_particles, frame + 1))

    def animate_ship_sinking(
        self,
        canvas: tk.Canvas,
        coordinates: list,
        cell_size: int,
        callback=None
    ):
        """Анімація вибуху корабля - блимання, вибух, розлітання"""
        # Фаза 1: Блимання червоним (3 рази)
        self._flash_ship(canvas, coordinates, cell_size, 0, 6,
                        lambda: self._explode_ship(canvas, coordinates, cell_size, callback))

    def _flash_ship(self, canvas: tk.Canvas, coordinates: list, cell_size: int,
                   flash_count: int, max_flashes: int, next_callback):
        """Блимання корабля перед вибухом"""
        if flash_count >= max_flashes:
            next_callback()
            return

        # Створюємо блимаючі прямокутники
        for x, y in coordinates:
            x1 = x * cell_size
            y1 = y * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            color = '#ffff00' if flash_count % 2 == 0 else '#ff0000'

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline='',
                tags=('flash_ship',)
            )

        # Видаляємо через короткий час
        self.root.after(80, lambda: canvas.delete('flash_ship'))
        self.root.after(80, lambda: self._flash_ship(canvas, coordinates, cell_size,
                                                      flash_count + 1, max_flashes, next_callback))

    def _explode_ship(self, canvas: tk.Canvas, coordinates: list, cell_size: int, callback):
        """Вибух корабля з розлітанням частин"""
        # Центр вибуху
        center_x = sum(x for x, y in coordinates) * cell_size // len(coordinates) + cell_size // 2
        center_y = sum(y for x, y in coordinates) * cell_size // len(coordinates) + cell_size // 2

        # Ударна хвиля (розширюється)
        self._create_shockwave(canvas, center_x, center_y)

        # Створюємо великий вибух в центрі
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.randint(4, 12)

            particle = canvas.create_oval(
                center_x - size, center_y - size,
                center_x + size, center_y + size,
                fill=random.choice(['#ff6b00', '#ff0000', '#ffaa00', '#fff', '#ff9f43']),
                outline='',
                tags=('explosion_particle',)
            )

        # Створюємо частини корабля що розлітаються
        ship_pieces = []
        for x, y in coordinates:
            cx = x * cell_size + cell_size // 2
            cy = y * cell_size + cell_size // 2

            # Напрямок від центру вибуху
            dx = cx - center_x
            dy = cy - center_y
            distance = math.sqrt(dx*dx + dy*dy) or 1

            # Нормалізуємо і додаємо швидкість
            vx = (dx / distance) * random.uniform(4, 8)
            vy = (dy / distance) * random.uniform(4, 8)

            # Створюємо уламок корабля
            piece_size = cell_size // 3
            piece = canvas.create_rectangle(
                cx - piece_size, cy - piece_size,
                cx + piece_size, cy + piece_size,
                fill='#2d3436',
                outline='#1a1a1a',
                tags=('ship_piece',)
            )

            ship_pieces.append({
                'id': piece,
                'x': cx,
                'y': cy,
                'vx': vx,
                'vy': vy,
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-20, 20),
                'life': 20
            })

        # Анімуємо розлітання
        self._animate_explosion(canvas, ship_pieces, 0, callback)

    def _animate_explosion(self, canvas: tk.Canvas, ship_pieces: list, frame: int, callback):
        """Анімує розлітання уламків"""
        if frame >= 20:
            # Видаляємо все
            try:
                canvas.delete('ship_piece')
                canvas.delete('explosion_particle')
            except tk.TclError:
                pass
            # Викликаємо callback
            if callback:
                callback()
            return

        alive_pieces = []

        for piece in ship_pieces:
            piece['life'] -= 1
            if piece['life'] <= 0:
                try:
                    canvas.delete(piece['id'])
                except tk.TclError:
                    pass
                continue

            # Оновлюємо позицію
            piece['x'] += piece['vx']
            piece['y'] += piece['vy']

            # Гравітація і затухання
            piece['vy'] += 0.5
            piece['vx'] *= 0.95
            piece['vy'] *= 0.95

            # Обертання
            piece['rotation'] += piece['rotation_speed']

            try:
                # Оновлюємо позицію уламка
                piece_size = 10
                canvas.coords(
                    piece['id'],
                    piece['x'] - piece_size,
                    piece['y'] - piece_size,
                    piece['x'] + piece_size,
                    piece['y'] + piece_size
                )

                # Затемнюємо з часом
                progress = frame / 20
                darkness = int(45 * (1 - progress))
                canvas.itemconfig(piece['id'], fill=f'#{darkness:02x}{darkness:02x}{darkness:02x}')

                alive_pieces.append(piece)
            except tk.TclError:
                pass

        if alive_pieces or frame < 20:
            self.root.after(50, lambda: self._animate_explosion(canvas, alive_pieces, frame + 1, callback))

    def _create_shockwave(self, canvas: tk.Canvas, center_x: int, center_y: int):
        """Створює ударну хвилю що розширюється"""
        # Створюємо кілька кіл що розширюються
        shockwave_circles = []
        for i in range(3):
            circle = canvas.create_oval(
                center_x - 5, center_y - 5,
                center_x + 5, center_y + 5,
                outline='#ffaa00',
                width=3,
                tags=('shockwave',)
            )
            shockwave_circles.append({
                'id': circle,
                'radius': 5,
                'delay': i * 2
            })

        self._animate_shockwave(canvas, shockwave_circles, center_x, center_y, 0)

    def _animate_shockwave(self, canvas: tk.Canvas, circles: list, cx: int, cy: int, frame: int):
        """Анімує розширення ударної хвилі"""
        if frame >= 15:
            try:
                canvas.delete('shockwave')
            except tk.TclError:
                pass
            return

        for circle_data in circles:
            if frame < circle_data['delay']:
                continue

            actual_frame = frame - circle_data['delay']
            circle_data['radius'] += 8

            # Затухання
            alpha = max(0, 1 - actual_frame / 15)
            width = max(1, int(3 * alpha))

            try:
                canvas.coords(
                    circle_data['id'],
                    cx - circle_data['radius'],
                    cy - circle_data['radius'],
                    cx + circle_data['radius'],
                    cy + circle_data['radius']
                )
                canvas.itemconfig(circle_data['id'], width=width)
            except tk.TclError:
                pass

        self.root.after(40, lambda: self._animate_shockwave(canvas, circles, cx, cy, frame + 1))

    def create_smoke_effect(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        cell_size: int,
        duration: int = 5000
    ):
        """Створює димовий ефект на клітинці"""
        smoke_id = f"smoke_{x}_{y}"
        center_x = x * cell_size + cell_size // 2
        center_y = y * cell_size + cell_size // 2

        # Створюємо кілька хмарок диму
        smoke_items = []
        for i in range(3):
            offset_x = random.randint(-cell_size//4, cell_size//4)
            offset_y = random.randint(-cell_size//4, cell_size//4)
            size = cell_size // 2 + random.randint(-5, 5)

            smoke = canvas.create_oval(
                center_x + offset_x - size,
                center_y + offset_y - size,
                center_x + offset_x + size,
                center_y + offset_y + size,
                fill='#555555',
                outline='',
                stipple='gray50',
                tags=(smoke_id, 'smoke_effect')
            )
            smoke_items.append({
                'id': smoke,
                'x': center_x + offset_x,
                'y': center_y + offset_y,
                'size': size,
                'alpha': 1.0
            })

        self._animate_smoke(canvas, smoke_items, smoke_id, 0, duration // 100)

        # Видалимо дим через заданий час
        def remove_smoke():
            try:
                canvas.delete(smoke_id)
            except tk.TclError:
                pass

        self.root.after(duration, remove_smoke)

    def _animate_smoke(self, canvas: tk.Canvas, smoke_items: list, smoke_id: str, frame: int, max_frames: int):
        """Анімує дим (піднімається вгору)"""
        if frame >= max_frames:
            return

        for smoke in smoke_items:
            # Підніммаємо вгору
            smoke['y'] -= 0.5
            smoke['size'] *= 1.01  # Трохи збільшуємо

            try:
                canvas.coords(
                    smoke['id'],
                    smoke['x'] - smoke['size'],
                    smoke['y'] - smoke['size'],
                    smoke['x'] + smoke['size'],
                    smoke['y'] + smoke['size']
                )
            except tk.TclError:
                return

        self.root.after(100, lambda: self._animate_smoke(canvas, smoke_items, smoke_id, frame + 1, max_frames))

    def create_water_waves(self, canvas: tk.Canvas, board_size: int, cell_size: int):
        """Створює анімацію хвиль на фоні"""
        canvas_width = board_size * cell_size
        canvas_height = board_size * cell_size

        # Створюємо кілька хвильових ліній
        wave_lines = []
        for i in range(5):
            y_pos = (i + 1) * canvas_height // 6
            wave_line = canvas.create_line(
                0, y_pos,
                canvas_width, y_pos,
                fill='#0a3d62',
                width=1,
                tags=('wave_bg',)
            )
            wave_lines.append({'id': wave_line, 'base_y': y_pos, 'offset': i * 1.5})

        self._animate_waves(canvas, wave_lines, 0, canvas_width)

    def _animate_waves(self, canvas: tk.Canvas, wave_lines: list, frame: int, canvas_width: int):
        """Анімує хвилі"""
        if not wave_lines:
            return

        for wave in wave_lines:
            # Обчислюємо хвильову форму
            points = []
            for x in range(0, canvas_width, 20):
                wave_offset = math.sin((x / 50) + (frame / 10) + wave['offset']) * 3
                points.extend([x, wave['base_y'] + wave_offset])

            if points:
                try:
                    canvas.coords(wave['id'], *points)
                except tk.TclError:
                    return

        self.root.after(50, lambda: self._animate_waves(canvas, wave_lines, frame + 1, canvas_width))

    def create_hit_flash(self, canvas: tk.Canvas, x: int, y: int, cell_size: int, color: str = '#ffff00'):
        """Створює спалах при попаданні"""
        center_x = x * cell_size + cell_size // 2
        center_y = y * cell_size + cell_size // 2

        # Створюємо спалах
        flash = canvas.create_oval(
            center_x - cell_size//2,
            center_y - cell_size//2,
            center_x + cell_size//2,
            center_y + cell_size//2,
            fill=color,
            outline='',
            stipple='gray25',
            tags=('flash_effect',)
        )

        # Анімуємо розширення та зникнення
        self._animate_flash(canvas, flash, center_x, center_y, cell_size//2, 0)

    def _animate_flash(self, canvas: tk.Canvas, flash_id: int, center_x: int, center_y: int, start_size: int, frame: int):
        """Анімує спалах"""
        if frame >= 8:
            try:
                canvas.delete(flash_id)
            except tk.TclError:
                pass
            return

        # Збільшуємо розмір
        size = start_size + frame * 5

        try:
            canvas.coords(
                flash_id,
                center_x - size,
                center_y - size,
                center_x + size,
                center_y + size
            )
        except tk.TclError:
            return

        self.root.after(40, lambda: self._animate_flash(canvas, flash_id, center_x, center_y, start_size, frame + 1))
