from enum import Enum
from typing import List, Tuple, Optional
import random

class CellState(Enum):
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3

class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1

class Ship:
    def __init__(self, size: int, position: Tuple[int, int], orientation: Orientation):
        self.size = size
        self.position = position
        self.orientation = orientation
        self.hits = 0

    def is_sunk(self) -> bool:
        return self.hits >= self.size

    def get_coordinates(self) -> List[Tuple[int, int]]:
        coords = []
        x, y = self.position
        for i in range(self.size):
            if self.orientation == Orientation.HORIZONTAL:
                coords.append((x + i, y))
            else:
                coords.append((x, y + i))
        return coords

class Board:
    """Клас ігрового поля для морського бою"""
    
    def __init__(self, size: int = 10, ship_sizes: List[int] = None):
        self.size = size
        # Сітка зі станами клітинок
        self.grid = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self.ships: List[Ship] = []
        # Матриця відкритих клітинок (для відстеження пострілів)
        self.revealed = [[False for _ in range(size)] for _ in range(size)]
        # Конфігурація кораблів
        self.ship_sizes = ship_sizes if ship_sizes else [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    
    def can_place_ship(self, size: int, x: int, y: int, orientation: Orientation) -> bool:
        if orientation == Orientation.HORIZONTAL:
            if x + size > self.size:
                return False
            for i in range(size):
                if not self._is_cell_free(x + i, y):
                    return False
        else:
            if y + size > self.size:
                return False
            for i in range(size):
                if not self._is_cell_free(x, y + i):
                    return False
        return True
    
    def _is_cell_free(self, x: int, y: int) -> bool:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.grid[ny][nx] == CellState.SHIP:
                        return False
        return True
    
    def place_ship(self, size: int, x: int, y: int, orientation: Orientation) -> bool:
        if not self.can_place_ship(size, x, y, orientation):
            return False
        
        ship = Ship(size, (x, y), orientation)
        self.ships.append(ship)
        
        for coord_x, coord_y in ship.get_coordinates():
            self.grid[coord_y][coord_x] = CellState.SHIP
        
        return True
    
    def attack(self, x: int, y: int) -> Tuple[bool, bool, Optional[Ship]]:
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False, False, None
        
        self.revealed[y][x] = True
        
        if self.grid[y][x] == CellState.SHIP:
            self.grid[y][x] = CellState.HIT
            
            for ship in self.ships:
                if (x, y) in ship.get_coordinates():
                    ship.hits += 1
                    if ship.is_sunk():
                        self.mark_surrounding_as_miss(ship)
                        return True, True, ship
                    return True, False, ship
            
            return True, False, None
        elif self.grid[y][x] == CellState.EMPTY:
            self.grid[y][x] = CellState.MISS
            return False, False, None
        
        return False, False, None
    
    def mark_surrounding_as_miss(self, ship: Ship):
        ship_coords = ship.get_coordinates()
        for sx, sy in ship_coords:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = sx + dx, sy + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.grid[ny][nx] == CellState.EMPTY:
                            self.grid[ny][nx] = CellState.MISS
                            self.revealed[ny][nx] = True
    
    def all_ships_sunk(self) -> bool:
        return all(ship.is_sunk() for ship in self.ships)
    
    def place_ships_randomly(self):
        ship_sizes = self.ship_sizes
        
        for size in ship_sizes:
            placed = False
            attempts = 0
            while not placed and attempts < 1000:
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                orientation = random.choice([Orientation.HORIZONTAL, Orientation.VERTICAL])
                placed = self.place_ship(size, x, y, orientation)
                attempts += 1