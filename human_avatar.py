# human_avatar.py
import math
import random
import tkinter as tk


class HumanAvatar:
    """Анімований аватар гравця - морський капітан."""

    def __init__(self, parent_frame: tk.Frame):
        self.parent_frame = parent_frame
        self.active = True
        self.animation_phase = 0
        self.current_emotion = "confident"  # confident, happy, worried, determined, victorious

        # Розміри canvas (такі ж як у робота)
        self.canvas_width = 180
        self.canvas_height = 200

        # Створюємо canvas для аватара
        self.canvas = tk.Canvas(
            parent_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#1a1a2e",
            highlightthickness=0,
        )
        self.canvas.pack(expand=True, pady=5)

        # Колірна палітра
        self.palette = {
            "background": "#1a1a2e",
            "skin": "#ffcc99",
            "skin_shadow": "#e6b380",
            "uniform_blue": "#1e3a5f",
            "uniform_light": "#2e5a8f",
            "gold": "#ffd700",
            "white": "#ffffff",
            "hat_dark": "#1a1a3e",
            "eye_white": "#ffffff",
            "eye_blue": "#4a90e2",
            "pupil": "#1a1a1a",
            "beard": "#8b7355",
            "accent": "#00ff88",
            "text": "#ffffff",
        }

        self._blink_timer = random.randint(60, 100)
        self._blink_frames_remaining = 0
        self._blink_frames_total = 4
        self._idle_job = None

        # Текст діалогу
        self.dialogue_text = ""
        self.dialogue_visible = False

        # Центр
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2

        # Коефіцієнт масштабування
        self.scale = 0.64

        # Запускаємо анімацію
        self.animate_idle()

    def set_emotion(self, emotion: str):
        """Встановлює емоцію: confident, happy, worried, determined, victorious"""
        self.current_emotion = emotion

    def show_dialogue(self, text: str, duration: int = 3000):
        """Показує діалог на певний час"""
        self.dialogue_text = text
        self.dialogue_visible = True
        if duration > 0:
            self.parent_frame.after(duration, self.hide_dialogue)

    def hide_dialogue(self):
        """Ховає діалог"""
        self.dialogue_visible = False
        self.dialogue_text = ""

    def animate_idle(self):
        """Анімація стану спокою"""
        if not self.active:
            return

        self.animation_phase = (self.animation_phase + 1) % 1024

        # Легке покачування
        body_offset = math.sin(self.animation_phase / 18) * 3

        # Моргання
        if self._blink_frames_remaining > 0:
            frame_index = self._blink_frames_total - self._blink_frames_remaining
            eye_state = "half" if frame_index in (0, self._blink_frames_total - 1) else "closed"
            self._blink_frames_remaining -= 1
            if self._blink_frames_remaining == 0:
                self._blink_timer = random.randint(60, 100)
        else:
            if self._blink_timer <= 0:
                self._blink_frames_remaining = self._blink_frames_total
                eye_state = "half"
            else:
                self._blink_timer -= 1
                eye_state = "open"

        self._draw_captain(body_offset, eye_state)
        self._idle_job = self.parent_frame.after(80, self.animate_idle)

    def _draw_captain(self, body_offset: float, eye_state: str):
        """Малює капітана"""
        self.canvas.delete("all")
        p = self.palette

        # Фон
        self.canvas.create_rectangle(
            0, 0, self.canvas_width, self.canvas_height,
            fill=p["background"], outline=""
        )

        # Позиція
        body_y = self.center_y + body_offset

        # Тіло (уніформа)
        body_width = int(100 * self.scale)
        body_height = int(140 * self.scale)

        # Торс
        self.canvas.create_rectangle(
            self.center_x - body_width//2,
            body_y - body_height//2,
            self.center_x + body_width//2,
            body_y + body_height//2,
            fill=p["uniform_blue"],
            outline=p["uniform_light"],
            width=int(2 * self.scale)
        )

        # Золоті погони
        epaulet_width = int(30 * self.scale)
        epaulet_height = int(10 * self.scale)
        shoulder_y = body_y - body_height//2 + int(15 * self.scale)

        for x_offset in [-body_width//2 + int(10 * self.scale), body_width//2 - int(10 * self.scale)]:
            self.canvas.create_rectangle(
                self.center_x + x_offset - epaulet_width//2,
                shoulder_y,
                self.center_x + x_offset + epaulet_width//2,
                shoulder_y + epaulet_height,
                fill=p["gold"],
                outline=p["gold"]
            )

        # Золоті гудзики
        button_positions = [0, int(25 * self.scale), int(50 * self.scale)]
        button_radius = int(4 * self.scale)
        for offset_y in button_positions:
            self.canvas.create_oval(
                self.center_x - button_radius,
                body_y - int(30 * self.scale) + offset_y - button_radius,
                self.center_x + button_radius,
                body_y - int(30 * self.scale) + offset_y + button_radius,
                fill=p["gold"],
                outline=""
            )

        # Голова
        head_y = body_y - body_height//2 - int(40 * self.scale)
        head_radius = int(35 * self.scale)

        # Обличчя (коло)
        self.canvas.create_oval(
            self.center_x - head_radius,
            head_y - head_radius,
            self.center_x + head_radius,
            head_y + head_radius,
            fill=p["skin"],
            outline=p["skin_shadow"],
            width=int(2 * self.scale)
        )

        # Капітанський капелюх
        hat_width = int(80 * self.scale)
        hat_height = int(25 * self.scale)
        hat_top_y = head_y - head_radius - int(5 * self.scale)

        # Поля капелюха
        self.canvas.create_oval(
            self.center_x - hat_width//2,
            hat_top_y - int(8 * self.scale),
            self.center_x + hat_width//2,
            hat_top_y + int(8 * self.scale),
            fill=p["hat_dark"],
            outline=""
        )

        # Верх капелюха
        self.canvas.create_rectangle(
            self.center_x - int(30 * self.scale),
            hat_top_y - hat_height,
            self.center_x + int(30 * self.scale),
            hat_top_y,
            fill=p["hat_dark"],
            outline=""
        )

        # Золота кокарда на капелюсі
        self.canvas.create_oval(
            self.center_x - int(8 * self.scale),
            hat_top_y - int(15 * self.scale),
            self.center_x + int(8 * self.scale),
            hat_top_y - int(5 * self.scale),
            fill=p["gold"],
            outline=""
        )

        # Очі
        self._draw_eyes(head_y, eye_state)

        # Ніс
        nose_y = head_y + int(5 * self.scale)
        nose_width = int(8 * self.scale)
        nose_height = int(12 * self.scale)
        self.canvas.create_oval(
            self.center_x - nose_width//2,
            nose_y - nose_height//2,
            self.center_x + nose_width//2,
            nose_y + nose_height//2,
            fill=p["skin_shadow"],
            outline=""
        )

        # Рот (залежить від емоції)
        self._draw_mouth(head_y)

        # Борода/вуса
        beard_y = head_y + int(20 * self.scale)
        beard_width = int(40 * self.scale)
        beard_height = int(15 * self.scale)

        # Вуса
        mustache_width = int(25 * self.scale)
        mustache_y = head_y + int(15 * self.scale)
        self.canvas.create_arc(
            self.center_x - mustache_width,
            mustache_y - int(8 * self.scale),
            self.center_x,
            mustache_y + int(8 * self.scale),
            start=0,
            extent=180,
            fill=p["beard"],
            outline=p["beard"],
            style=tk.CHORD
        )
        self.canvas.create_arc(
            self.center_x,
            mustache_y - int(8 * self.scale),
            self.center_x + mustache_width,
            mustache_y + int(8 * self.scale),
            start=0,
            extent=180,
            fill=p["beard"],
            outline=p["beard"],
            style=tk.CHORD
        )

        # Невелика борідка
        self.canvas.create_oval(
            self.center_x - int(10 * self.scale),
            beard_y,
            self.center_x + int(10 * self.scale),
            beard_y + beard_height,
            fill=p["beard"],
            outline=""
        )

        # Ранг (зірки на уніформі)
        self.canvas.create_text(
            self.center_x,
            body_y + body_height//2 + int(25 * self.scale),
            text="⭐ КАПІТАН ⭐",
            font=("Arial", int(7 * self.scale), "bold"),
            fill=p["gold"]
        )

        # Діалог
        if self.dialogue_visible and self.dialogue_text:
            self._draw_dialogue_bubble()

    def _draw_eyes(self, head_y: float, eye_state: str):
        """Малює очі"""
        p = self.palette

        eye_y = head_y - int(5 * self.scale)
        eye_spacing = int(20 * self.scale)
        eye_width = int(12 * self.scale)
        eye_height = int(16 * self.scale)

        if eye_state == "closed":
            # Закриті очі
            for x_offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_line(
                    self.center_x + x_offset - eye_width,
                    eye_y,
                    self.center_x + x_offset + eye_width,
                    eye_y,
                    fill=p["pupil"],
                    width=int(2 * self.scale),
                    capstyle=tk.ROUND
                )
        elif eye_state == "half":
            # Напіввідкриті
            for x_offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_rectangle(
                    self.center_x + x_offset - eye_width//2,
                    eye_y - eye_height//4,
                    self.center_x + x_offset + eye_width//2,
                    eye_y + eye_height//4,
                    fill=p["eye_white"],
                    outline=""
                )
        else:
            # Відкриті очі
            for x_offset in [-eye_spacing, eye_spacing]:
                # Біле очей
                self.canvas.create_oval(
                    self.center_x + x_offset - eye_width//2,
                    eye_y - eye_height//2,
                    self.center_x + x_offset + eye_width//2,
                    eye_y + eye_height//2,
                    fill=p["eye_white"],
                    outline=""
                )
                # Райдужка
                pupil_size = int(6 * self.scale)
                self.canvas.create_oval(
                    self.center_x + x_offset - pupil_size//2,
                    eye_y - pupil_size//2,
                    self.center_x + x_offset + pupil_size//2,
                    eye_y + pupil_size//2,
                    fill=p["eye_blue"],
                    outline=""
                )
                # Зіниця
                pupil_mini = int(3 * self.scale)
                self.canvas.create_oval(
                    self.center_x + x_offset - pupil_mini//2,
                    eye_y - pupil_mini//2,
                    self.center_x + x_offset + pupil_mini//2,
                    eye_y + pupil_mini//2,
                    fill=p["pupil"],
                    outline=""
                )
                # Відблиск
                highlight = int(2 * self.scale)
                self.canvas.create_oval(
                    self.center_x + x_offset - pupil_mini//2 - highlight,
                    eye_y - pupil_mini//2 - highlight,
                    self.center_x + x_offset - pupil_mini//2,
                    eye_y - pupil_mini//2,
                    fill=p["white"],
                    outline=""
                )

    def _draw_mouth(self, head_y: float):
        """Малює рот залежно від емоції"""
        p = self.palette
        mouth_y = head_y + int(15 * self.scale)
        mouth_width = int(20 * self.scale)

        if self.current_emotion in ("happy", "victorious"):
            # Усміхнений рот (дуга вгору)
            self.canvas.create_arc(
                self.center_x - mouth_width,
                mouth_y - int(10 * self.scale),
                self.center_x + mouth_width,
                mouth_y + int(10 * self.scale),
                start=200,
                extent=140,
                style=tk.ARC,
                outline=p["skin_shadow"],
                width=int(3 * self.scale)
            )
        elif self.current_emotion == "worried":
            # Засмучений рот (дуга вниз)
            self.canvas.create_arc(
                self.center_x - mouth_width,
                mouth_y - int(5 * self.scale),
                self.center_x + mouth_width,
                mouth_y + int(15 * self.scale),
                start=20,
                extent=140,
                style=tk.ARC,
                outline=p["skin_shadow"],
                width=int(3 * self.scale)
            )
        elif self.current_emotion == "determined":
            # Рішучий рот (пряма лінія)
            self.canvas.create_line(
                self.center_x - mouth_width,
                mouth_y,
                self.center_x + mouth_width,
                mouth_y,
                fill=p["skin_shadow"],
                width=int(3 * self.scale)
            )
        else:
            # Нейтральний (невелика усмішка)
            self.canvas.create_arc(
                self.center_x - mouth_width,
                mouth_y - int(8 * self.scale),
                self.center_x + mouth_width,
                mouth_y + int(8 * self.scale),
                start=200,
                extent=140,
                style=tk.ARC,
                outline=p["skin_shadow"],
                width=int(2 * self.scale)
            )

    def _draw_dialogue_bubble(self):
        """Малює діалогове вікно"""
        bubble_x = int(10 * self.scale)
        bubble_y = int(15 * self.scale)
        bubble_width = self.canvas_width - int(20 * self.scale)
        bubble_height = int(50 * self.scale)

        # Фон вікна
        self.canvas.create_rectangle(
            bubble_x,
            bubble_y,
            bubble_x + bubble_width,
            bubble_y + bubble_height,
            fill="#2d3748",
            outline=self.palette["accent"],
            width=int(2 * self.scale)
        )

        # Трикутник (хвостик)
        tail_size = int(10 * self.scale)
        self.canvas.create_polygon(
            self.center_x - tail_size,
            bubble_y + bubble_height,
            self.center_x + tail_size,
            bubble_y + bubble_height,
            self.center_x,
            bubble_y + bubble_height + int(12 * self.scale),
            fill="#2d3748",
            outline=self.palette["accent"],
            width=int(2 * self.scale)
        )

        # Текст
        self.canvas.create_text(
            bubble_x + bubble_width//2,
            bubble_y + bubble_height//2,
            text=self.dialogue_text,
            font=("Arial", max(6, int(7 * self.scale)), "bold"),
            fill=self.palette["text"],
            width=bubble_width - int(10 * self.scale)
        )

    def destroy(self):
        """Знищує аватар"""
        self.active = False
        if self._idle_job is not None:
            try:
                self.parent_frame.after_cancel(self._idle_job)
            except tk.TclError:
                pass
            self._idle_job = None
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.destroy()
