# ai_robot.py
import math
import random
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from battleship import Board


class AIRobot:
    """Анімований робот-противник, що відображається у правому куті екрану."""

    def __init__(
        self,
        parent_frame: tk.Frame,
        difficulty: str = "easy",
    ):
        self.parent_frame = parent_frame
        self.difficulty = difficulty
        self.active = True
        self.animation_phase = 0
        self.current_emotion = "angry"  # neutral, happy, angry, thinking, scared - починаємо зі злого!

        # Розміри canvas (зменшені для аватара)
        self.canvas_width = 180
        self.canvas_height = 200

        # Створюємо canvas для робота
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
            "body": "#4a5568",
            "body_light": "#6b7280",
            "body_dark": "#2d3748",
            "accent": "#00d4ff",
            "accent_glow": "#00a8cc",
            "eye": "#00ff88",
            "eye_angry": "#ff4444",
            "eye_scared": "#ffd700",
            "antenna": "#ff8800",
            "text": "#ffffff",
        }

        self._blink_timer = random.randint(60, 100)
        self._blink_frames_remaining = 0
        self._blink_frames_total = 4
        self._idle_job = None

        # Текст діалогу
        self.dialogue_text = ""
        self.dialogue_visible = False

        # Центр робота
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2

        # Коефіцієнт масштабування (180/280 ≈ 0.64)
        self.scale = 0.64

        # Запускаємо анімацію
        self.animate_idle()

    def set_emotion(self, emotion: str):
        """Встановлює емоцію робота: neutral, happy, angry, thinking, scared"""
        self.current_emotion = emotion

    def show_dialogue(self, text: str, duration: int = 3000):
        """Показує діалог на певний час (в мілісекундах)"""
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

        # Вертикальне покачування
        body_offset = math.sin(self.animation_phase / 15) * 4

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

        self._draw_robot(body_offset, eye_state)
        self._idle_job = self.parent_frame.after(80, self.animate_idle)

    def _draw_robot(self, body_offset: float, eye_state: str):
        """Малює робота"""
        self.canvas.delete("all")
        p = self.palette

        # Фон
        self.canvas.create_rectangle(
            0, 0, self.canvas_width, self.canvas_height,
            fill=p["background"], outline=""
        )

        # Тіло робота (прямокутник з закругленнями) - масштабування
        body_y = self.center_y + body_offset
        body_width = int(140 * self.scale)
        body_height = int(180 * self.scale)

        # Головне тіло
        self.canvas.create_rectangle(
            self.center_x - body_width//2,
            body_y - body_height//2,
            self.center_x + body_width//2,
            body_y + body_height//2,
            fill=p["body"],
            outline=p["body_dark"],
            width=int(3 * self.scale)
        )

        # Деталі корпусу
        for i in range(3):
            y_pos = body_y - int(40 * self.scale) + i * int(30 * self.scale)
            self.canvas.create_rectangle(
                self.center_x - int(50 * self.scale),
                y_pos,
                self.center_x + int(50 * self.scale),
                y_pos + int(15 * self.scale),
                fill=p["body_dark"],
                outline=""
            )

        # Антена
        antenna_y = body_y - body_height//2 - int(30 * self.scale)
        self.canvas.create_line(
            self.center_x,
            body_y - body_height//2,
            self.center_x,
            antenna_y,
            fill=p["antenna"],
            width=int(3 * self.scale)
        )
        # Лампочка на антені (пульсує)
        pulse = abs(math.sin(self.animation_phase / 10))
        lamp_color = self._interpolate_color("#ff8800", "#ffff00", pulse)
        lamp_radius = int(8 * self.scale)
        self.canvas.create_oval(
            self.center_x - lamp_radius,
            antenna_y - lamp_radius * 2,
            self.center_x + lamp_radius,
            antenna_y,
            fill=lamp_color,
            outline=p["antenna"],
            width=int(2 * self.scale)
        )

        # Голова (екран)
        head_y = body_y - int(50 * self.scale)
        head_width = int(120 * self.scale)
        head_height = int(80 * self.scale)

        self.canvas.create_rectangle(
            self.center_x - head_width//2,
            head_y - head_height//2,
            self.center_x + head_width//2,
            head_y + head_height//2,
            fill=p["body_light"],
            outline=p["accent"],
            width=int(2 * self.scale)
        )

        # Екран
        screen_margin = int(10 * self.scale)
        self.canvas.create_rectangle(
            self.center_x - head_width//2 + screen_margin,
            head_y - head_height//2 + screen_margin,
            self.center_x + head_width//2 - screen_margin,
            head_y + head_height//2 - screen_margin,
            fill="#0a0a0a",
            outline=""
        )

        # Очі
        self._draw_eyes(head_y, eye_state)

        # Руки (масштабовані)
        arm_y = body_y + int(10 * self.scale)
        arm_length = int(50 * self.scale)
        arm_angle = math.sin(self.animation_phase / 20) * 0.2

        # Ліва рука
        left_arm_x = self.center_x - body_width//2 - arm_length
        self.canvas.create_line(
            self.center_x - body_width//2,
            arm_y,
            left_arm_x + arm_length * math.cos(arm_angle),
            arm_y + arm_length * math.sin(arm_angle),
            fill=p["body"],
            width=int(8 * self.scale),
            capstyle=tk.ROUND
        )
        # Кисть
        hand_radius = int(8 * self.scale)
        self.canvas.create_oval(
            left_arm_x - hand_radius + arm_length * math.cos(arm_angle),
            arm_y - hand_radius + arm_length * math.sin(arm_angle),
            left_arm_x + hand_radius + arm_length * math.cos(arm_angle),
            arm_y + hand_radius + arm_length * math.sin(arm_angle),
            fill=p["body_light"],
            outline=p["body_dark"],
            width=int(2 * self.scale)
        )

        # Права рука
        right_arm_x = self.center_x + body_width//2 + arm_length
        self.canvas.create_line(
            self.center_x + body_width//2,
            arm_y,
            right_arm_x - arm_length * math.cos(arm_angle),
            arm_y - arm_length * math.sin(arm_angle),
            fill=p["body"],
            width=int(8 * self.scale),
            capstyle=tk.ROUND
        )
        # Кисть
        self.canvas.create_oval(
            right_arm_x - hand_radius - arm_length * math.cos(arm_angle),
            arm_y - hand_radius - arm_length * math.sin(arm_angle),
            right_arm_x + hand_radius - arm_length * math.cos(arm_angle),
            arm_y + hand_radius - arm_length * math.sin(arm_angle),
            fill=p["body_light"],
            outline=p["body_dark"],
            width=int(2 * self.scale)
        )

        # Ноги (гусениці) - масштабовані
        leg_y = body_y + body_height//2
        leg_width = int(40 * self.scale)
        leg_height = int(30 * self.scale)
        leg_spacing = int(20 * self.scale)

        self.canvas.create_rectangle(
            self.center_x - leg_width - leg_spacing,
            leg_y,
            self.center_x - leg_spacing,
            leg_y + leg_height,
            fill=p["body_dark"],
            outline=p["accent"],
            width=int(2 * self.scale)
        )
        self.canvas.create_rectangle(
            self.center_x + leg_spacing,
            leg_y,
            self.center_x + leg_spacing + leg_width,
            leg_y + leg_height,
            fill=p["body_dark"],
            outline=p["accent"],
            width=int(2 * self.scale)
        )

        # Індикатор складності
        difficulty_text = "😴 EASY" if self.difficulty == "easy" else "💀 HARD"
        self.canvas.create_text(
            self.center_x,
            leg_y + int(40 * self.scale),
            text=difficulty_text,
            font=("Arial", int(12 * self.scale), "bold"),
            fill=p["accent"]
        )

        # Діалог
        if self.dialogue_visible and self.dialogue_text:
            self._draw_dialogue_bubble()

    def _draw_eyes(self, head_y: float, eye_state: str):
        """Малює очі робота"""
        p = self.palette

        # Визначаємо колір очей в залежності від емоції
        if self.current_emotion == "angry":
            eye_color = p["eye_angry"]
        elif self.current_emotion == "scared":
            eye_color = p["eye_scared"]
        else:
            eye_color = p["eye"]

        eye_y = head_y
        eye_spacing = int(30 * self.scale)
        eye_width = int(20 * self.scale)
        eye_height = int(25 * self.scale)

        if eye_state == "closed":
            # Закриті очі (лінії)
            self.canvas.create_line(
                self.center_x - eye_spacing - eye_width,
                eye_y,
                self.center_x - eye_spacing + eye_width,
                eye_y,
                fill=eye_color,
                width=int(3 * self.scale),
                capstyle=tk.ROUND
            )
            self.canvas.create_line(
                self.center_x + eye_spacing - eye_width,
                eye_y,
                self.center_x + eye_spacing + eye_width,
                eye_y,
                fill=eye_color,
                width=int(3 * self.scale),
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
                    fill=eye_color,
                    outline=""
                )
        else:
            # Відкриті очі
            if self.current_emotion == "happy":
                # Щасливі очі (дуги)
                for x_offset in [-eye_spacing, eye_spacing]:
                    self.canvas.create_arc(
                        self.center_x + x_offset - eye_width,
                        eye_y - eye_height,
                        self.center_x + x_offset + eye_width,
                        eye_y + eye_height,
                        start=180,
                        extent=180,
                        style=tk.ARC,
                        outline=eye_color,
                        width=5
                    )
            elif self.current_emotion == "angry":
                # Злі очі (трикутники) - масштабовані
                for x_offset in [-eye_spacing, eye_spacing]:
                    direction = 1 if x_offset < 0 else -1
                    self.canvas.create_polygon(
                        self.center_x + x_offset - eye_width//2,
                        eye_y + eye_height//2,
                        self.center_x + x_offset + eye_width//2,
                        eye_y + eye_height//2,
                        self.center_x + x_offset + direction * eye_width//2,
                        eye_y - eye_height//2,
                        fill=eye_color,
                        outline="",
                        width=int(2 * self.scale)
                    )
            else:
                # Звичайні очі (прямокутники)
                for x_offset in [-eye_spacing, eye_spacing]:
                    self.canvas.create_rectangle(
                        self.center_x + x_offset - eye_width//2,
                        eye_y - eye_height//2,
                        self.center_x + x_offset + eye_width//2,
                        eye_y + eye_height//2,
                        fill=eye_color,
                        outline=""
                    )

    def _draw_dialogue_bubble(self):
        """Малює діалогове вікно (масштабоване)"""
        # Позиція вікна (зліва від робота)
        bubble_x = int(10 * self.scale)
        bubble_y = int(15 * self.scale)
        bubble_width = self.canvas_width - int(20 * self.scale)
        bubble_height = int(60 * self.scale)

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

        # Текст (збільшений шрифт)
        self.canvas.create_text(
            bubble_x + bubble_width//2,
            bubble_y + bubble_height//2,
            text=self.dialogue_text,
            font=("Arial", max(10, int(12 * self.scale)), "bold"),
            fill=self.palette["text"],
            width=bubble_width - int(10 * self.scale)
        )

    def _interpolate_color(self, color1: str, color2: str, t: float) -> str:
        """Інтерполює між двома кольорами"""
        # Перетворюємо hex в RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

        # Інтерполюємо
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        return f"#{r:02x}{g:02x}{b:02x}"

    def destroy(self):
        """Знищує робота"""
        self.active = False
        if self._idle_job is not None:
            try:
                self.parent_frame.after_cancel(self._idle_job)
            except tk.TclError:
                pass
            self._idle_job = None
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.destroy()
