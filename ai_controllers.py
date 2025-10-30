import random
from typing import Tuple, List, Set, Optional
from Board import Board


class IAIController:
    """Базовий інтерфейс AI."""
    def perform_attack(self) -> Tuple[int, int]:
        raise NotImplementedError

    def register_result(self, x: int, y: int, hit: bool, sunk: bool):
        """Опціональний метод для обробки результатів атаки (реалізується у HardAI)."""
        pass


class EasyAIController(IAIController):
    """Простий бот: стріляє випадково, уникаючи повторів."""
    def __init__(self, board: Board):
        self.board = board
        self.size = board.size
        self.attacked: Set[Tuple[int, int]] = set()

    def perform_attack(self) -> Tuple[int, int]:
        while True:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if (x, y) not in self.attacked:
                self.attacked.add((x, y))
                return x, y


class HardAIController(IAIController):
    """Складний бот: покращена стратегія 'пошук і добивання'."""
    def __init__(self, board: Board):
        self.board = board
        self.size = board.size
        self.attacked: Set[Tuple[int, int]] = set()
        self.hits: List[Tuple[int, int]] = []         # поточні не потоплені влучання
        self.target_queue: List[Tuple[int, int]] = [] # пріоритетні цілі для добивання

    def perform_attack(self) -> Tuple[Optional[int], Optional[int]]:
        # 1) Черга добивання — найвищий пріоритет
        while self.target_queue:
            x, y = self.target_queue.pop(0)
            if self._is_valid_board_cell(x, y):
                self.attacked.add((x, y))
                return x, y

        # 2) Якщо є вирівняна група хітів — визначаємо напрямок та продовжуємо лінією
        aligned = self._get_best_aligned_group()
        if len(aligned) >= 2:
            # сортуємо по осі і пробуємо продовжити в обидва боки
            if aligned[0][0] == aligned[-1][0]:  # same x => vertical
                x_fixed = aligned[0][0]
                ys = sorted([p[1] for p in aligned])
                # вперед від max
                ny = ys[-1] + 1
                if self._is_valid_board_cell(x_fixed, ny):
                    self.attacked.add((x_fixed, ny)); return x_fixed, ny
                # назад від min
                ny = ys[0] - 1
                if self._is_valid_board_cell(x_fixed, ny):
                    self.attacked.add((x_fixed, ny)); return x_fixed, ny
            else:  # same y => horizontal
                y_fixed = aligned[0][1]
                xs = sorted([p[0] for p in aligned])
                nx = xs[-1] + 1
                if self._is_valid_board_cell(nx, y_fixed):
                    self.attacked.add((nx, y_fixed)); return nx, y_fixed
                nx = xs[0] - 1
                if self._is_valid_board_cell(nx, y_fixed):
                    self.attacked.add((nx, y_fixed)); return nx, y_fixed

        # 3) Якщо є один хіт або не вдалося продовжити — додати сусідів останнього хіта в чергу
        if len(self.hits) >= 1:
            # зосереджуємось на останньому хіті (якщо aligned не дав ходу)
            hx, hy = self.hits[-1]
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = hx + dx, hy + dy
                if self._is_valid_board_cell(nx, ny) and (nx, ny) not in self.target_queue:
                    self.target_queue.append((nx, ny))
            while self.target_queue:
                x, y = self.target_queue.pop(0)
                if self._is_valid_board_cell(x, y):
                    self.attacked.add((x, y)); return x, y

        # 4) Режим пошуку — шахова стратегія
        candidates = [
            (x, y)
            for y in range(self.size)
            for x in range(self.size)
            if (x + y) % 2 == 0 and self._is_valid_board_cell(x, y)
        ]
        if candidates:
            choice = random.choice(candidates)
            self.attacked.add(choice)
            return choice

        # 5) Фолбек — будь-яка перша доступна клітинка
        for y in range(self.size):
            for x in range(self.size):
                if self._is_valid_board_cell(x, y):
                    self.attacked.add((x, y)); return x, y

        return None, None

    def register_result(self, x: int, y: int, hit: bool, sunk: bool):
        """Оновлює стан AI після пострілу."""
        self.attacked.add((x, y))

        if hit:
            self.hits.append((x, y))
            # додаємо сусідів як потенційні добивання
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = x + dx, y + dy
                if self._is_valid_board_cell(nx, ny) and (nx, ny) not in self.target_queue:
                    self.target_queue.append((nx, ny))

            if sunk:
                # помічаємо навколишні клітини як відмічені і очищуємо стан влучань
                for hx, hy in list(self.hits):
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = hx + dx, hy + dy
                            if 0 <= nx < self.size and 0 <= ny < self.size:
                                self.attacked.add((nx, ny))
                self.hits.clear()
                self.target_queue.clear()
        else:
            # промах: якщо немає активних хітів — очищаємо чергу
            if not self.hits:
                self.target_queue.clear()

    def _get_best_aligned_group(self) -> List[Tuple[int,int]]:
        if not self.hits:
            return []
        # групування по x (vertical) та по y (horizontal)
        by_x = {}
        by_y = {}
        for x,y in self.hits:
            by_x.setdefault(x, []).append((x,y))
            by_y.setdefault(y, []).append((x,y))
        # обираємо найбільшу групу
        vx = max(by_x.values(), key=len) if by_x else []
        vy = max(by_y.values(), key=len) if by_y else []
        best = vx if len(vx) >= len(vy) else vy
        # сортуємо за координатою вздовж лінії
        if not best:
            return []
        if len(best) == 1:
            return best
        if best[0][0] == best[-1][0]:  # vertical -> sort by y
            return sorted(best, key=lambda p: p[1])
        else:
            return sorted(best, key=lambda p: p[0])

    def _is_valid_board_cell(self, x: int, y: int) -> bool:
        """Перевірка валідності клітинки з урахуванням board.revealed і attacked set."""
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        if (x, y) in self.attacked:
            return False
        if self.board.revealed[y][x]:
            return False
        return True