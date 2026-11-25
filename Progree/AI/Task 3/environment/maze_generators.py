"""
Procedural Maze and Terrain Generators for Grid Pathfinding.
Includes:
- Recursive Backtracker (DFS)
- Randomized Prim's Algorithm
- Recursive Division
- Random Obstacle Density Arrays
- Cellular Automata (Cave Generation)
- Weighted Terrain Cluster Generator
"""

import random
from typing import List, Tuple, Set
from .grid import Grid, CellType

def generate_random_obstacles(grid: Grid, density: float = 0.25, seed: int = None) -> None:
    """Fills the grid with randomly distributed walls according to density."""
    if seed is not None:
        random.seed(seed)
    grid.clear_all()
    for r in range(grid.rows):
        for c in range(grid.cols):
            if (r, c) == grid.start or (r, c) == grid.goal:
                continue
            if random.random() < density:
                grid.set_cell(r, c, CellType.WALL)

def generate_recursive_backtracker(grid: Grid, seed: int = None) -> None:
    """Generates a perfect maze with deep, winding passages using randomized DFS."""
    if seed is not None:
        random.seed(seed)
    # Fill grid with walls first
    for r in range(grid.rows):
        for c in range(grid.cols):
            grid.set_cell(r, c, CellType.WALL)

    # Pick a starting cell (odd coordinates work best for 2-step carving)
    start_r = (grid.start[0] // 2) * 2 + 1 if grid.rows > 2 else 0
    start_c = (grid.start[1] // 2) * 2 + 1 if grid.cols > 2 else 0
    start_r = min(start_r, grid.rows - 1)
    start_c = min(start_c, grid.cols - 1)

    grid.set_cell(start_r, start_c, CellType.EMPTY)
    stack = [(start_r, start_c)]
    visited = {(start_r, start_c)}

    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        cr, cc = stack[-1]
        neighbors = []
        for dr, dc in directions:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < grid.rows and 0 <= nc < grid.cols:
                if (nr, nc) not in visited:
                    neighbors.append((nr, nc, dr, dc))

        if neighbors:
            nr, nc, dr, dc = random.choice(neighbors)
            # Carve through intermediate cell
            mid_r, mid_c = cr + dr // 2, cc + dc // 2
            grid.set_cell(mid_r, mid_c, CellType.EMPTY)
            grid.set_cell(nr, nc, CellType.EMPTY)
            visited.add((nr, nc))
            visited.add((mid_r, mid_c))
            stack.append((nr, nc))
        else:
            stack.pop()

    # Ensure start and goal are open and connected to adjacent paths
    grid.set_cell(grid.start[0], grid.start[1], CellType.EMPTY)
    grid.set_cell(grid.goal[0], grid.goal[1], CellType.EMPTY)
    _connect_node_to_nearest_open(grid, grid.start)
    _connect_node_to_nearest_open(grid, grid.goal)

def generate_prims(grid: Grid, seed: int = None) -> None:
    """Generates a maze with many short dead ends and branches using Randomized Prim's algorithm."""
    if seed is not None:
        random.seed(seed)
    # Fill grid with walls
    for r in range(grid.rows):
        for c in range(grid.cols):
            grid.set_cell(r, c, CellType.WALL)

    start_r, start_c = grid.start
    grid.set_cell(start_r, start_c, CellType.EMPTY)

    # Frontier walls: (wall_r, wall_c, origin_r, origin_c)
    walls = []
    for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        nr, nc = start_r + dr, start_c + dc
        if 0 <= nr < grid.rows and 0 <= nc < grid.cols:
            walls.append((nr, nc, start_r, start_c))

    visited = {(start_r, start_c)}

    while walls:
        idx = random.randint(0, len(walls) - 1)
        wr, wc, orig_r, orig_c = walls.pop(idx)

        if (wr, wc) not in visited:
            mid_r = (wr + orig_r) // 2
            mid_c = (wc + orig_c) // 2
            grid.set_cell(mid_r, mid_c, CellType.EMPTY)
            grid.set_cell(wr, wc, CellType.EMPTY)
            visited.add((wr, wc))
            visited.add((mid_r, mid_c))

            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = wr + dr, wc + dc
                if 0 <= nr < grid.rows and 0 <= nc < grid.cols and (nr, nc) not in visited:
                    walls.append((nr, nc, wr, wc))

    grid.set_cell(grid.start[0], grid.start[1], CellType.EMPTY)
    grid.set_cell(grid.goal[0], grid.goal[1], CellType.EMPTY)
    _connect_node_to_nearest_open(grid, grid.start)
    _connect_node_to_nearest_open(grid, grid.goal)

def generate_recursive_division(grid: Grid, seed: int = None) -> None:
    """Generates structured rooms and corridors by recursively subdividing chambers."""
    if seed is not None:
        random.seed(seed)
    grid.clear_all()

    # Outer boundary walls
    for r in range(grid.rows):
        grid.set_cell(r, 0, CellType.WALL)
        grid.set_cell(r, grid.cols - 1, CellType.WALL)
    for c in range(grid.cols):
        grid.set_cell(0, c, CellType.WALL)
        grid.set_cell(grid.rows - 1, c, CellType.WALL)

    def divide(r1, r2, c1, c2):
        if r2 - r1 < 3 or c2 - c1 < 3:
            return

        # Choose orientation: horizontal if height > width, vertical if width > height, else random
        horizontal = (r2 - r1) > (c2 - c1) if (r2 - r1) != (c2 - c1) else random.choice([True, False])

        if horizontal:
            # Pick a wall row (must be odd/even consistent if possible)
            wall_r = random.randrange(r1 + 1, r2, 2) if (r2 - r1 >= 4) else random.randint(r1 + 1, r2 - 1)
            # Pick passage column
            passage_c = random.randint(c1, c2)

            for c in range(c1, c2 + 1):
                if c != passage_c:
                    grid.set_cell(wall_r, c, CellType.WALL)

            divide(r1, wall_r - 1, c1, c2)
            divide(wall_r + 1, r2, c1, c2)
        else:
            wall_c = random.randrange(c1 + 1, c2, 2) if (c2 - c1 >= 4) else random.randint(c1 + 1, c2 - 1)
            passage_r = random.randint(r1, r2)

            for r in range(r1, r2 + 1):
                if r != passage_r:
                    grid.set_cell(r, wall_c, CellType.WALL)

            divide(r1, r2, c1, wall_c - 1)
            divide(r1, r2, wall_c + 1, c2)

    divide(1, grid.rows - 2, 1, grid.cols - 2)
    grid.set_cell(grid.start[0], grid.start[1], CellType.EMPTY)
    grid.set_cell(grid.goal[0], grid.goal[1], CellType.EMPTY)

def generate_cellular_automata(grid: Grid, initial_wall_prob: float = 0.45, iterations: int = 4, seed: int = None) -> None:
    """Generates organic cave-like maze environments using B5678/S45678 Cellular Automata rules."""
    if seed is not None:
        random.seed(seed)
    grid.clear_all()

    # Random initialization
    map_state = [[1 if random.random() < initial_wall_prob else 0 for _ in range(grid.cols)] for _ in range(grid.rows)]

    for _ in range(iterations):
        new_state = [[0 for _ in range(grid.cols)] for _ in range(grid.rows)]
        for r in range(grid.rows):
            for c in range(grid.cols):
                # Count walls in 3x3 neighborhood
                wall_count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if not (0 <= nr < grid.rows and 0 <= nc < grid.cols):
                            wall_count += 1
                        elif map_state[nr][nc] == 1:
                            wall_count += 1

                # Smooth rule: 5 or more neighbors -> wall
                if wall_count >= 5:
                    new_state[r][c] = 1
                else:
                    new_state[r][c] = 0
        map_state = new_state

    for r in range(grid.rows):
        for c in range(grid.cols):
            if (r, c) != grid.start and (r, c) != grid.goal:
                grid.set_cell(r, c, CellType.WALL if map_state[r][c] == 1 else CellType.EMPTY)

    grid.set_cell(grid.start[0], grid.start[1], CellType.EMPTY)
    grid.set_cell(grid.goal[0], grid.goal[1], CellType.EMPTY)

def generate_weighted_terrain_map(grid: Grid, seed: int = None) -> None:
    """Generates natural terrain clusters containing Mud, Water, and Forest zones."""
    if seed is not None:
        random.seed(seed)
    
    # Place some random wall pillars
    for r in range(grid.rows):
        for c in range(grid.cols):
            if (r, c) not in (grid.start, grid.goal) and random.random() < 0.12:
                grid.set_cell(r, c, CellType.WALL)

    # Spawn cluster centers for Mud, Water, Forest
    cluster_types = [CellType.MUD, CellType.WATER, CellType.FOREST]
    num_clusters = max(3, (grid.rows * grid.cols) // 100)

    for _ in range(num_clusters):
        t = random.choice(cluster_types)
        cr = random.randint(0, grid.rows - 1)
        cc = random.randint(0, grid.cols - 1)
        radius = random.randint(2, 5)

        for r in range(max(0, cr - radius), min(grid.rows, cr + radius + 1)):
            for c in range(max(0, cc - radius), min(grid.cols, cc + radius + 1)):
                dist = ((r - cr) ** 2 + (c - cc) ** 2) ** 0.5
                if dist <= radius and grid.get_cell(r, c) == CellType.EMPTY:
                    if (r, c) != grid.start and (r, c) != grid.goal:
                        if random.random() < 0.8:
                            grid.set_cell(r, c, t)

    grid.set_cell(grid.start[0], grid.start[1], CellType.EMPTY)
    grid.set_cell(grid.goal[0], grid.goal[1], CellType.EMPTY)

def _connect_node_to_nearest_open(grid: Grid, node: Tuple[int, int]) -> None:
    """Carves a straight opening from node to the closest open cell if blocked."""
    r, c = node
    # If already has an open neighbor, nothing to do
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if grid.in_bounds(nr, nc) and grid.get_cell(nr, nc) != CellType.WALL:
            return

    # Otherwise carve to nearest cell
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if grid.in_bounds(nr, nc):
            grid.set_cell(nr, nc, CellType.EMPTY)
            return
