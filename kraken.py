import math
import random
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from battleship import Board


class Kraken:
    """Animated kraken companion that attacks both boards."""

    def __init__(
        self,
        parent_frame: tk.Frame,
        board_size: int,
        player_board: "Board",
        computer_board: "Board",
        on_attack_callback=None,
        player_canvas: tk.Canvas | None = None,
        computer_canvas: tk.Canvas | None = None,
        cell_size: int | None = None,
    ):
        self.parent_frame = parent_frame
        self.board_size = board_size
        self.player_board = player_board
        self.computer_board = computer_board
        self.on_attack_callback = on_attack_callback
        self.player_canvas_widget = player_canvas
        self.computer_canvas_widget = computer_canvas
        self.cell_size = cell_size

        if board_size == 6:
            self.active = False
            self.canvas = None
            return

        self.active = True
        self.animation_phase = 0
        self.attack_animation_active = False
        self.attack_target = None  # (board, x, y, size)

        self.canvas_width = 360
        self.canvas_height = 260
        self.canvas = tk.Canvas(
            parent_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#1a1a2e",
            highlightthickness=0,
        )
        self.canvas.pack(expand=True, pady=10)

        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2 + 5
        self.palette = {
            "background": "#1a1a2e",
            "glow": "#29122d",
            "body": "#ff2d2d",
            "body_shadow": "#d21b24",
            "outline": "#830f19",
            "highlight": "#ff5454",
            "horn": "#ff3b3b",
            "horn_outline": "#830f19",
            "eye": "#ffe63c",
            "eye_rage": "#ffd047",
            "eye_outline": "#ff9720",
            "pupil": "#100510",
            "pupil_glow": "#fff6b7",
            "eye_closed": "#a31524",
            "tentacle": "#ff2d2d",
            "tentacle_outline": "#b51723",
            "sucker": "#ff7171",
            "sucker_highlight": "#ffd7c8",
            "teeth": "#ff9a7b",
            "teeth_outline": "#82151d",
            "spark": "#ffd166",
            "text_primary": "#3de0ff",
            "text_accent": "#ff5b61",
        }
        self.tentacles = [
            {
                "points": [
                    (-70, -12),
                    (-108, 8),
                    (-122, 34),
                    (-108, 62),
                    (-120, 82),
                    (-92, 96),
                    (-62, 80),
                ],
                "width": 16,
                "amplitude": 11,
                "cups": [(-116, 54), (-118, 74), (-100, 92)],
            },
            {
                "points": [
                    (-48, -6),
                    (-84, 12),
                    (-92, 38),
                    (-78, 64),
                    (-88, 82),
                    (-66, 96),
                    (-38, 78),
                ],
                "width": 14,
                "amplitude": 9,
                "cups": [(-80, 50), (-78, 70), (-62, 90)],
            },
            {
                "points": [
                    (-28, -2),
                    (-50, 16),
                    (-60, 38),
                    (-48, 62),
                    (-56, 82),
                    (-38, 94),
                    (-16, 76),
                ],
                "width": 12,
                "amplitude": 8,
                "cups": [(-46, 52), (-40, 74), (-26, 90)],
            },
            {
                "points": [
                    (-12, 4),
                    (-24, 24),
                    (-30, 46),
                    (-22, 68),
                    (-28, 84),
                    (-12, 96),
                    (6, 76),
                ],
                "width": 10,
                "amplitude": 6,
                "cups": [(-20, 60), (-16, 82)],
            },
        ]
        self.tentacle_phase_offsets = [
            random.uniform(0, 2 * math.pi) for _ in range(len(self.tentacles))
        ]

        self._blink_timer = random.randint(55, 90)
        self._blink_frames_total = 4
        self._blink_frames_remaining = 0
        self._idle_job = None
        self._spawn_job = None

        self.spawn_animation()
        self.schedule_next_attack()

    # ------------------------------------------------------------------ #
    # Spawn and idle animation
    # ------------------------------------------------------------------ #
    def spawn_animation(self):
        if not self.active:
            return
        self.canvas.delete("all")
        self.draw_bubbles()
        self.spawn_progress = 0
        self.spawn_steps = 14

        if self._spawn_job is not None:
            try:
                self.parent_frame.after_cancel(self._spawn_job)
            except tk.TclError:
                pass
        self._spawn_job = self.parent_frame.after(550, self._spawn_step)

    def _spawn_step(self):
        if not self.active:
            return
        if self.spawn_progress >= self.spawn_steps:
            self._spawn_job = None
            self.animate_idle()
            return

        progress = (self.spawn_progress + 1) / self.spawn_steps
        eased = progress**0.9
        wobble = 0.35 * (1 - progress)
        self.animation_phase = (self.animation_phase + 5) % 1024
        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=0.4 + wobble,
            body_offset=(1 - progress) * 26,
            eye_state="half" if progress < 0.6 else "open",
            glow_strength=min(0.3, eased * 0.4),
            reveal_progress=eased,
        )
        self.spawn_progress += 1
        delay = 160 if progress > 0.7 else 120
        self._spawn_job = self.parent_frame.after(delay, self._spawn_step)

    def draw_bubbles(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(
            0,
            0,
            self.canvas_width,
            self.canvas_height,
            outline="",
            fill=self.palette["background"],
        )
        for _ in range(30):
            size = random.randint(6, 16)
            x = random.randint(18, self.canvas_width - 18 - size)
            y = random.randint(24, self.canvas_height - 70 - size)
            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                outline="#3ad1ff",
                fill="#152659",
                width=1,
            )
        self.canvas.create_text(
            self.center_x,
            36,
            text="КРАКЕН ПІДПЛИВАЄ",
            font=("Bahnschrift", 16, "bold"),
            fill=self.palette["text_primary"],
        )

    def draw_tentacles_emerging(self):
        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=0.35,
            body_offset=10,
            eye_state="half",
            glow_strength=0.2,
        )
        self.canvas.create_text(
            self.center_x,
            self.canvas_height - 26,
            text="Він вже тут...",
            font=("Bahnschrift", 12),
            fill=self.palette["text_primary"],
        )

    def draw_kraken_emerging(self):
        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=0.25,
            body_offset=4,
            eye_state="open",
            glow_strength=0.15,
        )
        self.canvas.create_text(
            self.center_x,
            self.canvas_height - 26,
            text="КРАКЕН ГОТОВИЙ",
            font=("Bahnschrift", 12, "bold"),
            fill=self.palette["text_accent"],
        )

    def draw_full_kraken(self):
        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=0.25,
            body_offset=0,
            eye_state="open",
            glow_strength=0.0,
        )

    def animate_idle(self):
        if not self.active or self.attack_animation_active:
            return

        self.animation_phase = (self.animation_phase + 1) % 1024
        body_offset = math.sin(self.animation_phase / 20) * 3.2
        tentacle_wave = 0.75 + 0.2 * math.sin(self.animation_phase / 26)

        if self._blink_frames_remaining > 0:
            frame_index = self._blink_frames_total - self._blink_frames_remaining
            eye_state = (
                "half" if frame_index in (0, self._blink_frames_total - 1) else "closed"
            )
            self._blink_frames_remaining -= 1
            if self._blink_frames_remaining == 0:
                self._blink_timer = random.randint(55, 95)
        else:
            if self._blink_timer <= 0:
                self._blink_frames_remaining = self._blink_frames_total
                eye_state = "half"
            else:
                self._blink_timer -= 1
                eye_state = "open"

        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=tentacle_wave,
            body_offset=body_offset,
            eye_state=eye_state,
            glow_strength=0.0,
        )
        self._idle_job = self.parent_frame.after(90, self.animate_idle)

    # ------------------------------------------------------------------ #
    # Attack animation
    # ------------------------------------------------------------------ #
    def schedule_next_attack(self):
        if not self.active:
            return
        delay = random.randint(8000, 15000)
        self.parent_frame.after(delay, self.execute_attack)

    def execute_attack(self):
        if not self.active or self.attack_animation_active:
            return
        target_board = random.choice([self.player_board, self.computer_board])
        attack_size = 3 if self.board_size == 14 else 1
        max_coord = self.board_size - attack_size
        x = random.randint(0, max_coord)
        y = random.randint(0, max_coord)
        self.attack_target = (target_board, x, y, attack_size)
        self.animate_attack()

    def animate_attack(self):
        self.attack_animation_active = True
        attack_frames = [
            self.draw_attack_charge,
            self.draw_attack_extend,
            self.draw_attack_strike,
            self.draw_attack_return,
        ]

        def animate_attack_sequence(phase: int = 0):
            if not self.active:
                return
            if phase < len(attack_frames):
                attack_frames[phase]()
                self.parent_frame.after(280, lambda: animate_attack_sequence(phase + 1))
            else:
                self.apply_attack_damage()
                self.attack_animation_active = False
                self.animate_idle()
                self.schedule_next_attack()

        animate_attack_sequence()

    def draw_attack_charge(self):
        self.animation_phase = (self.animation_phase + 6) % 1024
        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=1.4,
            body_offset=-6,
            eye_state="rage",
            glow_strength=0.6,
        )
        for idx in range(3):
            radius = 70 + idx * 16
            self.canvas.create_oval(
                self.center_x - radius,
                self.center_y - 60 - idx * 6,
                self.center_x + radius,
                self.center_y + 40 + idx * 6,
                outline=self.palette["text_accent"],
                width=3,
            )
        for _ in range(7):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(60, 85)
            sx = self.center_x + math.cos(angle) * distance
            sy = self.center_y - 18 + math.sin(angle) * distance * 0.6
            self.canvas.create_oval(
                sx - 4,
                sy - 4,
                sx + 4,
                sy + 4,
                fill=self.palette["spark"],
                outline="",
            )
        self.canvas.create_text(
            self.center_x,
            32,
            text="КРАКЕН ЗАРЯДЖАЄТЬСЯ",
            font=("Bahnschrift", 14, "bold"),
            fill=self.palette["text_accent"],
        )

    def draw_attack_extend(self):
        self.animation_phase = (self.animation_phase + 6) % 1024
        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=1.2,
            body_offset=-4,
            eye_state="rage",
            glow_strength=0.45,
            strike=self._build_strike_params(progress=0.75, impact=False),
        )

    def draw_attack_strike(self):
        self.animation_phase = (self.animation_phase + 6) % 1024
        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=1.0,
            body_offset=-2,
            eye_state="rage",
            glow_strength=0.7,
            strike=self._build_strike_params(progress=1.0, impact=True),
        )
        self.canvas.create_text(
            self.center_x,
            34,
            text="КРАКЕН Б’Є!",
            font=("Bahnschrift", 16, "bold"),
            fill=self.palette["text_accent"],
        )

    def draw_attack_return(self):
        self.animation_phase = (self.animation_phase + 4) % 1024
        self._draw_scene(
            phase=self.animation_phase,
            tentacle_wave=0.6,
            body_offset=2,
            eye_state="open",
            glow_strength=0.15,
            strike=self._build_strike_params(progress=0.35, impact=False),
        )
        self.canvas.create_text(
            self.center_x,
            self.canvas_height - 18,
            text="КРАКЕН ЗАДОВОЛЕНИЙ",
            font=("Bahnschrift", 12),
            fill=self.palette["text_primary"],
        )

    # ------------------------------------------------------------------ #
    # Game logic hooks
    # ------------------------------------------------------------------ #
    def apply_attack_damage(self):
        if not self.attack_target:
            return
        target_board, x, y, attack_size = self.attack_target
        for dx in range(attack_size):
            for dy in range(attack_size):
                attack_x = x + dx
                attack_y = y + dy
                if 0 <= attack_x < self.board_size and 0 <= attack_y < self.board_size:
                    if not target_board.revealed[attack_y][attack_x]:
                        target_board.attack(attack_x, attack_y)
        if self.on_attack_callback:
            board_name = "Гравець" if target_board == self.player_board else "Комп'ютер"
            self.on_attack_callback(board_name, x, y, attack_size)
        self.attack_target = None

    def destroy(self):
        self.active = False
        if self._idle_job is not None:
            try:
                self.parent_frame.after_cancel(self._idle_job)
            except tk.TclError:
                pass
            self._idle_job = None
        if self._spawn_job is not None:
            try:
                self.parent_frame.after_cancel(self._spawn_job)
            except tk.TclError:
                pass
            self._spawn_job = None
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.destroy()

    # ------------------------------------------------------------------ #
    # Drawing helpers
    # ------------------------------------------------------------------ #
    def _draw_scene(
        self,
        *,
        phase: float,
        tentacle_wave: float,
        body_offset: float,
        eye_state: str,
        glow_strength: float,
        reveal_progress: float = 1.0,
        strike: dict | None = None,
    ):
        self.canvas.delete("all")
        self._draw_background(glow_strength)
        reveal_progress = max(0.0, min(1.0, reveal_progress))
        reveal_offset = (1 - reveal_progress) * 140
        self._draw_tentacles(phase, tentacle_wave, reveal_offset, strike)
        self._draw_body(body_offset + (1 - reveal_progress) * 20, eye_state, reveal_offset)

    def _draw_background(self, glow_strength: float):
        p = self.palette
        self.canvas.create_rectangle(
            0,
            0,
            self.canvas_width,
            self.canvas_height,
            fill=p["background"],
            outline="",
        )
        if glow_strength > 0:
            radius = 90 + glow_strength * 16
            self.canvas.create_oval(
                self.center_x - radius,
                self.center_y - 76,
                self.center_x + radius,
                self.center_y + 66,
                fill=p["glow"],
                outline="",
            )

    def _draw_tentacles(
        self,
        phase: float,
        tentacle_wave: float,
        reveal_offset: float,
        strike: dict | None,
    ):
        p = self.palette
        margin_x = 22
        margin_y = 18
        attack_direction = strike["direction"] if strike else None
        attack_progress = strike["progress"] if strike else 0.0
        target_coords = (
            (strike["target_x"], strike["target_y"]) if strike else None
        )
        impact = strike["impact"] if strike else False

        for direction in (-1, 1):
            for idx, tentacle in enumerate(self.tentacles):
                base_points = tentacle["points"]
                amplitude = tentacle_wave * tentacle["amplitude"]
                offset = self.tentacle_phase_offsets[idx]
                points = []
                for point_idx, (px, py) in enumerate(base_points):
                    if len(base_points) > 1:
                        progress = point_idx / (len(base_points) - 1)
                    else:
                        progress = 0
                    phase_value = phase * 0.08 + progress * 2.3 + offset
                    sway = math.sin(phase_value) * amplitude * (1 - progress * 0.25)
                    lift = math.cos(phase_value) * amplitude * 0.35
                    base_x = px if direction == -1 else -px
                    x = self.center_x + base_x + direction * sway
                    y = self.center_y + py + lift + reveal_offset
                    points.append((x, y))

                attack_anchor = None
                attack_eased = 0.0
                attack_ripple = False
                if (
                    strike
                    and direction == attack_direction
                    and idx == 0
                    and target_coords is not None
                ):
                    anchor_x, anchor_y = points[0]
                    eased = attack_progress ** 1.1
                    new_points = []
                    for i, (orig_x, orig_y) in enumerate(points):
                        t = i / (len(points) - 1) if len(points) > 1 else 1.0
                        stretch_x = anchor_x + (target_coords[0] - anchor_x) * eased * t
                        stretch_y = anchor_y + (target_coords[1] - anchor_y) * eased * t
                        relaxed_x = anchor_x + (orig_x - anchor_x) * (1 - eased)
                        relaxed_y = anchor_y + (orig_y - anchor_y) * (1 - eased)
                        final_x = relaxed_x + (stretch_x - anchor_x)
                        final_y = relaxed_y + (stretch_y - anchor_y)
                        final_x = max(margin_x, min(self.canvas_width - margin_x, final_x))
                        final_y = max(margin_y, min(self.canvas_height - margin_y, final_y))
                        if impact and attack_progress >= 1.0:
                            final_y -= math.sin((t + self.animation_phase / 10) * math.pi) * 4 * (1 - t)
                            final_y = max(margin_y, min(self.canvas_height - margin_y, final_y))
                        new_points.append((final_x, final_y))
                    points = new_points
                    attack_anchor = (anchor_x, anchor_y)
                    attack_eased = eased
                    attack_ripple = impact and attack_progress >= 1.0

                outline_width = tentacle["width"] + 4
                self.canvas.create_line(
                    *self._flatten(points),
                    smooth=True,
                    width=outline_width,
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                    fill=p["tentacle_outline"],
                )
                self.canvas.create_line(
                    *self._flatten(points),
                    smooth=True,
                    width=tentacle["width"],
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                    fill=p["tentacle"],
                )

                for cup_idx, (cup_x, cup_y) in enumerate(tentacle["cups"]):
                    base_x = cup_x if direction == -1 else -cup_x
                    phase_value = phase * 0.08 + cup_y * 0.03 + offset
                    sway = math.sin(phase_value) * amplitude * 0.3
                    lift = math.cos(phase_value) * amplitude * 0.28
                    cx = self.center_x + base_x + direction * sway
                    cy = self.center_y + cup_y + lift + reveal_offset
                    if (
                        attack_anchor
                        and direction == attack_direction
                        and idx == 0
                        and target_coords is not None
                    ):
                        t = (cup_idx + 1) / (len(tentacle["cups"]) + 1)
                        cx = attack_anchor[0] + (cx - attack_anchor[0]) * (1 - attack_eased) + (target_coords[0] - attack_anchor[0]) * attack_eased * t
                        cy = attack_anchor[1] + (cy - attack_anchor[1]) * (1 - attack_eased) + (target_coords[1] - attack_anchor[1]) * attack_eased * t
                        if attack_ripple:
                            cy -= math.sin((t + self.animation_phase / 10) * math.pi) * 3 * (1 - t)
                            cy = max(margin_y, min(self.canvas_height - margin_y, cy))
                        cx = max(margin_x, min(self.canvas_width - margin_x, cx))
                        cy = max(margin_y, min(self.canvas_height - margin_y, cy))
                    radius = 4 if tentacle["width"] <= 12 else 5
                    self.canvas.create_oval(
                        cx - radius,
                        cy - radius,
                        cx + radius,
                        cy + radius,
                        fill=p["sucker"],
                        outline=p["tentacle_outline"],
                        width=1,
                    )
                    self.canvas.create_oval(
                        cx - radius * 0.45,
                        cy - radius * 0.45,
                        cx + radius * 0.45,
                        cy + radius * 0.45,
                        fill=p["sucker_highlight"],
                        outline="",
            )

    def _draw_body(self, body_offset: float, eye_state: str, reveal_offset: float):
        p = self.palette
        top = self.center_y - 82 + body_offset + reveal_offset
        bottom = self.center_y + 44 + body_offset + reveal_offset
        left = self.center_x - 64
        right = self.center_x + 64

        self.canvas.create_oval(
            left,
            top,
            right,
            bottom,
            fill=p["body"],
            outline=p["outline"],
            width=4,
        )
        self.canvas.create_oval(
            left + 14,
            top + 18,
            right - 14,
            bottom - 20,
            fill=p["body_shadow"],
            outline="",
        )
        self.canvas.create_oval(
            left + 26,
            top + 26,
            right - 26,
            bottom - 44,
            fill=p["body"],
            outline="",
        )

        horn_left = [
            (self.center_x - 26, top + 6),
            (self.center_x - 60, top - 24),
            (self.center_x - 32, top + 24),
        ]
        horn_right = [
            (self.center_x + 26, top + 6),
            (self.center_x + 60, top - 24),
            (self.center_x + 32, top + 24),
        ]
        for horn_points in (horn_left, horn_right):
            self.canvas.create_polygon(
                *self._flatten(horn_points),
                fill=p["horn"],
                outline=p["horn_outline"],
                width=3,
                smooth=True,
            )

        spots = [
            (-36, 36, 9),
            (-22, 60, 7),
            (22, 60, 7),
            (36, 36, 9),
            (0, 44, 6),
        ]
        for dx, dy, radius in spots:
            cx = self.center_x + dx
            cy = top + dy
            self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill=p["body_shadow"],
                outline="",
            )

        self.canvas.create_arc(
            left + 20,
            bottom - 46,
            right - 20,
            bottom - 24,
            start=210,
            extent=120,
            style=tk.ARC,
            outline=p["highlight"],
            width=6,
        )

        ridge_y = bottom - 38
        for offset in (-34, -14, 14, 34):
            self.canvas.create_oval(
                self.center_x + offset - 10,
                ridge_y - 12,
                self.center_x + offset + 10,
                ridge_y + 12,
                outline=p["outline"],
                width=2,
            )

        mouth_top = bottom - 48
        mouth_bottom = mouth_top + 28
        self.canvas.create_oval(
            self.center_x - 40,
            mouth_top,
            self.center_x + 40,
            mouth_bottom,
            fill=p["body_shadow"],
            outline=p["outline"],
            width=2,
        )
        inner_mouth = self.canvas.create_oval(
            self.center_x - 28,
            mouth_top + 10,
            self.center_x + 28,
            mouth_bottom + 2,
            fill="#2d0c18",
            outline="",
        )
        self.canvas.tag_lower(inner_mouth)

        fang_width = 12
        fang_height = 12
        for direction in (-1, 1):
            base_x = self.center_x + direction * 20
            self.canvas.create_polygon(
                base_x - fang_width // 2,
                mouth_top + 6,
                base_x,
                mouth_top - fang_height + 6,
                base_x + fang_width // 2,
                mouth_top + 6,
                fill=p["teeth"],
                outline=p["teeth_outline"],
                width=1,
            )

        bottom_teeth = [
            (-26, mouth_bottom - 10),
            (-8, mouth_bottom - 6),
            (8, mouth_bottom - 6),
            (26, mouth_bottom - 10),
        ]
        for tx, ty in bottom_teeth:
            self.canvas.create_polygon(
                self.center_x + tx - 5,
                ty,
                self.center_x + tx,
                ty + 12,
                self.center_x + tx + 5,
                ty,
                fill=p["teeth"],
                outline=p["teeth_outline"],
                width=1,
            )

        self._draw_eyes(top, eye_state)

    def _draw_eyes(self, top: float, eye_state: str):
        p = self.palette
        eye_y = top + 46
        eye_width = 44
        eye_height = 28
        pupil_width = 12 if eye_state == "rage" else 14

        for direction in (-1, 1):
            center_x = self.center_x + direction * 32
            x1 = center_x - eye_width // 2
            x2 = center_x + eye_width // 2
            y1 = eye_y - eye_height // 2
            y2 = eye_y + eye_height // 2
            fill_color = p["eye_rage"] if eye_state == "rage" else p["eye"]

            if eye_state != "closed":
                self.canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill_color,
                    outline=p["eye_outline"],
                    width=3,
                )
                pupil_offset = 9
                self.canvas.create_oval(
                    center_x - pupil_width // 2,
                    eye_y - pupil_offset,
                    center_x + pupil_width // 2,
                    eye_y + pupil_offset,
                    fill=p["pupil"],
                    outline="",
                )
                highlight_shift = -2 if direction == -1 else 2
                self.canvas.create_oval(
                    center_x + highlight_shift - 3,
                    eye_y - 3,
                    center_x + highlight_shift + 1,
                    eye_y + 1,
                    fill=p["pupil_glow"],
                    outline="",
                )
                if eye_state == "rage":
                    self.canvas.create_line(
                        center_x - 10,
                        eye_y + eye_height // 2 - 4,
                        center_x + 10,
                        eye_y + eye_height // 2 - 6,
                        fill=p["eye_outline"],
                        width=3,
                    )
                lid_intensity = 1.25 if eye_state == "rage" else 1.0
                cover_extra = eye_state == "half"
                self._draw_angry_upper_lid(
                    center_x=center_x,
                    eye_y=eye_y,
                    eye_width=eye_width,
                    eye_height=eye_height,
                    direction=direction,
                    intensity=lid_intensity,
                    cover_extra=cover_extra,
                )
            else:
                self.canvas.create_line(
                    x1,
                    eye_y,
                    x2,
                    eye_y,
                    fill=p["eye_closed"],
                    width=6,
                    capstyle=tk.ROUND,
                )

        if eye_state == "half":
            for direction in (-1, 1):
                center_x = self.center_x + direction * 32
                inner_x = center_x - direction * (eye_width // 2) + direction * 4
                outer_x = center_x + direction * (eye_width // 2) - direction * 6
                self.canvas.create_line(
                    inner_x,
                    eye_y + 2,
                    outer_x,
                    eye_y + 4,
                    fill=p["eye_outline"],
                    width=3,
                    capstyle=tk.ROUND,
                )

    def _draw_angry_upper_lid(
        self,
        *,
        center_x: float,
        eye_y: float,
        eye_width: float,
        eye_height: float,
        direction: int,
        intensity: float,
        cover_extra: bool,
    ):
        p = self.palette
        outer_x = center_x + direction * (eye_width / 2)
        inner_x = center_x - direction * (eye_width / 2)
        high_y = eye_y - eye_height / 2 - (6 * intensity)
        low_y = eye_y - eye_height / 2 + (5 * intensity)
        drop = 12 + (6 if cover_extra else 0)

        points = [
            (outer_x + direction * 5, high_y),
            (inner_x - direction * 4, low_y),
            (inner_x - direction * 6, low_y + drop),
            (outer_x + direction * 3, high_y + drop - 2),
        ]

        self.canvas.create_polygon(
            *self._flatten(points),
            fill=p["body"],
            outline="",
        )
        self.canvas.create_line(
            outer_x + direction * 5,
            high_y + 1,
            inner_x - direction * 4,
            low_y + 2,
            fill=p["outline"],
            width=3,
            capstyle=tk.ROUND,
        )
    @staticmethod
    def _flatten(points):
        flat = []
        for x, y in points:
            flat.extend([x, y])
        return flat

    def _build_strike_params(self, progress: float, impact: bool):
        progress = max(0.0, min(1.0, progress))
        target_canvas = None
        highlight = 0
        cell_size = self.cell_size or 40

        margin_x = 22
        margin_y = 18
        if not self.attack_target:
            direction = 1
            target_x = self.center_x + self.canvas_width / 2 + 60
            target_y = self.center_y
        else:
            target_board, x, y, attack_size = self.attack_target
            direction = -1 if target_board == self.player_board else 1
            target_canvas = (
                self.player_canvas_widget if direction == -1 else self.computer_canvas_widget
            )
            size_span = max(1, attack_size)
            center_col = x + (size_span - 1) / 2
            center_row = y + (size_span - 1) / 2

            if target_canvas is not None:
                target_canvas.update_idletasks()
                self.canvas.update_idletasks()
                try:
                    highlight = int(target_canvas.cget("highlightthickness"))
                except tk.TclError:
                    highlight = 0
                board_x = target_canvas.winfo_rootx()
                board_y = target_canvas.winfo_rooty()
                kraken_x = self.canvas.winfo_rootx()
                kraken_y = self.canvas.winfo_rooty()

                if self.cell_size:
                    cell_size = self.cell_size
                else:
                    cell_size = max(1, target_canvas.winfo_width() / self.board_size)

                target_x = (
                    board_x
                    - kraken_x
                    + highlight
                    + cell_size * (center_col + 0.5)
                )
                target_y = (
                    board_y
                    - kraken_y
                    + highlight
                    + cell_size * (center_row + 0.5)
                )
                target_x = max(margin_x, min(self.canvas_width - margin_x, target_x))
                target_y = max(margin_y, min(self.canvas_height - margin_y, target_y))
                return {
                    "direction": direction,
                    "progress": progress,
                    "impact": impact,
                    "target_x": target_x,
                    "target_y": target_y,
                }

        # fallback estimation if canvases unavailable
        if self.attack_target:
            size_span = max(1, attack_size)
            center_col = x + (size_span - 1) / 2
            center_row = y + (size_span - 1) / 2
            normalized_row = (center_row + 0.5) / self.board_size
            normalized_col = (center_col + 0.5) / self.board_size
            vertical_span = self.canvas_height * 0.7
            target_y = self.center_y + (normalized_row - 0.5) * vertical_span
            target_y = max(
                self.center_y - vertical_span / 2,
                min(self.center_y + vertical_span / 2, target_y),
            )
            side_reach = self.canvas_width / 2 + 70
            column_adjust = (normalized_col - 0.5) * 60
            target_x = self.center_x + direction * (side_reach + column_adjust)
        target_x = max(margin_x, min(self.canvas_width - margin_x, target_x))
        target_y = max(margin_y, min(self.canvas_height - margin_y, target_y))

        return {
            "direction": direction,
            "progress": progress,
            "impact": impact,
            "target_x": target_x,
            "target_y": target_y,
        }
