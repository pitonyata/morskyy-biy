# player_avatar.py
import math
import random
import tkinter as tk


class PlayerAvatar:
    """Анімований аватар гравця-капітана, що відображається у лівому куті екрану."""

    def __init__(self, parent_frame: tk.Frame):
        self.parent_frame = parent_frame
        self.active = True
        self.animation_phase = 0
        self.current_emotion = "neutral"  # neutral, happy, sad, excited, worried, thinking

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

        # Колірна палітра (морська/людська тематика)
        self.palette = {
            "background": "#1a1a2e",
            "skin": "#ffdbac",
            "skin_dark": "#e3b58f",
            "uniform_blue": "#1e3a8a",
            "uniform_light": "#3b82f6",
            "hat_dark": "#1a1a3e",
            "gold": "#ffd700",
            "white": "#ffffff",
            "eye": "#2d3748",
            "eye_happy": "#00ff88",
            "eye_worried": "#ff8800",
            "accent": "#00d4ff",
            "text": "#ffffff",
        }

        self._blink_timer = random.randint(60, 120)
        self._blink_frames_remaining = 0
        self._blink_frames_total = 4
        self._idle_job = None

        # Текст діалогу
        self.dialogue_text = ""
        self.dialogue_visible = False

        # Центр аватара
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2

        # Коефіцієнт масштабування
        self.scale = 0.64

        # Запускаємо анімацію
        self.animate_idle()

    def set_emotion(self, emotion: str):
        """Встановлює емоцію капітана: neutral, happy, sad, excited, worried, thinking"""
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

        # Вертикальне покачування (як на хвилях)
        body_offset = math.sin(self.animation_phase / 15) * 3

        # Моргання
        if self._blink_frames_remaining > 0:
            frame_index = self._blink_frames_total - self._blink_frames_remaining
            eye_state = "half" if frame_index in (0, self._blink_frames_total - 1) else "closed"
            self._blink_frames_remaining -= 1
            if self._blink_frames_remaining == 0:
                self._blink_timer = random.randint(60, 120)
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

        # Тіло капітана (китель/піджак)
        body_y = self.center_y + body_offset + int(20 * self.scale)
        body_width = int(120 * self.scale)
        body_height = int(100 * self.scale)

        # Китель (трапеція)
        self.canvas.create_polygon(
            self.center_x - int(40 * self.scale), body_y - int(20 * self.scale),
            self.center_x + int(40 * self.scale), body_y - int(20 * self.scale),
            self.center_x + int(60 * self.scale), body_y + int(80 * self.scale),
            self.center_x - int(60 * self.scale), body_y + int(80 * self.scale),
            fill=p["uniform_blue"],
            outline=p["uniform_light"],
            width=int(2 * self.scale)
        )

        # Гудзики на кителі
        for i in range(3):
            button_y = body_y + i * int(25 * self.scale)
            button_radius = int(4 * self.scale)
            self.canvas.create_oval(
                self.center_x - button_radius,
                button_y - button_radius,
                self.center_x + button_radius,
                button_y + button_radius,
                fill=p["gold"],
                outline=p["gold"]
            )

        # Комір
        collar_y = body_y - int(20 * self.scale)
        self.canvas.create_polygon(
            self.center_x - int(40 * self.scale), collar_y,
            self.center_x - int(30 * self.scale), collar_y - int(10 * self.scale),
            self.center_x + int(30 * self.scale), collar_y - int(10 * self.scale),
            self.center_x + int(40 * self.scale), collar_y,
            fill=p["uniform_light"],
            outline=""
        )

        # Голова (коло)
        head_y = body_y - int(60 * self.scale)
        head_radius = int(35 * self.scale)

        self.canvas.create_oval(
            self.center_x - head_radius,
            head_y - head_radius,
            self.center_x + head_radius,
            head_y + head_radius,
            fill=p["skin"],
            outline=p["skin_dark"],
            width=int(2 * self.scale)
        )

        # Капітанська кепка
        self._draw_captain_hat(head_y, head_radius)

        # Обличчя (очі, ніс, рот)
        self._draw_face(head_y, eye_state)

        # Руки
        self._draw_arms(body_y, body_offset)

        # Підпис "ГРАВЕЦЬ"
        self.canvas.create_text(
            self.center_x,
            body_y + int(90 * self.scale),
            text="👤 ГРАВЕЦЬ",
            font=("Arial", int(12 * self.scale), "bold"),
            fill=p["accent"]
        )

        # Діалог
        if self.dialogue_visible and self.dialogue_text:
            self._draw_dialogue_bubble()

    def _draw_captain_hat(self, head_y: float, head_radius: int):
        """Малює капітанську кепку"""
        p = self.palette

        # Козирок кепки
        visor_y = head_y - int(5 * self.scale)
        self.canvas.create_oval(
            self.center_x - int(45 * self.scale),
            visor_y - int(8 * self.scale),
            self.center_x + int(45 * self.scale),
            visor_y + int(8 * self.scale),
            fill=p["hat_dark"],
            outline=p["hat_dark"]
        )

        # Верх кепки
        hat_y = head_y - head_radius - int(5 * self.scale)
        self.canvas.create_oval(
            self.center_x - int(40 * self.scale),
            hat_y - int(20 * self.scale),
            self.center_x + int(40 * self.scale),
            hat_y + int(15 * self.scale),
            fill=p["uniform_blue"],
            outline=p["uniform_light"],
            width=int(2 * self.scale)
        )

        # Емблема на кепці (якір)
        anchor_y = hat_y - int(5 * self.scale)
        anchor_size = int(10 * self.scale)
        self.canvas.create_text(
            self.center_x,
            anchor_y,
            text="⚓",
            font=("Arial", anchor_size),
            fill=p["gold"]
        )

    def _draw_face(self, head_y: float, eye_state: str):
        """Малює обличчя капітана"""
        p = self.palette

        # Очі
        self._draw_eyes(head_y, eye_state)

        # Ніс
        nose_y = head_y + int(5 * self.scale)
        nose_size = int(4 * self.scale)
        self.canvas.create_oval(
            self.center_x - nose_size,
            nose_y - nose_size // 2,
            self.center_x + nose_size,
            nose_y + nose_size // 2,
            fill=p["skin_dark"],
            outline=""
        )

        # Рот (залежить від емоції)
        mouth_y = head_y + int(18 * self.scale)
        mouth_width = int(20 * self.scale)
        mouth_height = int(10 * self.scale)

        if self.current_emotion == "happy" or self.current_emotion == "excited":
            # Усмішка
            self.canvas.create_arc(
                self.center_x - mouth_width,
                mouth_y - mouth_height,
                self.center_x + mouth_width,
                mouth_y + mouth_height,
                start=0,
                extent=-180,
                style=tk.ARC,
                outline=p["eye"],
                width=int(3 * self.scale)
            )
        elif self.current_emotion == "sad" or self.current_emotion == "worried":
            # Сумний рот
            self.canvas.create_arc(
                self.center_x - mouth_width,
                mouth_y,
                self.center_x + mouth_width,
                mouth_y + mouth_height * 2,
                start=0,
                extent=180,
                style=tk.ARC,
                outline=p["eye"],
                width=int(3 * self.scale)
            )
        else:
            # Нейтральний рот (пряма лінія)
            self.canvas.create_line(
                self.center_x - mouth_width,
                mouth_y,
                self.center_x + mouth_width,
                mouth_y,
                fill=p["eye"],
                width=int(3 * self.scale)
            )

    def _draw_eyes(self, head_y: float, eye_state: str):
        """Малює очі капітана"""
        p = self.palette

        eye_y = head_y - int(5 * self.scale)
        eye_spacing = int(18 * self.scale)
        eye_radius = int(5 * self.scale)

        if eye_state == "closed":
            # Закриті очі (лінії)
            for x_offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_line(
                    self.center_x + x_offset - eye_radius,
                    eye_y,
                    self.center_x + x_offset + eye_radius,
                    eye_y,
                    fill=p["eye"],
                    width=int(2 * self.scale),
                    capstyle=tk.ROUND
                )
        elif eye_state == "half":
            # Напіввідкриті
            for x_offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_oval(
                    self.center_x + x_offset - eye_radius,
                    eye_y - eye_radius // 2,
                    self.center_x + x_offset + eye_radius,
                    eye_y + eye_radius // 2,
                    fill=p["eye"],
                    outline=""
                )
        else:
            # Відкриті очі
            for x_offset in [-eye_spacing, eye_spacing]:
                # Біла частина ока
                self.canvas.create_oval(
                    self.center_x + x_offset - eye_radius,
                    eye_y - eye_radius,
                    self.center_x + x_offset + eye_radius,
                    eye_y + eye_radius,
                    fill=p["white"],
                    outline=p["eye"],
                    width=int(1 * self.scale)
                )

                # Зіниця
                pupil_radius = int(3 * self.scale)
                pupil_y_offset = 0

                # Для деяких емоцій зіниці дивляться в інший бік
                if self.current_emotion == "worried":
                    pupil_y_offset = -int(2 * self.scale)
                elif self.current_emotion == "thinking":
                    pupil_y_offset = int(2 * self.scale)

                self.canvas.create_oval(
                    self.center_x + x_offset - pupil_radius,
                    eye_y - pupil_radius + pupil_y_offset,
                    self.center_x + x_offset + pupil_radius,
                    eye_y + pupil_radius + pupil_y_offset,
                    fill=p["eye"],
                    outline=""
                )

            # Брови (для емоцій)
            if self.current_emotion == "worried" or self.current_emotion == "sad":
                # Стурбовані брови
                for x_offset in [-eye_spacing, eye_spacing]:
                    direction = 1 if x_offset < 0 else -1
                    self.canvas.create_line(
                        self.center_x + x_offset - eye_radius,
                        eye_y - eye_radius - int(5 * self.scale),
                        self.center_x + x_offset + eye_radius,
                        eye_y - eye_radius - int(5 * self.scale) + direction * int(4 * self.scale),
                        fill=p["eye"],
                        width=int(2 * self.scale)
                    )
            elif self.current_emotion == "excited":
                # Здивовані брови
                for x_offset in [-eye_spacing, eye_spacing]:
                    self.canvas.create_arc(
                        self.center_x + x_offset - eye_radius,
                        eye_y - eye_radius - int(8 * self.scale),
                        self.center_x + x_offset + eye_radius,
                        eye_y - eye_radius,
                        start=0,
                        extent=180,
                        style=tk.ARC,
                        outline=p["eye"],
                        width=int(2 * self.scale)
                    )

    def _draw_arms(self, body_y: float, body_offset: float):
        """Малює руки капітана"""
        p = self.palette

        arm_y = body_y + int(10 * self.scale)
        arm_angle = math.sin(self.animation_phase / 20) * 0.15

        # Ліва рука
        left_arm_end_x = self.center_x - int(80 * self.scale)
        left_arm_end_y = arm_y + int(30 * self.scale) * math.sin(arm_angle)

        self.canvas.create_line(
            self.center_x - int(40 * self.scale),
            arm_y,
            left_arm_end_x,
            left_arm_end_y,
            fill=p["uniform_blue"],
            width=int(10 * self.scale),
            capstyle=tk.ROUND
        )

        # Кисть лівої руки
        hand_radius = int(8 * self.scale)
        self.canvas.create_oval(
            left_arm_end_x - hand_radius,
            left_arm_end_y - hand_radius,
            left_arm_end_x + hand_radius,
            left_arm_end_y + hand_radius,
            fill=p["skin"],
            outline=p["skin_dark"],
            width=int(2 * self.scale)
        )

        # Права рука
        right_arm_end_x = self.center_x + int(80 * self.scale)
        right_arm_end_y = arm_y - int(30 * self.scale) * math.sin(arm_angle)

        self.canvas.create_line(
            self.center_x + int(40 * self.scale),
            arm_y,
            right_arm_end_x,
            right_arm_end_y,
            fill=p["uniform_blue"],
            width=int(10 * self.scale),
            capstyle=tk.ROUND
        )

        # Кисть правої руки
        self.canvas.create_oval(
            right_arm_end_x - hand_radius,
            right_arm_end_y - hand_radius,
            right_arm_end_x + hand_radius,
            right_arm_end_y + hand_radius,
            fill=p["skin"],
            outline=p["skin_dark"],
            width=int(2 * self.scale)
        )

    def _draw_dialogue_bubble(self):
        """Малює діалогове вікно"""
        # Позиція вікна (зверху)
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
            font=("Arial", max(8, int(10 * self.scale)), "bold"),
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
