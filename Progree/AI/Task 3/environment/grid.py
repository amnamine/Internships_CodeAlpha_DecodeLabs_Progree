"""
Grid Environment Representation for Pathfinding Search Engine.
Handles 2D matrix grids, node properties, terrain weights, obstacles, and serialization.
"""

from enum import IntEnum
from typing import List, Tuple, Optional, Dict, Any, Set
import json
import math

class CellType(IntEnum):
    EMPTY = 0
    WALL = 1
    MUD = 2      # Terrain with cost multiplier (3.0)
    WATER = 3    # Terrain with cost multiplier (5.0)
    FOREST = 4   # Terrain with cost multiplier (2.0)

# Cost mapping for each cell type
CELL_COSTS = {
    CellType.EMPTY: 1.0,
    CellType.WALL: float('inf'),
    CellType.MUD: 3.0,
    CellType.WATER: 5.0,
    CellType.FOREST: 2.0,
}

class Grid:
    def __init__(self, rows: int = 25, cols: int = 40):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[int]] = [[CellType.EMPTY for _ in range(cols)] for _ in range(rows)]
        self.start: Tuple[int, int] = (rows // 2, max(1, cols // 8))
        self.goal: Tuple[int, int] = (rows // 2, cols - max(2, cols // 8))

    def reset_dimensions(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[CellType.EMPTY for _ in range(cols)] for _ in range(rows)]
        self.start = (rows // 2, max(1, cols // 8))
        self.goal = (rows // 2, cols - max(2, cols // 8))

    def clear_all(self):
        """Clears all walls and terrain, keeping start and goal."""
        self.grid = [[CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

    def clear_terrain(self):
        """Clears only weighted terrain (mud, water, forest), keeping walls."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] not in (CellType.WALL, CellType.EMPTY):
                    self.grid[r][c] = CellType.EMPTY

    def set_cell(self, r: int, c: int, cell_type: CellType) -> bool:
        if not self.in_bounds(r, c):
            return False
        if (r, c) == self.start or (r, c) == self.goal:
            if cell_type == CellType.WALL:
                return False
        self.grid[r][c] = int(cell_type)
        return True

    def get_cell(self, r: int, c: int) -> int:
        if not self.in_bounds(r, c):
            return CellType.WALL
        return self.grid[r][c]

    def set_start(self, r: int, c: int) -> bool:
        if self.in_bounds(r, c) and (r, c) != self.goal:
            self.start = (r, c)
            if self.grid[r][c] == CellType.WALL:
                self.grid[r][c] = CellType.EMPTY
            return True
        return False

    def set_goal(self, r: int, c: int) -> bool:
        if self.in_bounds(r, c) and (r, c) != self.start:
            self.goal = (r, c)
            if self.grid[r][c] == CellType.WALL:
                self.grid[r][c] = CellType.EMPTY
            return True
        return False

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, r: int, c: int) -> bool:
        return self.in_bounds(r, c) and self.grid[r][c] != CellType.WALL

    def get_cost(self, r: int, c: int) -> float:
        if not self.is_walkable(r, c):
            return float('inf')
        return CELL_COSTS.get(CellType(self.grid[r][c]), 1.0)

    def get_move_cost(self, from_node: Tuple[int, int], to_node: Tuple[int, int]) -> float:
        """Returns the cost to step from from_node to to_node, handling diagonal distance scaling."""
        base_cost = self.get_cost(to_node[0], to_node[1])
        dr = abs(to_node[0] - from_node[0])
        dc = abs(to_node[1] - from_node[1])
        if dr > 0 and dc > 0:
            return base_cost * math.sqrt(2)
        return base_cost

    def get_neighbors(self, node: Tuple[int, int], allow_diagonal: bool = False, prevent_corner_cutting: bool = True) -> List[Tuple[int, int]]:
        r, c = node
        neighbors = []
        
        orthogonal = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for dr, dc in orthogonal:
            nr, nc = r + dr, c + dc
            if self.is_walkable(nr, nc):
                neighbors.append((nr, nc))

        if allow_diagonal:
            diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in diagonals:
                nr, nc = r + dr, c + dc
                if self.is_walkable(nr, nc):
                    if prevent_corner_cutting:
                        if self.is_walkable(r + dr, c) and self.is_walkable(r, c + dc):
                            neighbors.append((nr, nc))
                    else:
                        neighbors.append((nr, nc))

        return neighbors

    @property
    def total_cells(self) -> int:
        return self.rows * self.cols

    @property
    def total_walkable_cells(self) -> int:
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != CellType.WALL:
                    count += 1
        return count

    @property
    def obstacle_density(self) -> float:
        walls = sum(1 for r in range(self.rows) for c in range(self.cols) if self.grid[r][c] == CellType.WALL)
        return walls / self.total_cells if self.total_cells > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "start": list(self.start),
            "goal": list(self.goal),
            "grid": self.grid
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Grid":
        grid_obj = cls(rows=data["rows"], cols=data["cols"])
        grid_obj.start = tuple(data["start"])
        grid_obj.goal = tuple(data["goal"])
        grid_obj.grid = data["grid"]
        return grid_obj
