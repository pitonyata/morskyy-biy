# rockets.py
import random
import tkinter as tk
from typing import Optional, Tuple, Set, Callable


class RocketsManager:
    """
    Менеджер ракет для BattleshipGame.
    - Підтримує ручне розміщення 'ракеть' гравцем під час фази setup (опційно).
    - Дозволяє кидати ракету під час гри (1x1 на 6x6 або 3x3 на більших полях).
    - Підтримує ракети противника (приховані).
    - Малює тимчасовий ефект вибуху на canvas.
    """

    def __init__(
        self,
        game,  # очікуємо BattleshipGame об'єкт
        player_canvas: tk.Canvas,
        computer_canvas: tk.Canvas,
        board_size: int,
        root: tk.Tk,
        rockets_limit_map: dict | None = None,
    ):
        self.game = game
        self.root = root
        self.player_canvas = player_canvas
        self.computer_canvas = computer_canvas
        self.board_size = board_size

        # кількість ракет залежно від розміру поля (за замовчуванням)
        default = {6: 2, 10: 3, 14: 4}
        self.rockets_limit = rockets_limit_map if rockets_limit_map else default
        self.rockets_limit_count = self.rockets_limit.get(board_size, 3)

        # зберігаємо координати "розміщених" ракет гравця як множину (можна не використовувати)
        self.player_rockets: Set[Tuple[int, int]] = set()
        # ракети комп'ютера (якщо хочеш — можна розміщати приховано)
        self.computer_rockets: Set[Tuple[int, int]] = set()

        # режими: None, "placing" (розміщення гравцем), "throw" (кидання під час ходу)
        self.mode: Optional[str] = None

        # колбеки / зручні прапори
        self.on_rocket_thrown_callback: Optional[Callable[[str, int, int, int], None]] = None
        # останній результат (для UI)
        self._last_throw_result = None

        # тимчасові графічні об'єкти анімацій (щоб потім видалити)
        self._temp_items = []

        # UI об'єкти
        self.rocket_button = None
        self.rockets_label = None

        # прив'язка до гри
        setattr(self.game, "rockets_manager", self)

        # лічильник використаних ракет гравцем
        if not hasattr(self.game, "player_rockets_used"):
            self.game.player_rockets_used = []


    def start_placing(self):
        if self.game.game_phase != "setup":
            return
        self.mode = "placing"
        self.game.info_label.config(
            text=f"Розміщення ракет (необов'язково): клацніть на полі для розміщення (макс {self.rockets_limit_count})."
        )

    def stop_placing(self):
        self.mode = None
        self.game.update_info_label()

    def toggle_place_at(self, x: int, y: int) -> bool:
        """Додає/видаляє маркер ракети у позиції (x,y) для гравця (визуально)."""
        if self.game.game_phase != "setup":
            return False

        if (x, y) in self.player_rockets:
            self.player_rockets.remove((x, y))
            self.game.draw_boards()
            self._update_rockets_label()
            return True

        if len(self.player_rockets) >= self.rockets_limit_count:
            return False

        # Не ставимо ракети поверх кораблів
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            if self.game.player_board.grid[y][x] == self.game.player_board.grid[y][x].__class__.EMPTY:
                self.player_rockets.add((x, y))
                self.game.draw_boards()
                self._update_rockets_label()
                return True
        return False

    # ------------------------
    # Розміщення ракет комп'ютера (приховано)
    # ------------------------
    def place_computer_rockets_random(self):
        """Розставляє приховані ракети комп'ютера."""
        attempts = 0
        while len(self.computer_rockets) < self.rockets_limit_count and attempts < 5000:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            # тільки на пусті клітинки (не поверх кораблів)
            if self.game.computer_board.grid[y][x] == self.game.computer_board.grid[y][x].__class__.EMPTY:
                if (x, y) not in self.computer_rockets:
                    self.computer_rockets.add((x, y))
            attempts += 1

    # ------------------------
    # Кидок ракети під час ходу
    # ------------------------
    def enable_throw_mode(self):
        """Активує режим 'кинути ракету' — наступний клік по полю противника кинув ракету."""
        if self.game.game_phase != "playing":
            return
        if self.rockets_remaining_for_player() <= 0:
            return
        self.mode = "throw"
        self.game.info_label.config(text="Режим: кинути ракету. Клікніть по полю противника для цілі.")

    def cancel_throw_mode(self):
        self.mode = None
        self.game.update_info_label()

    def rockets_remaining_for_player(self) -> int:
        used = len(getattr(self.game, "player_rockets_used", []))
        return max(0, self.rockets_limit_count - used)

    def _use_player_rocket(self):
        self.game.player_rockets_used.append(True)

    def _get_rocket_radius(self) -> int:
        """Повертає 'radius' у клітинках: radius=0 => 1x1; radius=1 => 3x3"""
        return 0 if self.board_size == 6 else 1

    def throw_rocket_at(self, target_board_name: str, x: int, y: int):
        """
        Виконує логіку вибуху: якщо radius=0 => 1x1, інакше 3x3.
        Повертає (hit_any, coords_hit) як і старий модуль.
        """
        if target_board_name == "computer":
            board = self.game.computer_board
        else:
            board = self.game.player_board

        radius = self._get_rocket_radius()
        hit_any = False
        coords_hit = []

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tx = x + dx
                ty = y + dy
                if 0 <= tx < self.board_size and 0 <= ty < self.board_size:
                    if not board.revealed[ty][tx]:
                        hit, sunk, ship = board.attack(tx, ty)
                        board.revealed[ty][tx] = True
                        coords_hit.append((tx, ty, hit))
                        if hit:
                            hit_any = True

        # анімація вибуху на canvas (область залежить від radius)
        target_canvas = self.computer_canvas if target_board_name == "computer" else self.player_canvas
        self._animate_explosion(target_canvas, x, y, radius)

        # якщо кидала гравець — відмічаємо використання
        if target_board_name == "computer":
            self._use_player_rocket()

        # якщо кидала AI і була ракета з computer_rockets, видаляємо її
        if target_board_name == "player":
            # якщо там була ракета комп'ютера — видалимо
            if (x, y) in self.computer_rockets:
                self.computer_rockets.remove((x, y))

        # колбек для оновлення UI/логіки
        if self.on_rocket_thrown_callback:
            self.on_rocket_thrown_callback(target_board_name, x, y, radius)

        return hit_any, coords_hit

    # ------------------------
    # Графіка
    # ------------------------
    def _canvas_cell_bbox(self, canvas: tk.Canvas, col: int, row: int) -> Tuple[int, int, int, int]:
        cs = self.game.cell_size
        x1 = col * cs
        y1 = row * cs
        x2 = x1 + cs
        y2 = y1 + cs
        return x1, y1, x2, y2

    def draw_rockets_on_player_canvas(self):
        """Малюємо іконки ракет на полі гравця (при показі кораблів)."""
        canvas = self.player_canvas
        canvas.delete("rocket_icon")
        for (x, y) in self.player_rockets:
            x1, y1, x2, y2 = self._canvas_cell_bbox(canvas, x, y)
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            r = min(self.game.cell_size, 24) / 2
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#88c0d0", outline="#3b82a5", tags=("rocket_icon",))
            canvas.create_text(cx, cy, text="🚀", font=("Arial", int(r)), tags=("rocket_icon",))

    def _animate_explosion(self, canvas: tk.Canvas, center_col: int, center_row: int, radius: int):
        """Ефект вибуху: напівпрозорий прямокутник над областю та емодзі '💥'."""
        cs = self.game.cell_size

        # Малюємо область ураження для кожної клітинки в зоні вибуху
        rects = []
        texts = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tx = center_col + dx
                ty = center_row + dy
                if 0 <= tx < self.board_size and 0 <= ty < self.board_size:
                    x1, y1, x2, y2 = self._canvas_cell_bbox(canvas, tx, ty)

                    # Малюємо червоний прямокутник для кожної клітинки
                    rect = canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="#ff6b6b",
                        stipple="gray50",
                        outline="#ff0000",
                        width=2,
                        tags=("rocket_anim",)
                    )
                    rects.append(rect)

                    # Малюємо емодзі вибуху в центрі клітинки
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    t = canvas.create_text(
                        cx, cy,
                        text="💥",
                        font=("Arial", int(cs * 0.6)),
                        tags=("rocket_anim",)
                    )
                    texts.append(t)

        self.root.update_idletasks()

        def clear():
            try:
                canvas.delete("rocket_anim")
            except tk.TclError:
                pass

        self.root.after(800, clear)

    # ------------------------
    # UI: кнопка та лічильник
    # ------------------------
    def create_rocket_controls(self, parent_frame: tk.Frame):
        container = tk.Frame(parent_frame, bg="#1a1a2e")
        container.pack(side=tk.LEFT, padx=6)

        self.rocket_button = tk.Button(
            container,
            text=f"🚀 Кинути ракету",
            font=("Arial", 12, "bold"),
            bg="#ff9f43",
            fg="#1a1a2e",
            activebackground="#ff8c1a",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.enable_throw_mode
        )
        self.rocket_button.pack(side=tk.LEFT, padx=(0, 6))

        self.rockets_label = tk.Label(
            container,
            text=f"×{self.rockets_limit_count}",
            font=("Arial", 12, "bold"),
            fg="#ffd166",
            bg="#1a1a2e"
        )
        self.rockets_label.pack(side=tk.LEFT)

        self._update_rockets_label()

    def _update_rockets_label(self):
        used = len(getattr(self.game, "player_rockets_used", []))
        remaining = max(0, self.rockets_limit_count - used)
        if self.rockets_label:
            self.rockets_label.config(text=f"×{remaining}")
        if self.rocket_button:
            if remaining <= 0:
                self.rocket_button.config(state=tk.DISABLED)
            else:
                self.rocket_button.config(state=tk.NORMAL)

    # ------------------------
    # AI: комп'ютер використовує ракети
    # ------------------------
    def ai_maybe_throw(self):
        """
        Викликається під час ходу комп'ютера — з певним шансом комп кидає ракету.
        Повертає True якщо була кинута ракета і вона влучила хоча б в одну клітинку (hit_any).
        """
        # комп'ютер кидає ракету тільки якщо у нього є хоча б одна (комп'ютер_ракетки)
        if not self.computer_rockets and len(self.computer_rockets) == 0:
            # якщо комп'ютер не мав попередньо розставлених ракет, даємо йому шанс кинути випадкову,
            # але обмежимо загальну кількість ходів: імплементуємо шанс лише коли рандом пройшов.
            # Тут логіка: якщо є ліміт, комп може створити тимчасову ракету та кинути її.
            # шанс кидка
            chance = 0.15  # 15% шанс кинути випадкову ракету
            if random.random() > chance:
                return False
            # обираємо випадкову ціль
            tx = random.randint(0, self.board_size - 1)
            ty = random.randint(0, self.board_size - 1)
            hit_any, _ = self.throw_rocket_at("player", tx, ty)
            return hit_any

        # якщо комп'ютер розставив свої ракети при старті — використовує одну з них із імовірністю
        if self.computer_rockets:
            # шанс використання ракети зараз (наприклад 25%)
            if random.random() > 0.25:
                return False
            tx, ty = random.choice(tuple(self.computer_rockets))
            # виконуємо вибух на позиції ракети
            hit_any, _ = self.throw_rocket_at("player", tx, ty)
            # після використання видаляємо її
            if (tx, ty) in self.computer_rockets:
                self.computer_rockets.remove((tx, ty))
            return hit_any

        return False
