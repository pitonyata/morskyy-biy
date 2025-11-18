import tkinter as tk
import random
from typing import List, Tuple, Optional
from kraken import Kraken
from rockets import RocketsManager
from ai_controllers import EasyAIController, HardAIController
from Board import Board, CellState, Orientation, Ship
from ai_robot import AIRobot
from player_avatar import PlayerAvatar
from dialogue_manager import DialogueManager
from visual_effects import VisualEffects

class MainMenu:
    """Головне меню гри з анімацією"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Морський бій")
        self.root.resizable(True, True)  # Дозволяємо зміну розміру
        self.root.configure(bg='#1a1a2e')
        
        # Мінімальний розмір вікна
        self.root.minsize(600, 700)
        
        # Центруємо вікно - адаптивні відступи
        window_width = 650
        window_height = 760  # трохи менше, щоб важливі кнопки були видимі на невеликих екранах
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Якщо екран маленький, зменшуємо вікно
        if screen_height < 900:
            window_height = int(screen_height * 0.92)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.selected_board_size = 10  # За замовчуванням нормальний розмір
        
        self.setup_menu()
        self.animate_title()
    
    def setup_menu(self):
        # Контейнер + Canvas зі scrollbar для прокручування меню
        container = tk.Frame(self.root, bg='#1a1a2e')
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg='#1a1a2e', highlightthickness=0)
        v_scroll = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Внутрішній frame куди додаються всі віджети меню
        main_frame = tk.Frame(canvas, bg='#1a1a2e')
        window_id = canvas.create_window((0, 0), window=main_frame, anchor='nw')

        # Оновлюємо область прокрутки при зміні розмірів контенту
        def on_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        main_frame.bind("<Configure>", on_frame_config)

        # Підлаштовуємо ширину внутрішнього вікна при зміні розміру канви
        def on_canvas_resize(event):
            canvas.itemconfig(window_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_resize)

        # Декоративні хвилі зверху
        wave_frame = tk.Frame(main_frame, bg='#1a1a2e', height=30)
        wave_frame.pack(fill=tk.X, pady=(0, 20))

        wave_label = tk.Label(
            wave_frame,
            text="〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            font=('Arial', 16),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        wave_label.pack()

        # Заголовок з емодзі
        self.title_label = tk.Label(
            main_frame,
            text="⚓ МОРСЬКИЙ БІЙ ⚓",
            font=('Arial', 42, 'bold'),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        self.title_label.pack(pady=(20, 10))

        # Підзаголовок
        subtitle = tk.Label(
            main_frame,
            text="🚢 Битва на морі 🚢",
            font=('Arial', 18),
            fg='#00ff88',
            bg='#1a1a2e'
        )
        subtitle.pack(pady=(0, 20))

        # Блок вибору розміру поля
        size_frame = tk.Frame(main_frame, bg='#0f3460', relief=tk.RAISED, bd=2)
        size_frame.pack(pady=12, padx=20, fill=tk.X)

        size_title = tk.Label(
            size_frame,
            text="📏 ОБЕРІТЬ РОЗМІР ПОЛЯ",
            font=('Arial', 14, 'bold'),
            fg='#00d4ff',
            bg='#0f3460'
        )
        size_title.pack(pady=(12, 8))

        # Кнопки вибору розміру
        size_buttons_frame = tk.Frame(size_frame, bg='#0f3460')
        size_buttons_frame.pack(pady=(5, 12))

        # Маленьке поле 6x6
        self.small_btn = tk.Button(
            size_buttons_frame,
            text="🔸 МАЛЕНЬКЕ\n6×6\n5 кораблів",
            font=('Arial', 11, 'bold'),
            bg='#4a5568',
            fg='#ffffff',
            activebackground='#5a6578',
            relief=tk.RAISED,
            bd=3,
            padx=15,
            pady=12,
            cursor='hand2',
            command=lambda: self.select_board_size(6)
        )
        self.small_btn.pack(side=tk.LEFT, padx=8)
        
        # Нормальне поле 10x10
        self.normal_btn = tk.Button(
            size_buttons_frame,
            text="🔷 НОРМАЛЬНЕ\n10×10\n10 кораблів",
            font=('Arial', 11, 'bold'),
            bg='#00ff88',
            fg='#1a2a2e',
            activebackground='#00cc6f',
            relief=tk.SUNKEN,
            bd=3,
            padx=15,
            pady=12,
            cursor='hand2',
            command=lambda: self.select_board_size(10)
        )
        self.normal_btn.pack(side=tk.LEFT, padx=8)
        
        # Велике поле 14x14
        self.large_btn = tk.Button(
            size_buttons_frame,
            text="🔶 ВЕЛИКЕ\n14×14\n15 кораблів",
            font=('Arial', 11, 'bold'),
            bg='#4a5568',
            fg='#ffffff',
            activebackground='#5a6578',
            relief=tk.RAISED,
            bd=3,
            padx=15,
            pady=12,
            cursor='hand2',
            command=lambda: self.select_board_size(14)
        )
        self.large_btn.pack(side=tk.LEFT, padx=8)

        # --- Новий блок вибору складності ---
        difficulty_frame = tk.Frame(main_frame, bg='#0f3460', relief=tk.RAISED, bd=2)
        difficulty_frame.pack(pady=20, padx=20, fill=tk.X)

        diff_title = tk.Label(
            difficulty_frame,
            text="🤖 ОБЕРІТЬ СКЛАДНІСТЬ AI",
            font=('Arial', 14, 'bold'),
            fg='#00d4ff',
            bg='#0f3460'
        )
        diff_title.pack(pady=(15, 10))

        diff_buttons_frame = tk.Frame(difficulty_frame, bg='#0f3460')
        diff_buttons_frame.pack(pady=(5, 15))

        self.difficulty = "easy"

        def select_difficulty(level):
            self.difficulty = level
            easy_btn.config(bg='#00ff88' if level == "easy" else '#4a5568',
                            fg='#1a1a2e' if level == "easy" else '#ffffff',
                            relief=tk.SUNKEN if level == "easy" else tk.RAISED)
            hard_btn.config(bg='#00ff88' if level == "hard" else '#4a5568',
                            fg='#1a2a2e' if level == "hard" else '#ffffff',
                            relief=tk.SUNKEN if level == "hard" else tk.RAISED)

        easy_btn = tk.Button(
            diff_buttons_frame,
            text="😴 EASY",
            font=('Arial', 12, 'bold'),
            bg='#00ff88',
            fg='#1a2a2e',
            relief=tk.SUNKEN,
            padx=20,
            pady=10,
            cursor='hand2',
            command=lambda: select_difficulty("easy")
        )
        easy_btn.pack(side=tk.LEFT, padx=8)

        hard_btn = tk.Button(
            diff_buttons_frame,
            text="💀 HARD",
            font=('Arial', 12, 'bold'),
            bg='#4a5568',
            fg='#ffffff',
            relief=tk.RAISED,
            padx=20,
            pady=10,
            cursor='hand2',
            command=lambda: select_difficulty("hard")
        )
        hard_btn.pack(side=tk.LEFT, padx=8)

        
        # Контейнер для кнопок
        buttons_frame = tk.Frame(main_frame, bg='#1a1a2e')
        buttons_frame.pack(pady=10)
        
        # Кнопка "Нова гра"
        self.play_button = tk.Button(
            buttons_frame,
            text="🎮  ПОЧАТИ ГРУ",
            font=('Arial', 18, 'bold'),
            bg='#00ff88',
            fg='#1a2a2e',
            activebackground='#00cc6f',
            relief=tk.FLAT,
            padx=50,
            pady=20,
            cursor='hand2',
            command=self.start_game
        )
        self.play_button.pack(pady=15)
        
        # Кнопка "Про гру"
        self.about_button = tk.Button(
            buttons_frame,
            text="ℹ️  ПРО ГРУ",
            font=('Arial', 16, 'bold'),
            bg='#00d4ff',
            fg='#1a2a2e',
            activebackground='#00a8cc',
            relief=tk.FLAT,
            padx=50,
            pady=18,
            cursor='hand2',
            command=self.show_about
        )
        self.about_button.pack(pady=15)
        
        # Кнопка "Вихід з гри"
        self.exit_button = tk.Button(
            buttons_frame,
            text="🚪  ВИХІД З ГРИ",
            font=('Arial', 18, 'bold'),
            bg='#ff4444',
            fg='#ffffff',
            activebackground='#cc3333',
            relief=tk.FLAT,
            padx=50,
            pady=20,
            cursor='hand2',
            command=self.exit_game
        )
        self.exit_button.pack(pady=15)
        
        # Декоративні хвилі знизу
        bottom_wave_frame = tk.Frame(main_frame, bg='#1a1a2e')
        bottom_wave_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        bottom_wave = tk.Label(
            bottom_wave_frame,
            text="〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
            font=('Arial', 16),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        bottom_wave.pack()
        
        # Інформація про версію
        version_label = tk.Label(
            bottom_wave_frame,
            text="версія 2.1",
            font=('Arial', 10),
            fg='#666666',
            bg='#1a1a2e'
        )
        version_label.pack(pady=(10, 0))
        
        # Додаємо ефекти наведення
        self.add_button_effects()
    
    def select_board_size(self, size: int):
        """Вибір розміру ігрового поля"""
        self.selected_board_size = size
        
        # Оновлюємо вигляд кнопок
        self.small_btn.config(
            bg='#00ff88' if size == 6 else '#4a5568',
            fg='#1a2a2e' if size == 6 else '#ffffff',
            relief=tk.SUNKEN if size == 6 else tk.RAISED
        )
        self.normal_btn.config(
            bg='#00ff88' if size == 10 else '#4a5568',
            fg='#1a2a2e' if size == 10 else '#ffffff',
            relief=tk.SUNKEN if size == 10 else tk.RAISED
        )
        self.large_btn.config(
            bg='#00ff88' if size == 14 else '#4a5568',
            fg='#1a2a2e' if size == 14 else '#ffffff',
            relief=tk.SUNKEN if size == 14 else tk.RAISED
        )
    
    def add_button_effects(self):
        """Додає ефекти наведення для кнопок"""
        def on_enter_play(e):
            self.play_button.config(bg='#00cc6f', font=('Arial', 19, 'bold'))
        
        def on_leave_play(e):
            self.play_button.config(bg='#00ff88', font=('Arial', 18, 'bold'))
        
        def on_enter_about(e):
            self.about_button.config(bg='#00a8cc', font=('Arial', 17, 'bold'))
        
        def on_leave_about(e):
            self.about_button.config(bg='#00d4ff', font=('Arial', 16, 'bold'))
        
        def on_enter_exit(e):
            self.exit_button.config(bg='#cc3333', font=('Arial', 19, 'bold'))
        
        def on_leave_exit(e):
            self.exit_button.config(bg='#ff4444', font=('Arial', 18, 'bold'))
        
        self.play_button.bind('<Enter>', on_enter_play)
        self.play_button.bind('<Leave>', on_leave_play)
        self.about_button.bind('<Enter>', on_enter_about)
        self.about_button.bind('<Leave>', on_leave_about)
        self.exit_button.bind('<Enter>', on_enter_exit)
        self.exit_button.bind('<Leave>', on_leave_exit)
    
    def exit_game(self):
        """Виходить з програми з підтвердженням в стилі гри"""
        # Створюємо кастомне вікно підтвердження
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("Вихід з гри")
        confirm_window.configure(bg='#1a1a2e')
        confirm_window.resizable(False, False)
        confirm_window.grab_set()
        
        # Центруємо вікно
        window_width = 420
        window_height = 360
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        confirm_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        main_frame = tk.Frame(confirm_window, bg='#1a1a2e', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Іконка
        icon_label = tk.Label(
            main_frame,
            text="⚓",
            font=('Arial', 40),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        icon_label.pack(pady=(0, 10))
        
        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="ВИХІД З ГРИ",
            font=('Arial', 18, 'bold'),
            fg='#ff4444',
            bg='#1a1a2e'
        )
        title_label.pack(pady=(0, 8))
        
        # Текст питання
        question_label = tk.Label(
            main_frame,
            text="Ви впевнені, що хочете\nпокинути гру?",
            font=('Arial', 13),
            fg='#ffffff',
            bg='#1a1a2e',
            justify=tk.CENTER
        )
        question_label.pack(pady=(0, 20))
        
        # Контейнер для кнопок з фіксованою шириною
        buttons_container = tk.Frame(main_frame, bg='#1a1a2e')
        buttons_container.pack()
        
        # Кнопка "Так" - фіксована ширина
        yes_btn = tk.Button(
            buttons_container,
            text="✓  ТАК",
            font=('Arial', 16, 'bold'),
            bg='#ff4444',
            fg='#ffffff',
            activebackground='#cc3333',
            relief=tk.FLAT,
            width=12,
            pady=12,
            cursor='hand2',
            command=self.root.quit
        )
        yes_btn.pack(pady=6)
        
        # Кнопка "Ні" - фіксована ширина
        no_btn = tk.Button(
            buttons_container,
            text="✗  НІ",
            font=('Arial', 16, 'bold'),
            bg='#00ff88',
            fg='#1a2a2e',
            activebackground='#00cc6f',
            relief=tk.FLAT,
            width=12,
            pady=12,
            cursor='hand2',
            command=confirm_window.destroy
        )
        no_btn.pack(pady=6)
        
        # Ефекти наведення
        def on_enter_yes(e):
            yes_btn.config(bg='#cc3333', font=('Arial', 17, 'bold'))
        
        def on_leave_yes(e):
            yes_btn.config(bg='#ff4444', font=('Arial', 16, 'bold'))
        
        def on_enter_no(e):
            no_btn.config(bg='#00cc6f', font=('Arial', 17, 'bold'))
        
        def on_leave_no(e):
            no_btn.config(bg='#00ff88', font=('Arial', 16, 'bold'))
        
        yes_btn.bind('<Enter>', on_enter_yes)
        yes_btn.bind('<Leave>', on_leave_yes)
        no_btn.bind('<Enter>', on_enter_no)
        no_btn.bind('<Leave>', on_leave_no)
    
    def animate_title(self):
        """Анімація пульсації заголовка"""
        colors = ['#00d4ff', '#00a8cc', '#0088aa', '#00a8cc', '#00d4ff']
        self.color_index = 0
        self.animation_running = True
        
        def pulse():
            if self.animation_running and self.title_label.winfo_exists():
                try:
                    self.title_label.config(fg=colors[self.color_index % len(colors)])
                    self.color_index += 1
                    self.root.after(500, pulse)
                except:
                    pass
        
        pulse()
    
    def stop_animation(self):
        """Зупиняє анімацію перед закриттям меню"""
        self.animation_running = False
    
    def show_about(self):
        """Показує інформацію про гру"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Про гру")
        about_window.configure(bg='#1a1a2e')
        about_window.resizable(True, True)  # Дозволяємо зміну розміру
        about_window.grab_set()
        
        # Мінімальний розмір
        about_window.minsize(500, 600)
        
        # Центруємо вікно
        window_width = 550
        window_height = 650
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        about_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        main_frame = tk.Frame(about_window, bg='#1a1a2e', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title = tk.Label(
            main_frame,
            text="🎮 ПРО ГРУ",
            font=('Arial', 24, 'bold'),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        title.pack(pady=(0, 20))
        
        # Інформаційний блок
        info_frame = tk.Frame(main_frame, bg='#0f3460', relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        info_text = """
🚢 МОРСЬКИЙ БІЙ - класична гра для одного гравця

📋 ПРАВИЛА ГРИ:
• Розмістіть свої кораблі на полі
• По черзі стріляйте по полю противника
• Мета: потопити всі кораблі противника

🐙 УВАГА: КРАКЕН!
• На середніх (10×10) та великих (14×14) полях
  з'являється КРАКЕН - морський монстр!
• Кракен атакує ОБИДВА поля випадково
• На полі 10×10: атакує 1 клітинку
• На полі 14×14: атакує область 3×3!
• Остерігайтеся його гніву! ⚡

🔢 РОЗМІРИ ПОЛІВ:

🔸 МАЛЕНЬКЕ (6×6):
  • 1 Крейсер (3), 1 Есмінець (2), 3 Катери (1)
  • Кракен НЕ з'являється ✅

🔷 НОРМАЛЬНЕ (10×10):
  • 1 Лінкор (4), 2 Крейсери (3)
  • 3 Есмінці (2), 4 Катери (1)
  • Кракен атакує 1×1 ⚠️

🔶 ВЕЛИКЕ (14×14):
  • 1 Авіаносець (5), 2 Лінкори (4)
  • 3 Крейсери (3), 4 Есмінці (2), 5 Катерів (1)
  • Кракен атакує 3×3 ☠️

💡 ПОРАДИ:
• Використовуйте розумну стратегію
• Кораблі не торкаються один одного
• Після потоплення клітинки навколо
  автоматично відкриваються
• Бережіться кракена на великих полях!

🎲 Бажаємо удачі, адміралe!
        """
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=('Arial', 10),
            fg='#ffffff',
            bg='#0f3460',
            justify=tk.LEFT,
            padx=20,
            pady=15
        )
        info_label.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка закриття
        close_btn = tk.Button(
            main_frame,
            text="✓ Зрозуміло",
            font=('Arial', 14, 'bold'),
            bg='#00ff88',
            fg='#1a2a2e',
            activebackground='#00cc6f',
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor='hand2',
            command=about_window.destroy
        )
        close_btn.pack(pady=(20, 0))
    
    def start_game(self):
        """Закриває меню та запускає гру"""
        # Зупиняємо анімацію
        self.stop_animation()
        
        # Очищаємо вікно
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Запускаємо гру з вибраним розміром та складністю
        game = BattleshipGame(self.root, self.selected_board_size, self.difficulty)


class BattleshipGame:
    """Головний клас гри Морський бій з GUI"""
    
    def __init__(self, root, board_size: int = 10, difficulty: str = "easy"):
        self.root = root
        self.root.title("Морський бій")
        self.root.resizable(True, True)
        self.root.configure(bg='#1a1a2e')
        
        self.board_size = board_size
        self.difficulty = difficulty  # зберігаємо складність
        
        # Розмір клітинки залежить від розміру поля
        if board_size == 6:
            self.cell_size = 60
            self.root.minsize(900, 700)
        elif board_size == 10:
            self.cell_size = 40
            self.root.minsize(1000, 800)
        else:  # 14
            self.cell_size = 35
            self.root.minsize(1100, 850)
        
        # Конфігурація кораблів залежно від розміру поля
        self.ship_sizes = self.get_ship_configuration(board_size)
        
        # Ігрові поля з правильною конфігурацією кораблів
        self.player_board = Board(self.board_size, self.ship_sizes)
        self.computer_board = Board(self.board_size, self.ship_sizes)
        
        # Стан гри: setup (розміщення), playing (гра), ended (завершено)
        self.game_phase = "setup"
        self.current_ship_index = 0
        self.current_orientation = Orientation.HORIZONTAL
        
        # Статистика гри
        self.player_score = 0      # Влучання гравця
        self.computer_score = 0    # Влучання комп'ютера
        self.player_shots = 0      # Всього пострілів гравця
        self.computer_shots = 0    # Всього пострілів комп'ютера

        # лічильник використаних мін гравцем
        self.player_mines_used = []

        # Змінні для розумного ШІ
        self.ai_mode = "hunt"           # Режим: hunt (пошук) або target (добивання)
        self.ai_target_queue = []       # Черга клітинок для атаки після влучання
        self.ai_last_hit = None         # Остання успішна атака
        self.ai_hit_direction = None    # Напрямок послідовних влучань
        
        # Ініціалізуємо кракена (None на початку, створимо після старту гри)
        self.kraken = None
        self.kraken_container = None

        # Ініціалізуємо AI-контролер згідно складності
        if self.difficulty == "easy":
            self.ai_controller = EasyAIController(self.player_board)
        else:
            self.ai_controller = HardAIController(self.player_board)

        # Ініціалізуємо робота, аватар гравця та менеджер діалогів
        self.ai_robot = None
        self.ai_robot_container = None
        self.player_avatar = None
        self.player_avatar_container = None
        self.dialogue_manager = DialogueManager(difficulty=self.difficulty)

        # Ініціалізуємо візуальні ефекти
        self.visual_effects = VisualEffects(self.root)

        self.setup_ui()
        self.center_window()
    
    def get_ship_configuration(self, board_size: int) -> List[int]:
        """Повертає конфігурацію кораблів залежно від розміру поля"""
        if board_size == 6:
            # Маленьке поле: 5 кораблів
            # 1 крейсер (3), 1 есмінець (2), 3 катери (1)
            return [3, 2, 1, 1, 1]
        elif board_size == 10:
            # Нормальне поле: 10 кораблів (класична конфігурація)
            # 1 лінкор (4), 2 крейсери (3), 3 есмінці (2), 4 катери (1)
            return [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        else:  # 14
            # Велике поле: 15 кораблів
            # 1 авіаносець (5), 2 лінкори (4), 3 крейсери (3), 4 есмінці (2), 5 катерів (1)
            return [5, 4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1]
    
    def center_window(self):
        """Центрує вікно гри на екрані з адаптивним розміром"""
        self.root.update_idletasks()
        
        # Розрахунок розміру вікна на основі розміру поля
        board_width = self.cell_size * self.board_size
        window_width = board_width * 2 + 200  # Два поля + відступи
        window_height = board_width + 320     # Висота поля + елементи інтерфейсу
        
        # Отримуємо розмір екрану
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Адаптація під розмір екрану
        if window_width > screen_width * 0.95:
            window_width = int(screen_width * 0.95)
        if window_height > screen_height * 0.9:
            window_height = int(screen_height * 0.9)
        
        # Розраховуємо позицію для центрування
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Встановлюємо розмір та позицію вікна
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
    def setup_ui(self):
        """Створює весь графічний інтерфейс гри"""
        # Заголовок гри
        title_frame = tk.Frame(self.root, bg='#1a1a2e')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🚢 МОРСЬКИЙ БІЙ 🚢",
            font=('Arial', 28, 'bold'),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        title_label.pack()
        
        # Інформаційна панель (підказки для гравця)
        self.info_label = tk.Label(
            self.root,
            text="Розміщуйте кораблі на своєму полі",
            font=('Arial', 14),
            fg='#ffffff',
            bg='#1a1a2e'
        )
        self.info_label.pack(pady=10)
        
        # Контейнер для аватара гравця у верхньому лівому куті
        top_left_container = tk.Frame(self.root, bg='#1a1a2e')
        top_left_container.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=10)

        self.player_avatar_container = tk.Frame(
            top_left_container,
            bg='#1a1a2e',
            width=180,
            height=200
        )
        self.player_avatar_container.pack()
        self.player_avatar_container.pack_propagate(False)

        # Контейнер для робота у верхньому правому куті (зменшений аватар)
        top_right_container = tk.Frame(self.root, bg='#1a1a2e')
        top_right_container.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

        self.ai_robot_container = tk.Frame(
            top_right_container,
            bg='#1a1a2e',
            width=180,  # Зменшений розмір
            height=200   # Зменшений розмір
        )
        self.ai_robot_container.pack()
        self.ai_robot_container.pack_propagate(False)

        # Контейнер для обох ігрових полів ТА КРАКЕНА
        boards_frame = tk.Frame(self.root, bg='#1a1a2e')
        boards_frame.pack(pady=10)

        # Зберігаємо посилання на boards_frame для кракена
        self.boards_frame = boards_frame

        # Поле гравця (ліворуч)
        player_container = tk.Frame(boards_frame, bg='#1a1a2e')
        player_container.pack(side=tk.LEFT, padx=20)
        
        # Контейнер для кракена між полями
        if self.board_size >= 10:
            kraken_height = self.cell_size * self.board_size + 1
            self.kraken_container = tk.Frame(
                boards_frame,
                bg='#1a1a2e',
                width=360,
                height=kraken_height
            )
            self.kraken_container.pack(side=tk.LEFT, padx=10)
            self.kraken_container.pack_propagate(False)
        else:
            self.kraken_container = None
        
        player_title = tk.Label(
            player_container,
            text="Ваше поле",
            font=('Arial', 16, 'bold'),
            fg='#00ff88',
            bg='#1a1a2e'
        )
        player_title.pack(pady=5)
        
        self.player_canvas = tk.Canvas(
            player_container,
            width=self.cell_size * self.board_size + 1,
            height=self.cell_size * self.board_size + 1,
            bg='#0f3460',
            highlightthickness=2,
            highlightbackground='#00d4ff'
        )
        self.player_canvas.pack()
        # Обробники подій для розміщення кораблів
        self.player_canvas.bind('<Button-1>', self.on_player_board_click)
        self.player_canvas.bind('<Motion>', self.on_player_board_hover)
        
        # Поле комп'ютера (праворуч)
        computer_container = tk.Frame(boards_frame, bg='#1a1a2e')
        computer_container.pack(side=tk.LEFT, padx=20)

        computer_title = tk.Label(
            computer_container,
            text="Поле противника",
            font=('Arial', 16, 'bold'),
            fg='#ff4444',
            bg='#1a1a2e'
        )
        computer_title.pack(pady=5)

        self.computer_canvas = tk.Canvas(
            computer_container,
            width=self.cell_size * self.board_size + 1,
            height=self.cell_size * self.board_size + 1,
            bg='#0f3460',
            highlightthickness=2,
            highlightbackground='#ff4444'
        )
        self.computer_canvas.pack()
        # Обробник кліків для атаки
        self.computer_canvas.bind('<Button-1>', self.on_computer_board_click)
        # Обробник наведення для показу області ураження ракети
        self.computer_canvas.bind('<Motion>', self.on_computer_board_hover)
        
        # Панель керування з кнопками
        control_frame = tk.Frame(self.root, bg='#1a1a2e')
        control_frame.pack(pady=20)
        
        self.rotate_button = tk.Button(
            control_frame,
            text="🔄 Повернути корабель",
            font=('Arial', 12, 'bold'),
            bg='#00d4ff',
            fg='#1a2a2e',
            activebackground='#00a8cc',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.rotate_ship
        )
        self.rotate_button.pack(side=tk.LEFT, padx=5)
        
        self.random_button = tk.Button(
            control_frame,
            text="🎲 Випадково",
            font=('Arial', 12, 'bold'),
            bg='#00ff88',
            fg='#1a2a2e',
            activebackground='#00cc6f',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.place_ships_randomly
        )
        self.random_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            control_frame,
            text="🔄 Нова гра",
            font=('Arial', 12, 'bold'),
            bg='#ff8800',
            fg='#1a2a2e',
            activebackground='#cc6600',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.reset_game
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.menu_button = tk.Button(
            control_frame,
            text="🏠 Головне меню",
            font=('Arial', 12, 'bold'),
            bg='#9b59b6',
            fg='#ffffff',
            activebackground='#8e44ad',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.return_to_menu
        )
        self.menu_button.pack(side=tk.LEFT, padx=5)

        self.rockets_manager = RocketsManager(
            game=self,
            player_canvas=self.player_canvas,
            computer_canvas=self.computer_canvas,
            board_size=self.board_size,
            root=self.root
        )
        self.rockets_manager.create_rocket_controls(control_frame)
        
        # Панель рахунку
        score_frame = tk.Frame(self.root, bg='#1a1a2e')
        score_frame.pack(pady=10)
        
        self.score_label = tk.Label(
            score_frame,
            text="Попадань гравця: 0 | Попадань комп'ютера: 0",
            font=('Arial', 12),
            fg='#ffffff',
            bg='#1a1a2e'
        )
        self.score_label.pack()
        
        self.draw_boards()
        
    def draw_ship(self, canvas: tk.Canvas, ship, cell_size: int):
        """Малює детальні унікальні військові кораблі"""
        coords = ship.get_coordinates()
        if not coords:
            return

        # Визначаємо орієнтацію
        is_horizontal = len(coords) == 1 or coords[0][1] == coords[1][1]

        # Сортуємо координати
        if is_horizontal:
            coords = sorted(coords, key=lambda c: c[0])
        else:
            coords = sorted(coords, key=lambda c: c[1])

        ship_size = len(coords)

        # Малюємо різні типи кораблів
        if ship_size == 1:
            self._draw_patrol_boat(canvas, coords, cell_size, is_horizontal)
        elif ship_size == 2:
            self._draw_torpedo_boat(canvas, coords, cell_size, is_horizontal)
        elif ship_size == 3:
            self._draw_destroyer(canvas, coords, cell_size, is_horizontal)
        elif ship_size == 4:
            self._draw_battleship(canvas, coords, cell_size, is_horizontal)

    def _draw_patrol_boat(self, canvas, coords, cell_size, is_horizontal):
        """Швидкісний катер - компактний та сучасний"""
        x, y = coords[0]
        cx, cy = x * cell_size + cell_size // 2, y * cell_size + cell_size // 2

        if is_horizontal:
            # Корпус (прямокутний але обтічний)
            canvas.create_rectangle(
                cx - 12, cy - 7,
                cx + 12, cy + 7,
                fill='#e74c3c', outline='#c0392b', width=2
            )
            # Гострий ніс
            canvas.create_polygon(
                cx + 12, cy - 7,
                cx + 18, cy,
                cx + 12, cy + 7,
                fill='#c0392b', outline=''
            )
            # Біла смуга
            canvas.create_rectangle(
                cx - 10, cy - 4,
                cx + 10, cy + 4,
                fill='#ecf0f1', outline=''
            )
            # Кабіна пілота (скло)
            canvas.create_rectangle(
                cx - 5, cy - 10,
                cx + 5, cy - 7,
                fill='#3498db', outline='#2980b9', width=1
            )
            # Мотор ззаду
            canvas.create_rectangle(
                cx - 14, cy - 5,
                cx - 12, cy + 5,
                fill='#34495e', outline='#2c3e50', width=1
            )
        else:
            # Вертикальний
            canvas.create_rectangle(
                cx - 7, cy - 12,
                cx + 7, cy + 12,
                fill='#e74c3c', outline='#c0392b', width=2
            )
            canvas.create_polygon(
                cx - 7, cy - 12,
                cx, cy - 18,
                cx + 7, cy - 12,
                fill='#c0392b', outline=''
            )
            canvas.create_rectangle(
                cx - 4, cy - 10,
                cx + 4, cy + 10,
                fill='#ecf0f1', outline=''
            )
            canvas.create_rectangle(
                cx - 10, cy - 5,
                cx - 7, cy + 5,
                fill='#3498db', outline='#2980b9', width=1
            )
            canvas.create_rectangle(
                cx - 5, cy + 12,
                cx + 5, cy + 14,
                fill='#34495e', outline='#2c3e50', width=1
            )

    def _draw_torpedo_boat(self, canvas, coords, cell_size, is_horizontal):
        """Торпедний катер - середній швидкий корабель"""
        if is_horizontal:
            x_start = coords[0][0] * cell_size
            x_end = (coords[-1][0] + 1) * cell_size
            y_center = coords[0][1] * cell_size + cell_size // 2

            # Корпус
            canvas.create_rectangle(
                x_start + 3, y_center - 8,
                x_end - 3, y_center + 8,
                fill='#2980b9', outline='#1c5985', width=2
            )
            # Ніс
            canvas.create_polygon(
                x_start + 3, y_center - 8,
                x_start - 5, y_center,
                x_start + 3, y_center + 8,
                fill='#1c5985', outline=''
            )
            # Палуба
            canvas.create_rectangle(
                x_start + 5, y_center - 5,
                x_end - 5, y_center + 5,
                fill='#5dade2', outline=''
            )
            # Рубка
            mid_x = (x_start + x_end) // 2
            canvas.create_rectangle(
                mid_x - 10, y_center - 14,
                mid_x + 10, y_center - 8,
                fill='#21618c', outline='#1c5985', width=1
            )
            # Вікна
            for i in range(3):
                wx = mid_x - 6 + i * 5
                canvas.create_rectangle(
                    wx, y_center - 12,
                    wx + 3, y_center - 10,
                    fill='#85c1e9', outline=''
                )
            # Торпеди
            canvas.create_oval(
                x_end - 15, y_center - 12,
                x_end - 8, y_center - 8,
                fill='#e74c3c', outline='#c0392b', width=1
            )
        else:
            y_start = coords[0][1] * cell_size
            y_end = (coords[-1][1] + 1) * cell_size
            x_center = coords[0][0] * cell_size + cell_size // 2

            canvas.create_rectangle(
                x_center - 8, y_start + 3,
                x_center + 8, y_end - 3,
                fill='#2980b9', outline='#1c5985', width=2
            )
            canvas.create_polygon(
                x_center - 8, y_start + 3,
                x_center, y_start - 5,
                x_center + 8, y_start + 3,
                fill='#1c5985', outline=''
            )
            canvas.create_rectangle(
                x_center - 5, y_start + 5,
                x_center + 5, y_end - 5,
                fill='#5dade2', outline=''
            )
            mid_y = (y_start + y_end) // 2
            canvas.create_rectangle(
                x_center - 14, mid_y - 10,
                x_center - 8, mid_y + 10,
                fill='#21618c', outline='#1c5985', width=1
            )
            for i in range(3):
                wy = mid_y - 6 + i * 5
                canvas.create_rectangle(
                    x_center - 12, wy,
                    x_center - 10, wy + 3,
                    fill='#85c1e9', outline=''
                )
            canvas.create_oval(
                x_center - 12, y_end - 15,
                x_center - 8, y_end - 8,
                fill='#e74c3c', outline='#c0392b', width=1
            )

    def _draw_destroyer(self, canvas, coords, cell_size, is_horizontal):
        """Есмінець - військовий корабель з озброєнням"""
        if is_horizontal:
            x_start = coords[0][0] * cell_size
            x_end = (coords[-1][0] + 1) * cell_size
            y_center = coords[0][1] * cell_size + cell_size // 2

            # Корпус
            canvas.create_rectangle(
                x_start + 3, y_center - 9,
                x_end - 3, y_center + 9,
                fill='#7f8c8d', outline='#34495e', width=2
            )
            # Ніс
            canvas.create_polygon(
                x_start + 3, y_center - 9,
                x_start - 6, y_center,
                x_start + 3, y_center + 9,
                fill='#34495e', outline=''
            )
            # Палуба
            canvas.create_rectangle(
                x_start + 5, y_center - 6,
                x_end - 5, y_center + 6,
                fill='#95a5a6', outline=''
            )

            # Рубка (велика)
            mid_x = (x_start + x_end) // 2 - 5
            canvas.create_rectangle(
                mid_x - 12, y_center - 16,
                mid_x + 12, y_center - 9,
                fill='#2c3e50', outline='#34495e', width=1
            )
            # Вікна
            for i in range(4):
                canvas.create_rectangle(
                    mid_x - 8 + i * 5, y_center - 14,
                    mid_x - 6 + i * 5, y_center - 11,
                    fill='#3498db', outline=''
                )

            # Труба
            canvas.create_rectangle(
                mid_x + 16, y_center - 15,
                mid_x + 22, y_center - 9,
                fill='#2c3e50', outline='#34495e', width=1
            )
            canvas.create_rectangle(
                mid_x + 16, y_center - 17,
                mid_x + 22, y_center - 15,
                fill='#e74c3c', outline=''
            )

            # Гарматна башта
            canvas.create_oval(
                x_start + 8, y_center - 12,
                x_start + 16, y_center - 6,
                fill='#34495e', outline='#1c2833', width=1
            )
            # Дуло
            canvas.create_rectangle(
                x_start + 16, y_center - 10,
                x_start + 24, y_center - 8,
                fill='#1c2833', outline=''
            )

            # Антена
            canvas.create_line(
                x_end - 8, y_center - 9,
                x_end - 8, y_center - 20,
                fill='#95a5a6', width=2
            )
            canvas.create_oval(
                x_end - 11, y_center - 22,
                x_end - 5, y_center - 18,
                fill='#e67e22', outline=''
            )
        else:
            y_start = coords[0][1] * cell_size
            y_end = (coords[-1][1] + 1) * cell_size
            x_center = coords[0][0] * cell_size + cell_size // 2

            canvas.create_rectangle(
                x_center - 9, y_start + 3,
                x_center + 9, y_end - 3,
                fill='#7f8c8d', outline='#34495e', width=2
            )
            canvas.create_polygon(
                x_center - 9, y_start + 3,
                x_center, y_start - 6,
                x_center + 9, y_start + 3,
                fill='#34495e', outline=''
            )
            canvas.create_rectangle(
                x_center - 6, y_start + 5,
                x_center + 6, y_end - 5,
                fill='#95a5a6', outline=''
            )

            mid_y = (y_start + y_end) // 2 - 5
            canvas.create_rectangle(
                x_center - 16, mid_y - 12,
                x_center - 9, mid_y + 12,
                fill='#2c3e50', outline='#34495e', width=1
            )
            for i in range(4):
                canvas.create_rectangle(
                    x_center - 14, mid_y - 8 + i * 5,
                    x_center - 11, mid_y - 6 + i * 5,
                    fill='#3498db', outline=''
                )

            canvas.create_rectangle(
                x_center - 15, mid_y + 16,
                x_center - 9, mid_y + 22,
                fill='#2c3e50', outline='#34495e', width=1
            )
            canvas.create_rectangle(
                x_center - 17, mid_y + 16,
                x_center - 15, mid_y + 22,
                fill='#e74c3c', outline=''
            )

            canvas.create_oval(
                x_center - 12, y_start + 8,
                x_center - 6, y_start + 16,
                fill='#34495e', outline='#1c2833', width=1
            )
            canvas.create_rectangle(
                x_center - 10, y_start + 16,
                x_center - 8, y_start + 24,
                fill='#1c2833', outline=''
            )

            canvas.create_line(
                x_center - 9, y_end - 8,
                x_center - 20, y_end - 8,
                fill='#95a5a6', width=2
            )
            canvas.create_oval(
                x_center - 22, y_end - 11,
                x_center - 18, y_end - 5,
                fill='#e67e22', outline=''
            )

    def _draw_battleship(self, canvas, coords, cell_size, is_horizontal):
        """Лінкор - великий військовий корабель"""
        if is_horizontal:
            x_start = coords[0][0] * cell_size
            x_end = (coords[-1][0] + 1) * cell_size
            y_center = coords[0][1] * cell_size + cell_size // 2

            # Корпус (товстий)
            canvas.create_rectangle(
                x_start + 2, y_center - 11,
                x_end - 2, y_center + 11,
                fill='#5d6d7e', outline='#17202a', width=3
            )
            # Ніс (масивний)
            canvas.create_polygon(
                x_start + 2, y_center - 11,
                x_start - 7, y_center,
                x_start + 2, y_center + 11,
                fill='#17202a', outline=''
            )
            # Палуба
            canvas.create_rectangle(
                x_start + 4, y_center - 7,
                x_end - 4, y_center + 7,
                fill='#85929e', outline=''
            )

            # Перша рубка
            mid_x = (x_start + x_end) // 2 - 10
            canvas.create_rectangle(
                mid_x - 14, y_center - 18,
                mid_x + 10, y_center - 11,
                fill='#212f3c', outline='#17202a', width=2
            )
            # Багато вікон
            for i in range(5):
                canvas.create_rectangle(
                    mid_x - 12 + i * 4, y_center - 16,
                    mid_x - 10 + i * 4, y_center - 13,
                    fill='#2e86de', outline=''
                )

            # Друга рубка (вища)
            canvas.create_rectangle(
                mid_x - 6, y_center - 24,
                mid_x + 6, y_center - 18,
                fill='#1c2833', outline='#17202a', width=1
            )
            canvas.create_rectangle(
                mid_x - 4, y_center - 22,
                mid_x - 1, y_center - 20,
                fill='#54a0ff', outline=''
            )
            canvas.create_rectangle(
                mid_x + 1, y_center - 22,
                mid_x + 4, y_center - 20,
                fill='#54a0ff', outline=''
            )

            # Дві труби
            canvas.create_rectangle(
                mid_x + 14, y_center - 17,
                mid_x + 20, y_center - 11,
                fill='#212f3c', outline='#17202a', width=2
            )
            canvas.create_rectangle(
                mid_x + 14, y_center - 19,
                mid_x + 20, y_center - 17,
                fill='#c0392b', outline=''
            )

            canvas.create_rectangle(
                mid_x + 24, y_center - 16,
                mid_x + 29, y_center - 11,
                fill='#212f3c', outline='#17202a', width=2
            )
            canvas.create_rectangle(
                mid_x + 24, y_center - 18,
                mid_x + 29, y_center - 16,
                fill='#c0392b', outline=''
            )

            # Передня гарматна башта
            canvas.create_oval(
                x_start + 6, y_center - 14,
                x_start + 18, y_center - 6,
                fill='#17202a', outline='#0b0e11', width=2
            )
            # Два дула
            canvas.create_rectangle(
                x_start + 18, y_center - 13,
                x_start + 28, y_center - 11,
                fill='#0b0e11', outline=''
            )
            canvas.create_rectangle(
                x_start + 18, y_center - 9,
                x_start + 28, y_center - 7,
                fill='#0b0e11', outline=''
            )

            # Задня гарматна башта
            canvas.create_oval(
                x_end - 18, y_center - 14,
                x_end - 6, y_center - 6,
                fill='#17202a', outline='#0b0e11', width=2
            )
            canvas.create_rectangle(
                x_end - 28, y_center - 13,
                x_end - 18, y_center - 11,
                fill='#0b0e11', outline=''
            )
            canvas.create_rectangle(
                x_end - 28, y_center - 9,
                x_end - 18, y_center - 7,
                fill='#0b0e11', outline=''
            )

            # Велика антена з радаром
            canvas.create_line(
                x_end - 10, y_center - 11,
                x_end - 10, y_center - 26,
                fill='#85929e', width=3
            )
            canvas.create_oval(
                x_end - 14, y_center - 29,
                x_end - 6, y_center - 24,
                fill='#f39c12', outline='#d68910', width=2
            )

        else:
            y_start = coords[0][1] * cell_size
            y_end = (coords[-1][1] + 1) * cell_size
            x_center = coords[0][0] * cell_size + cell_size // 2

            canvas.create_rectangle(
                x_center - 11, y_start + 2,
                x_center + 11, y_end - 2,
                fill='#5d6d7e', outline='#17202a', width=3
            )
            canvas.create_polygon(
                x_center - 11, y_start + 2,
                x_center, y_start - 7,
                x_center + 11, y_start + 2,
                fill='#17202a', outline=''
            )
            canvas.create_rectangle(
                x_center - 7, y_start + 4,
                x_center + 7, y_end - 4,
                fill='#85929e', outline=''
            )

            mid_y = (y_start + y_end) // 2 - 10
            canvas.create_rectangle(
                x_center - 18, mid_y - 14,
                x_center - 11, mid_y + 10,
                fill='#212f3c', outline='#17202a', width=2
            )
            for i in range(5):
                canvas.create_rectangle(
                    x_center - 16, mid_y - 12 + i * 4,
                    x_center - 13, mid_y - 10 + i * 4,
                    fill='#2e86de', outline=''
                )

            canvas.create_rectangle(
                x_center - 24, mid_y - 6,
                x_center - 18, mid_y + 6,
                fill='#1c2833', outline='#17202a', width=1
            )
            canvas.create_rectangle(
                x_center - 22, mid_y - 4,
                x_center - 20, mid_y - 1,
                fill='#54a0ff', outline=''
            )
            canvas.create_rectangle(
                x_center - 22, mid_y + 1,
                x_center - 20, mid_y + 4,
                fill='#54a0ff', outline=''
            )

            canvas.create_rectangle(
                x_center - 17, mid_y + 14,
                x_center - 11, mid_y + 20,
                fill='#212f3c', outline='#17202a', width=2
            )
            canvas.create_rectangle(
                x_center - 19, mid_y + 14,
                x_center - 17, mid_y + 20,
                fill='#c0392b', outline=''
            )

            canvas.create_rectangle(
                x_center - 16, mid_y + 24,
                x_center - 11, mid_y + 29,
                fill='#212f3c', outline='#17202a', width=2
            )
            canvas.create_rectangle(
                x_center - 18, mid_y + 24,
                x_center - 16, mid_y + 29,
                fill='#c0392b', outline=''
            )

            canvas.create_oval(
                x_center - 14, y_start + 6,
                x_center - 6, y_start + 18,
                fill='#17202a', outline='#0b0e11', width=2
            )
            canvas.create_rectangle(
                x_center - 13, y_start + 18,
                x_center - 11, y_start + 28,
                fill='#0b0e11', outline=''
            )
            canvas.create_rectangle(
                x_center - 9, y_start + 18,
                x_center - 7, y_start + 28,
                fill='#0b0e11', outline=''
            )

            canvas.create_oval(
                x_center - 14, y_end - 18,
                x_center - 6, y_end - 6,
                fill='#17202a', outline='#0b0e11', width=2
            )
            canvas.create_rectangle(
                x_center - 13, y_end - 28,
                x_center - 11, y_end - 18,
                fill='#0b0e11', outline=''
            )
            canvas.create_rectangle(
                x_center - 9, y_end - 28,
                x_center - 7, y_end - 18,
                fill='#0b0e11', outline=''
            )

            canvas.create_line(
                x_center - 11, y_end - 10,
                x_center - 26, y_end - 10,
                fill='#85929e', width=3
            )
            canvas.create_oval(
                x_center - 29, y_end - 14,
                x_center - 24, y_end - 6,
                fill='#f39c12', outline='#d68910', width=2
            )

    def draw_boards(self):
        self.draw_board(self.player_canvas, self.player_board, show_ships=True)
        self.draw_board(self.computer_canvas, self.computer_board, show_ships=False)
        
    def draw_board(self, canvas: tk.Canvas, board: Board, show_ships: bool):
        """Малює ігрове поле на canvas
        show_ships - чи показувати кораблі (True для свого поля, False для противника)"""
        canvas.delete('all')
        
        # Малюємо сітку поля
        for i in range(self.board_size + 1):
            # Vertical lines
            canvas.create_line(
                i * self.cell_size, 0,
                i * self.cell_size, self.board_size * self.cell_size,
                fill='#16213e', width=1
            )
            # Horizontal lines
            canvas.create_line(
                0, i * self.cell_size,
                self.board_size * self.cell_size, i * self.cell_size,
                fill='#16213e', width=1
            )
        
        # Малюємо клітинки з відповідними кольорами та символами
        for y in range(self.board_size):
            for x in range(self.board_size):
                cell_state = board.grid[y][x]
                is_revealed = board.revealed[y][x]
                
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Малюємо фон для всіх клітинок
                if cell_state == CellState.HIT:
                    canvas.create_rectangle(x1, y1, x2, y2, fill='#ff4444', outline='#16213e')
                elif cell_state == CellState.MISS:
                    canvas.create_rectangle(x1, y1, x2, y2, fill='#4a5568', outline='#16213e')
                else:
                    canvas.create_rectangle(x1, y1, x2, y2, fill='#0f3460', outline='#16213e')

        # Малюємо кораблі поверх сітки
        if show_ships:
            for ship in board.ships:
                if not ship.is_sunk():
                    self.draw_ship(canvas, ship, self.cell_size)

        # Малюємо потоплені кораблі (показуємо навіть на полі противника)
        for ship in board.ships:
            if ship.is_sunk():
                # Потоплені кораблі показуємо темними з червоним хрестом
                for x, y in ship.get_coordinates():
                    x1 = x * self.cell_size
                    y1 = y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    canvas.create_rectangle(x1, y1, x2, y2, fill='#1a1a1a', outline='#ff0000', width=2)
                    # Хрест
                    canvas.create_line(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill='#ff0000', width=3)
                    canvas.create_line(x2 - 5, y1 + 5, x1 + 5, y2 - 5, fill='#ff0000', width=3)

        # Малюємо попадання/промахи ПОВЕРХ кораблів
        for y in range(self.board_size):
            for x in range(self.board_size):
                cell_state = board.grid[y][x]
                x1 = x * self.cell_size
                y1 = y * self.cell_size

                if cell_state == CellState.HIT:
                    # Вогонь на попаданні
                    canvas.create_text(
                        x1 + self.cell_size // 2,
                        y1 + self.cell_size // 2,
                        text='💥',
                        font=('Arial', 16)
                    )
                elif cell_state == CellState.MISS:
                    # Промах
                    canvas.create_text(
                        x1 + self.cell_size // 2,
                        y1 + self.cell_size // 2,
                        text='○',
                        font=('Arial', 16),
                        fill='#ffffff'
                    )
        if canvas == self.player_canvas and show_ships and hasattr(self, "rockets_manager"):
            self.rockets_manager.draw_rockets_on_player_canvas()

    
    def on_player_board_click(self, event):
        """Обробляє клік по полі гравця для розміщення кораблів"""
        if self.game_phase != "setup":
            return

        # Конвертуємо координати миші в координати сітки
        x = event.x // self.cell_size
        y = event.y // self.cell_size

        # Розміщення кораблів
        if self.current_ship_index < len(self.ship_sizes):
                ship_size = self.ship_sizes[self.current_ship_index]

        if self.player_board.place_ship(ship_size, x, y, self.current_orientation):
            self.current_ship_index += 1

            # Якщо всі кораблі розміщені — починаємо гру
            if self.current_ship_index >= len(self.ship_sizes):
                self.start_game()
            else:
                self.update_info_label()

            self.draw_boards()
        else:
            # Показуємо повідомлення про помилку через info_label
            self.info_label.config(text="❌ Неможливо розмістити корабель тут!", fg='#ff4444')
            # Повертаємо нормальний колір через 2 секунди
            self.root.after(2000, lambda: self.info_label.config(fg='#ffffff'))
    
    def on_player_board_hover(self, event):
        """Показує попередній перегляд розміщення корабля при наведенні миші"""
        if self.game_phase != "setup" or self.current_ship_index >= len(self.ship_sizes):
            return
        
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        # Перемальовуємо поле
        self.draw_board(self.player_canvas, self.player_board, show_ships=True)
        
        # Показуємо попередній перегляд (зелений - можна, червоний - не можна)
        ship_size = self.ship_sizes[self.current_ship_index]
        can_place = self.player_board.can_place_ship(ship_size, x, y, self.current_orientation)
        color = '#88ff88' if can_place else '#ff8888'
        
        for i in range(ship_size):
            if self.current_orientation == Orientation.HORIZONTAL:
                px, py = x + i, y
            else:
                px, py = x, y + i
            
            if 0 <= px < self.board_size and 0 <= py < self.board_size:
                x1 = px * self.cell_size
                y1 = py * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.player_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline='#ffffff',
                    stipple='gray50'
                )
    
    def on_computer_board_hover(self, event):
        """Показує попередній перегляд області ураження ракети при наведенні миші"""
        if not hasattr(self, "rockets_manager"):
            return

        # Показуємо попередній перегляд тільки в режимі кидання ракети
        if self.rockets_manager.mode != "throw":
            return

        x = event.x // self.cell_size
        y = event.y // self.cell_size

        # Перемальовуємо поле
        self.draw_board(self.computer_canvas, self.computer_board, show_ships=False)

        # Отримуємо радіус ураження
        radius = self.rockets_manager._get_rocket_radius()

        # Показуємо попередній перегляд області ураження (зелений напівпрозорий)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tx = x + dx
                ty = y + dy

                if 0 <= tx < self.board_size and 0 <= ty < self.board_size:
                    x1 = tx * self.cell_size
                    y1 = ty * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size

                    # Малюємо зелений напівпрозорий квадрат для кожної клітинки
                    self.computer_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill='#88ff88',
                        outline='#00ff00',
                        width=2,
                        stipple='gray50',
                        tags=('rocket_preview',)
                    )

    def on_computer_board_click(self, event):
        """Обробляє клік по полі комп'ютера (стрільба та ракети)"""
        if self.game_phase != "playing":
            return

        x = event.x // self.cell_size
        y = event.y // self.cell_size

        # 🚀 Якщо активований режим ракети
        if hasattr(self, "rockets_manager") and self.rockets_manager.mode == "throw":
            hit_any, coords = self.rockets_manager.throw_rocket_at("computer", x, y)

            # Ефекти вибуху ракети - більше тремтіння та частинок
            self.visual_effects.shake_canvas(self.computer_canvas, intensity=8, duration=400)
            self.visual_effects.create_explosion_particles(
                self.computer_canvas,
                x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2,
                count=40,
                colors=['#ff6b6b', '#ff9f43', '#ffd166', '#ff0000', '#ffaa00', '#fff']
            )

            # Затримуємо перемальовування, щоб показати анімацію вибуху
            def after_explosion():
                self.draw_boards()
                self.update_score()

            self.root.after(850, after_explosion)
            self.rockets_manager.cancel_throw_mode()
            self.rockets_manager._update_rockets_label()

            # Аватар гравця радіє від використання ракети
            if self.player_avatar:
                if hit_any:
                    self.player_avatar.set_emotion("excited")
                    self.player_avatar.show_dialogue("Ракета влучила! 🚀", duration=2500)
                else:
                    self.player_avatar.set_emotion("sad")
                    self.player_avatar.show_dialogue("Ракета промахнулась... 💨", duration=2500)

            # Діалог про ракету гравця
            if self.ai_robot:
                dialogue = self.dialogue_manager.get_dialogue("player_rocket")
                emotion = self.dialogue_manager.get_emotion_for_event("player_rocket")
                self.ai_robot.set_emotion(emotion)
                self.ai_robot.show_dialogue(dialogue, duration=2500)

            if hit_any:
                self.info_label.config(text="🚀 Ракета влучила! Продовжуйте хід!")
            else:
                self.info_label.config(text="💨 Ракета не влучила. Хід противника...")
                self.root.after(1500, self.computer_turn)
            return

        # 🔫 Звичайний постріл
        if not (0 <= x < self.board_size and 0 <= y < self.board_size):
            return
        if self.computer_board.revealed[y][x]:
            return

        self.player_shots += 1
        hit, sunk, ship = self.computer_board.attack(x, y)

        if hit:
            self.player_score += 1
            # Ефекти попадання
            self.visual_effects.shake_canvas(self.computer_canvas, intensity=3, duration=200)
            self.visual_effects.create_hit_flash(self.computer_canvas, x, y, self.cell_size, color='#ff4444')
            self.visual_effects.create_explosion_particles(
                self.computer_canvas,
                x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2,
                count=15
            )
            if sunk:
                # Анімація потоплення корабля
                def after_sinking_animation():
                    # Після анімації перемальовуємо поле і додаємо дим
                    self.draw_boards()
                    for ship_x, ship_y in ship.get_coordinates():
                        self.visual_effects.create_smoke_effect(
                            self.computer_canvas, ship_x, ship_y, self.cell_size, duration=8000
                        )

                self.visual_effects.animate_ship_sinking(
                    self.computer_canvas,
                    ship.get_coordinates(),
                    self.cell_size,
                    callback=after_sinking_animation
                )
                self.info_label.config(text="Ви потопили корабель противника! 🎉 Продовжуйте!")
                # Аватар гравця радіє
                if self.player_avatar:
                    self.player_avatar.set_emotion("excited")
                    self.player_avatar.show_dialogue("Потопив! Ура! 🎉", duration=2500)
                # Діалог при потопленні корабля
                if self.ai_robot:
                    dialogue = self.dialogue_manager.get_dialogue("player_sunk")
                    emotion = self.dialogue_manager.get_emotion_for_event("player_sunk")
                    self.ai_robot.set_emotion(emotion)
                    self.ai_robot.show_dialogue(dialogue, duration=2500)
            else:
                self.info_label.config(text="Влучно! Стріляйте ще раз! 🎯")
                # Аватар гравця радіє
                if self.player_avatar:
                    self.player_avatar.set_emotion("happy")
                    self.player_avatar.show_dialogue("Влучання! 🎯", duration=2000)
                # Діалог при влучанні
                if self.ai_robot:
                    dialogue = self.dialogue_manager.get_dialogue("player_hit")
                    emotion = self.dialogue_manager.get_emotion_for_event("player_hit")
                    self.ai_robot.set_emotion(emotion)
                    self.ai_robot.show_dialogue(dialogue, duration=2000)
        else:
            self.info_label.config(text="Промах! Хід противника...")
            # Аватар гравця засмучений
            if self.player_avatar:
                self.player_avatar.set_emotion("sad")
                self.player_avatar.show_dialogue("Промах... 💨", duration=2000)
            # Діалог при промаху
            if self.ai_robot:
                dialogue = self.dialogue_manager.get_dialogue("player_miss")
                emotion = self.dialogue_manager.get_emotion_for_event("player_miss")
                self.ai_robot.set_emotion(emotion)
                self.ai_robot.show_dialogue(dialogue, duration=2000)
            self.root.after(500, self.computer_turn)

        self.draw_boards()
        self.update_score()

        if self.computer_board.all_ships_sunk():
            self.end_game(True)
    
    def computer_turn(self):
        """Хід комп'ютера з використанням розумного ШІ"""
        if self.game_phase != "playing":
            return

        # Показуємо що робот думає (для hard режиму)
        if self.difficulty == "hard" and self.ai_robot:
            dialogue = self.dialogue_manager.get_dialogue("thinking")
            emotion = self.dialogue_manager.get_emotion_for_event("thinking")
            self.ai_robot.set_emotion(emotion)
            self.ai_robot.show_dialogue(dialogue, duration=800)

        # Отримуємо координати для атаки від ШІ
        x, y = self.get_ai_move()

        if x is None or y is None:
            return

        self.computer_shots += 1
        hit, sunk, ship = self.player_board.attack(x, y)

        if hit:
            self.computer_score += 1
            self.ai_last_hit = (x, y)
            # Ефекти попадання комп'ютера
            self.visual_effects.shake_canvas(self.player_canvas, intensity=4, duration=250)
            self.visual_effects.create_hit_flash(self.player_canvas, x, y, self.cell_size, color='#ff0000')
            self.visual_effects.create_explosion_particles(
                self.player_canvas,
                x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2,
                count=20
            )

            if not sunk:
                # Влучання: переходимо в режим добивання, додаємо сусідні клітинки
                self.ai_mode = "target"
                self.add_adjacent_targets(x, y)
                self.info_label.config(text="Противник влучив! Він стріляє знову...")
                # Аватар гравця стурбований
                if self.player_avatar:
                    self.player_avatar.set_emotion("worried")
                    self.player_avatar.show_dialogue("Мене влучили! 😰", duration=2000)
                # Діалог при влучанні комп'ютера
                if self.ai_robot:
                    dialogue = self.dialogue_manager.get_dialogue("computer_hit")
                    emotion = self.dialogue_manager.get_emotion_for_event("computer_hit")
                    self.ai_robot.set_emotion(emotion)
                    self.ai_robot.show_dialogue(dialogue, duration=2000)
                self.root.after(1000, self.computer_turn)
            else:
                # Корабель потоплений: очищаємо цілі, повертаємося до режиму пошуку
                self.clean_target_queue_around_ship(ship)
                self.ai_mode = "hunt"
                self.ai_target_queue.clear()
                self.ai_last_hit = None
                self.ai_hit_direction = None

                # Анімація потоплення корабля гравця
                def after_player_sinking_animation():
                    # Після анімації перемальовуємо поле і додаємо дим
                    self.draw_boards()
                    for ship_x, ship_y in ship.get_coordinates():
                        self.visual_effects.create_smoke_effect(
                            self.player_canvas, ship_x, ship_y, self.cell_size, duration=8000
                        )

                self.visual_effects.animate_ship_sinking(
                    self.player_canvas,
                    ship.get_coordinates(),
                    self.cell_size,
                    callback=after_player_sinking_animation
                )
                self.info_label.config(text="Противник потопив ваш корабель! 💔")
                # Аватар гравця сумний
                if self.player_avatar:
                    self.player_avatar.set_emotion("sad")
                    self.player_avatar.show_dialogue("Мій корабель! 💔", duration=2500)
                # Діалог при потопленні корабля гравця
                if self.ai_robot:
                    dialogue = self.dialogue_manager.get_dialogue("computer_sunk")
                    emotion = self.dialogue_manager.get_emotion_for_event("computer_sunk")
                    self.ai_robot.set_emotion(emotion)
                    self.ai_robot.show_dialogue(dialogue, duration=2500)
                self.root.after(1000, self.computer_turn)
        else:
            self.ai_mode = "hunt" if not self.ai_target_queue else "target"
            self.info_label.config(text="Противник промахнувся! Ваш хід! 🎯")
            # Аватар гравця радіє
            if self.player_avatar:
                self.player_avatar.set_emotion("happy")
                self.player_avatar.show_dialogue("Промах! Чудово! 😊", duration=2000)
            # Діалог при промаху комп'ютера
            if self.ai_robot:
                dialogue = self.dialogue_manager.get_dialogue("computer_miss")
                emotion = self.dialogue_manager.get_emotion_for_event("computer_miss")
                self.ai_robot.set_emotion(emotion)
                self.ai_robot.show_dialogue(dialogue, duration=2000)

        # AI може кинути ракету
        if hasattr(self, "rockets_manager"):
            thrown = self.rockets_manager.ai_maybe_throw()
            if thrown:
                # Ефекти вибуху ракети AI
                self.visual_effects.shake_canvas(self.player_canvas, intensity=8, duration=400)

                # Діалог про ракету комп'ютера
                if self.ai_robot:
                    dialogue = self.dialogue_manager.get_dialogue("computer_rocket")
                    emotion = self.dialogue_manager.get_emotion_for_event("computer_rocket")
                    self.ai_robot.set_emotion(emotion)
                    self.ai_robot.show_dialogue(dialogue, duration=2500)

                # Затримуємо перемальовування, щоб показати анімацію вибуху
                def after_ai_explosion():
                    self.draw_boards()
                    self.update_score()
                    if self.player_board.all_ships_sunk():
                        self.end_game(False)
                    elif not self.player_board.all_ships_sunk():
                        self.root.after(600, self.computer_turn)

                self.root.after(850, after_ai_explosion)
                return  # Виходимо, щоб не перекривати анімацію

        self.draw_boards()
        self.update_score()
        
        if self.player_board.all_ships_sunk():
            self.end_game(False)
    
    def get_ai_move(self) -> Tuple[Optional[int], Optional[int]]:
        """Розумне прийняття рішень ШІ про наступну атаку
        Для EASY — повністю випадково (без добивання).
        Для HARD — використовує режим 'hunt' і 'target' (існуюча логіка)."""
        # EASY: повністю випадкова атака по будь-якій невідкритій клітині
        if getattr(self, "difficulty", "easy") == "easy":
            choices = [
                (x, y)
                for y in range(self.board_size)
                for x in range(self.board_size)
                if not self.player_board.revealed[y][x]
            ]
            if not choices:
                return None, None
            return random.choice(choices)

        # HARD: Режим добивання: атакуємо клітинки поруч з влучаннями
        if self.ai_mode == "target" and self.ai_target_queue:
            while self.ai_target_queue:
                x, y = self.ai_target_queue.pop(0)
                if 0 <= x < self.board_size and 0 <= y < self.board_size:
                    if not self.player_board.revealed[y][x]:
                        return x, y
            # Якщо черга порожня, повертаємося до режиму пошуку
            self.ai_mode = "hunt"
        
        # Режим пошуку: використовуємо шахову модель для ефективності
        max_attempts = self.board_size * 20
        attempts = 0
        
        while attempts < max_attempts:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            
            if not self.player_board.revealed[y][x]:
                if (x + y) % 2 == 0 or attempts > max_attempts // 2:
                    return x, y
            
            attempts += 1
        
        # Фолбек — перша невідкрита клітинка
        for y in range(self.board_size):
            for x in range(self.board_size):
                if not self.player_board.revealed[y][x]:
                    return x, y
        
        return None, None
    
    def add_adjacent_targets(self, x: int, y: int):
        """Додає сусідні клітинки до черги цілей після влучання
        Перевіряє 4 напрямки: вправо, вниз, вліво, вгору"""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if not self.player_board.revealed[ny][nx]:
                    if (nx, ny) not in self.ai_target_queue:
                        self.ai_target_queue.append((nx, ny))
    
    def clean_target_queue_around_ship(self, ship: Optional[Ship]):
        """Видаляє клітинки навколо потопленого корабля з черги цілей
        Це потрібно, щоб ШІ не намагався стріляти по неможливих позиціях"""
        if ship is None:
            return
        
        ship_coords = ship.get_coordinates()
        cells_to_remove = set()
        
        # Збираємо всі клітинки навколо корабля
        for sx, sy in ship_coords:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = sx + dx, sy + dy
                    cells_to_remove.add((nx, ny))
        
        # Фільтруємо чергу, видаляючи клітинки навколо потопленого корабля
        self.ai_target_queue = [(x, y) for x, y in self.ai_target_queue if (x, y) not in cells_to_remove]
    
    def rotate_ship(self):
        if self.game_phase == "setup":
            self.current_orientation = (
                Orientation.VERTICAL if self.current_orientation == Orientation.HORIZONTAL
                else Orientation.HORIZONTAL
            )
    
    def place_ships_randomly(self):
        """Автоматично розміщує всі кораблі гравця у випадкових позиціях"""
        if self.game_phase == "setup":
            self.player_board = Board(self.board_size, self.ship_sizes)
            self.player_board.place_ships_randomly()
            self.current_ship_index = len(self.ship_sizes)
            self.draw_boards()
            self.start_game()
    
    def start_game(self):
        """Починає гру після розміщення всіх кораблів"""
        self.game_phase = "playing"
        # Розміщуємо кораблі комп'ютера
        self.computer_board.place_ships_randomly()

        if hasattr(self, "rockets_manager"):
            self.rockets_manager.place_computer_rockets_random()
            self.rockets_manager._update_rockets_label()

        # Створюємо кракена (тільки для середніх та великих полів)
        if self.board_size >= 10:
            # Знищуємо старого кракена, якщо існує
            if self.kraken:
                self.kraken.destroy()

            # Створюємо нового кракена між полями
            parent = self.kraken_container if self.kraken_container else self.boards_frame
            self.kraken = Kraken(
                parent,
                self.board_size,
                self.player_board,
                self.computer_board,
                self.on_kraken_attack
            )

        # Створюємо аватар гравця
        if self.player_avatar:
            self.player_avatar.destroy()

        self.player_avatar = PlayerAvatar(self.player_avatar_container)
        self.player_avatar.set_emotion("neutral")
        self.player_avatar.show_dialogue("Готовий до бою! ⚓", duration=3000)

        # Створюємо AI-робота
        if self.ai_robot:
            self.ai_robot.destroy()

        self.ai_robot = AIRobot(
            self.ai_robot_container,
            difficulty=self.difficulty
        )

        # Показуємо початковий діалог
        dialogue = self.dialogue_manager.get_dialogue("game_start")
        emotion = self.dialogue_manager.get_emotion_for_event("game_start")
        if dialogue:
            self.ai_robot.set_emotion(emotion)
            self.ai_robot.show_dialogue(dialogue, duration=4000)

        self.info_label.config(text="Гра почалася! Стріляйте по полю противника! 🎯")
        # Вимикаємо кнопки розміщення
        self.rotate_button.config(state=tk.DISABLED)
        self.random_button.config(state=tk.DISABLED)
        self.draw_boards()
        if hasattr(self, "rockets_manager"):
            self.rockets_manager._update_rockets_label()

    
    def on_kraken_attack(self, board_name: str, x: int, y: int, attack_size: int):
        """Обробляє атаку кракена та оновлює інтерфейс"""
        # Визначаємо яке поле атаковано
        target_canvas = self.player_canvas if board_name == "Гравець" else self.computer_canvas

        # Ефекти атаки кракена - ДУЖЕ сильне тремтіння!
        self.visual_effects.shake_canvas(target_canvas, intensity=10, duration=500)
        # Додаємо частинки для всієї області атаки
        for dy in range(attack_size):
            for dx in range(attack_size):
                tx = x + dx
                ty = y + dy
                if 0 <= tx < self.board_size and 0 <= ty < self.board_size:
                    self.visual_effects.create_explosion_particles(
                        target_canvas,
                        tx * self.cell_size + self.cell_size // 2,
                        ty * self.cell_size + self.cell_size // 2,
                        count=25,
                        colors=['#ff2d2d', '#d21b24', '#ff5454', '#830f19', '#000']
                    )

        # Оновлюємо відображення полів
        self.draw_boards()

        # Показуємо повідомлення
        if attack_size == 1:
            attack_text = f"клітинку ({x}, {y})"
        else:
            attack_text = f"область {attack_size}x{attack_size} від ({x}, {y})"

        self.info_label.config(
            text=f"🐙 КРАКЕН АТАКУВАВ поле {board_name}: {attack_text}! 💥",
            fg='#ff0000'
        )

        # Аватар гравця злякний від кракена
        if self.player_avatar:
            self.player_avatar.set_emotion("worried")
            self.player_avatar.show_dialogue("Кракен! Рятуйся! 🐙", duration=3000)

        # Діалог про атаку кракена
        if self.ai_robot:
            dialogue = self.dialogue_manager.get_dialogue("kraken_attack")
            emotion = self.dialogue_manager.get_emotion_for_event("kraken_attack")
            self.ai_robot.set_emotion(emotion)
            self.ai_robot.show_dialogue(dialogue, duration=3000)

        # Перевіряємо, чи не закінчилась гра
        if self.player_board.all_ships_sunk():
            self.end_game(False)
        elif self.computer_board.all_ships_sunk():
            self.end_game(True)
        else:
            # Повертаємо нормальний колір тексту через 3 секунди
            self.root.after(3000, lambda: self.info_label.config(fg='#ffffff'))
    
    def end_game(self, player_won: bool):
        """Завершує гру та показує результати"""
        self.game_phase = "ended"

        # Показуємо всі кораблі комп'ютера
        self.draw_board(self.computer_canvas, self.computer_board, show_ships=True)

        # Розраховуємо статистику
        player_accuracy = (self.player_score / self.player_shots * 100) if self.player_shots > 0 else 0
        computer_accuracy = (self.computer_score / self.computer_shots * 100) if self.computer_shots > 0 else 0

        # Аватар гравця реагує на результат
        if self.player_avatar:
            if player_won:
                self.player_avatar.set_emotion("excited")
                self.player_avatar.show_dialogue("ПЕРЕМОГА! УРА! 🏆", duration=0)
            else:
                self.player_avatar.set_emotion("sad")
                self.player_avatar.show_dialogue("Поразка... Наступного разу переможу! 💪", duration=0)

        # Діалог про завершення гри
        if self.ai_robot:
            event = "player_wins" if player_won else "computer_wins"
            dialogue = self.dialogue_manager.get_dialogue(event)
            emotion = self.dialogue_manager.get_emotion_for_event(event)
            self.ai_robot.set_emotion(emotion)
            self.ai_robot.show_dialogue(dialogue, duration=0)  # Показуємо до закриття вікна

        # Показуємо кастомне вікно з результатами
        self.show_game_over_window(player_won, player_accuracy, computer_accuracy)
    
    def show_game_over_window(self, player_won: bool, player_accuracy: float, computer_accuracy: float):
        """Показує кастомне вікно завершення гри зі статистикою"""
        # Створюємо модальне вікно
        game_over_window = tk.Toplevel(self.root)
        game_over_window.title("Гра завершена")
        game_over_window.configure(bg='#1a1a2e')
        game_over_window.resizable(False, False)
        game_over_window.grab_set()
        
        # Центруємо вікно на екрані
        window_width = 500
        window_height = 550
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        game_over_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Головний контейнер з відступами
        main_frame = tk.Frame(game_over_window, bg='#1a1a2e', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок з результатом
        result_emoji = "🏆" if player_won else "💔"
        result_text = "ПЕРЕМОГА!" if player_won else "ПОРАЗКА"
        result_color = '#00ff88' if player_won else '#ff4444'
        
        title_label = tk.Label(
            main_frame,
            text=f"{result_emoji} {result_text} {result_emoji}",
            font=('Arial', 32, 'bold'),
            fg=result_color,
            bg='#1a1a2e'
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_text = "Вітаємо! Ви перемогли!" if player_won else "Комп'ютер переміг цього разу..."
        subtitle_label = tk.Label(
            main_frame,
            text=subtitle_text,
            font=('Arial', 14),
            fg='#ffffff',
            bg='#1a1a2e'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Контейнер для статистики
        stats_frame = tk.Frame(main_frame, bg='#0f3460', relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Stats title
        stats_title = tk.Label(
            stats_frame,
            text="📊 СТАТИСТИКА ГРИ",
            font=('Arial', 18, 'bold'),
            fg='#00d4ff',
            bg='#0f3460',
            pady=15
        )
        stats_title.pack()
        
        # Статистика гравця
        player_frame = tk.Frame(stats_frame, bg='#0f3460', pady=10)
        player_frame.pack(fill=tk.X, padx=20)
        
        player_title = tk.Label(
            player_frame,
            text="👤 ГРАВЕЦЬ",
            font=('Arial', 14, 'bold'),
            fg='#00ff88',
            bg='#0f3460',
            anchor='w'
        )
        player_title.pack(anchor='w', pady=(0, 5))
        
        player_stats = [
            f"Пострілів: {self.player_shots}",
            f"Влучань: {self.player_score}",
            f"Точність: {player_accuracy:.1f}%"
        ]
        
        for stat in player_stats:
            stat_label = tk.Label(
                player_frame,
                text=f"  • {stat}",
                font=('Arial', 12),
                fg='#ffffff',
                bg='#0f3460',
                anchor='w'
            )
            stat_label.pack(anchor='w', pady=2)
        
        # Роздільник
        divider = tk.Frame(stats_frame, bg='#16213e', height=2)
        divider.pack(fill=tk.X, padx=20, pady=10)
        
        # Статистика комп'ютера
        computer_frame = tk.Frame(stats_frame, bg='#0f3460', pady=10)
        computer_frame.pack(fill=tk.X, padx=20)
        
        computer_title = tk.Label(
            computer_frame,
            text="🤖 КОМП'ЮТЕР",
            font=('Arial', 14, 'bold'),
            fg='#ff4444',
            bg='#0f3460',
            anchor='w'
        )
        computer_title.pack(anchor='w', pady=(0, 5))
        
        computer_stats = [
            f"Пострілів: {self.computer_shots}",
            f"Влучань: {self.computer_score}",
            f"Точність: {computer_accuracy:.1f}%"
        ]
        
        for stat in computer_stats:
            stat_label = tk.Label(
                computer_frame,
                text=f"  • {stat}",
                font=('Arial', 12),
                fg='#ffffff',
                bg='#0f3460',
                anchor='w'
            )
            stat_label.pack(anchor='w', pady=2)
        
        # Повідомлення-досягнення залежно від результату
        if player_won:
            achievement_text = "⭐ Відмінна гра! Ви - справжній адмірал!" if player_accuracy >= 50 else "✨ Гарна гра! Продовжуйте тренуватись!"
            achievement_color = '#ffd700' if player_accuracy >= 50 else '#00d4ff'
        else:
            achievement_text = "💪 Не здавайтесь! Спробуйте ще раз!"
            achievement_color = '#ff8800'
        
        achievement_label = tk.Label(
            main_frame,
            text=achievement_text,
            font=('Arial', 12, 'italic'),
            fg=achievement_color,
            bg='#1a1a2e',
            pady=15
        )
        achievement_label.pack()
        
        # Панель з кнопками
        buttons_frame = tk.Frame(main_frame, bg='#1a1a2e')
        buttons_frame.pack(pady=(10, 0))
        
        # Кнопка нової гри
        new_game_btn = tk.Button(
            buttons_frame,
            text="🎮 Нова гра",
            font=('Arial', 14, 'bold'),
            bg='#00ff88',
            fg='#1a2a2e',
            activebackground='#00cc6f',
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2',
            command=lambda: [game_over_window.destroy(), self.reset_game()]
        )
        new_game_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка виходу
        exit_btn = tk.Button(
            buttons_frame,
            text="🏠 Меню",
            font=('Arial', 14, 'bold'),
            bg='#9b59b6',
            fg='#ffffff',
            activebackground='#8e44ad',
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2',
            command=lambda: [game_over_window.destroy(), self.return_to_menu()]
        )
        exit_btn.pack(side=tk.LEFT, padx=5)
        
        # Ефекти наведення для кнопок
        def on_enter_new_game(e):
            new_game_btn.config(bg='#00cc6f')
        
        def on_leave_new_game(e):
            new_game_btn.config(bg='#00ff88')
        
        def on_enter_exit(e):
            exit_btn.config(bg='#8e44ad')
        
        def on_leave_exit(e):
            exit_btn.config(bg='#9b59b6')
        
        new_game_btn.bind('<Enter>', on_enter_new_game)
        new_game_btn.bind('<Leave>', on_leave_new_game)
        exit_btn.bind('<Enter>', on_enter_exit)
        exit_btn.bind('<Leave>', on_leave_exit)
    
    def reset_game(self):
        """Скидає гру до початкового стану для нової партії"""
        # Створюємо нові поля з правильною конфігурацією
        self.player_board = Board(self.board_size, self.ship_sizes)
        self.computer_board = Board(self.board_size, self.ship_sizes)

        # Знищуємо кракена
        if hasattr(self, 'kraken') and self.kraken:
            self.kraken.destroy()
            self.kraken = None

        # Знищуємо робота
        if hasattr(self, 'ai_robot') and self.ai_robot:
            self.ai_robot.destroy()
            self.ai_robot = None

        # Знищуємо аватар гравця
        if hasattr(self, 'player_avatar') and self.player_avatar:
            self.player_avatar.destroy()
            self.player_avatar = None
        
        self.game_phase = "setup"
        self.current_ship_index = 0
        self.current_orientation = Orientation.HORIZONTAL
        
        # Скидаємо статистику
        self.player_score = 0
        self.computer_score = 0
        self.player_shots = 0
        self.computer_shots = 0
        
        # Скидаємо стан ШІ
        self.ai_mode = "hunt"
        self.ai_target_queue.clear()
        self.ai_last_hit = None
        self.ai_hit_direction = None
        
        self.rotate_button.config(state=tk.NORMAL)
        self.random_button.config(state=tk.NORMAL)
        self.update_info_label()
        self.update_score()
        self.draw_boards()
        if hasattr(self, "rockets_manager"):
            self.rockets_manager._update_rockets_label()

    
    def return_to_menu(self):
        """Повертає гравця до головного меню"""
        # Знищуємо кракена перед поверненням до меню
        if hasattr(self, 'kraken') and self.kraken:
            self.kraken.destroy()

        # Знищуємо робота перед поверненням до меню
        if hasattr(self, 'ai_robot') and self.ai_robot:
            self.ai_robot.destroy()

        # Знищуємо аватар гравця перед поверненням до меню
        if hasattr(self, 'player_avatar') and self.player_avatar:
            self.player_avatar.destroy()

        # Очищаємо вікно
        for widget in self.root.winfo_children():
            widget.destroy()

        # Повертаємося до меню
        menu = MainMenu(self.root)
    
    def update_info_label(self):
        """Оновлює інформаційну панель з підказками для гравця"""
        if self.current_ship_index < len(self.ship_sizes):
            ship_size = self.ship_sizes[self.current_ship_index]
            ship_names = {5: "Авіаносець", 4: "Лінкор", 3: "Крейсер", 2: "Есмінець", 1: "Катер"}
            ship_name = ship_names.get(ship_size, "Корабель")
            orientation_text = "горизонтально" if self.current_orientation == Orientation.HORIZONTAL else "вертикально"
            remaining = len(self.ship_sizes) - self.current_ship_index
            self.info_label.config(
                text=f"Розмістіть {ship_name} ({ship_size} клітин) - {orientation_text} | Залишилось: {remaining}"
            )
    
    def update_score(self):
        """Оновлює панель з рахунком гри"""
        self.score_label.config(
            text=f"Попадань гравця: {self.player_score} | Попадань комп'ютера: {self.computer_score}"
        )


def main():
    """Головна функція для запуску гри"""
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()
