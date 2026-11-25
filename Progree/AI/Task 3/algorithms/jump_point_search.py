"""
Jump Point Search (JPS) Algorithm.
Prunes redundant symmetry in uniform grids by jumping along straight lines to identify key decision vertices.
"""

import heapq
import time
from typing import List, Tuple, Dict, Any, Generator, Optional, Set
from .base import (
    BaseSearchAlgorithm, SearchResult, StepLog, HeuristicType,
    calculate_heuristic, reconstruct_path, calculate_path_cost
)

class JumpPointSearch(BaseSearchAlgorithm):
    def __init__(self, heuristic_type: HeuristicType = HeuristicType.OCTILE):
        super().__init__(f"Jump Point Search (JPS)")
        self.heuristic_type = heuristic_type

    def _jump(self, grid: Any, current: Tuple[int, int], direction: Tuple[int, int], goal: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Recursively steps in direction until a jump point (or obstacle/goal) is hit."""
        r, c = current
        dr, dc = direction
        nr, nc = r + dr, c + dc

        if not grid.is_walkable(nr, nc):
            return None

        next_node = (nr, nc)
        if next_node == goal:
            return next_node

        # Check for forced neighbors
        if dr != 0 and dc != 0:
            # Diagonal jump
            # Forced neighbor checks:
            if (not grid.is_walkable(r, nc) and grid.is_walkable(r - dr, nc)) or \
               (not grid.is_walkable(nr, c) and grid.is_walkable(nr, c - dc)):
                return next_node
            # Check horizontal and vertical projections
            if self._jump(grid, next_node, (dr, 0), goal) is not None or \
               self._jump(grid, next_node, (0, dc), goal) is not None:
                return next_node
        else:
            # Orthogonal jump
            if dr != 0:
                # Vertical
                if (not grid.is_walkable(nr, c + 1) and grid.is_walkable(nr + dr, c + 1)) or \
                   (not grid.is_walkable(nr, c - 1) and grid.is_walkable(nr + dr, c - 1)):
                    return next_node
            else:
                # Horizontal
                if (not grid.is_walkable(r + 1, nc) and grid.is_walkable(r + 1, nc + dc)) or \
                   (not grid.is_walkable(r - 1, nc) and grid.is_walkable(r - 1, nc + dc)):
                    return next_node

        return self._jump(grid, next_node, direction, goal)

    def _get_jump_successors(self, grid: Any, current: Tuple[int, int], parent: Optional[Tuple[int, int]], goal: Tuple[int, int]) -> List[Tuple[Tuple[int, int], float]]:
        successors = []
        r, c = current

        # Determine natural search directions based on parent incoming direction
        if parent is None:
            # All 8 directions from start
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            pr, pc = parent
            dr = max(-1, min(1, r - pr))
            dc = max(-1, min(1, c - pc))
            directions = []
            if dr != 0 and dc != 0:
                # Diagonal incoming
                directions.extend([(dr, 0), (0, dc), (dr, dc)])
                if not grid.is_walkable(r - dr, c):
                    directions.append((-dr, dc))
                if not grid.is_walkable(r, c - dc):
                    directions.append((dr, -dc))
            else:
                if dr != 0:
                    directions.append((dr, 0))
                    if not grid.is_walkable(r, c + 1):
                        directions.append((dr, 1))
                    if not grid.is_walkable(r, c - 1):
                        directions.append((dr, -1))
                else:
                    directions.append((0, dc))
                    if not grid.is_walkable(r + 1, c):
                        directions.append((1, dc))
                    if not grid.is_walkable(r - 1, c):
                        directions.append((-1, dc))

        for direction in directions:
            jump_point = self._jump(grid, current, direction, goal)
            if jump_point is not None:
                cost = calculate_heuristic(HeuristicType.EUCLIDEAN, current, jump_point)
                successors.append((jump_point, cost))

        return successors

    def search(self, grid: Any, allow_diagonal: bool = True, **kwargs) -> SearchResult:
        start_time = time.perf_counter_ns()
        start = grid.start
        goal = grid.goal
        total_walkable = grid.total_walkable_cells

        if start == goal:
            return SearchResult(
                algorithm_name=self.name,
                success=True,
                path=[start],
                path_cost=0.0,
                step_count=0,
                expanded_nodes_count=0,
                expanded_density=0.0,
                runtime_ms=(time.perf_counter_ns() - start_time) / 1e6,
                peak_frontier=1
            )

        tie_counter = 0
        open_heap: List[Tuple[float, float, int, Tuple[int, int]]] = []
        open_set: Set[Tuple[int, int]] = {start}
        closed_set: Set[Tuple[int, int]] = set()

        g_score: Dict[Tuple[int, int], float] = {start: 0.0}
        h_start = calculate_heuristic(self.heuristic_type, start, goal)
        f_score: Dict[Tuple[int, int], float] = {start: h_start}
        parent_map: Dict[Tuple[int, int], Tuple[int, int]] = {}

        heapq.heappush(open_heap, (h_start, h_start, tie_counter, start))
        peak_frontier = 1
        steps = 0
        step_logs: List[StepLog] = []

        while open_heap:
            _, _, _, current = heapq.heappop(open_heap)
            if current in open_set:
                open_set.remove(current)

            if current in closed_set:
                continue

            closed_set.add(current)
            steps += 1
            peak_frontier = max(peak_frontier, len(open_heap))

            step_logs.append(StepLog(
                step_num=steps,
                current_node=current,
                action="jump_expand",
                open_nodes=list(open_set),
                closed_nodes=list(closed_set),
                parent_map=parent_map.copy()
            ))

            if current == goal:
                elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
                # Reconstruct dense path from jump points
                jump_path = reconstruct_path(parent_map, start, goal)
                dense_path = self._interpolate_path(jump_path)
                path_cost = calculate_path_cost(grid, dense_path)
                expanded_count = len(closed_set)
                density = expanded_count / total_walkable if total_walkable > 0 else 0.0

                return SearchResult(
                    algorithm_name=self.name,
                    success=True,
                    path=dense_path,
                    path_cost=path_cost,
                    step_count=steps,
                    expanded_nodes_count=expanded_count,
                    expanded_density=density,
                    runtime_ms=elapsed_ms,
                    peak_frontier=peak_frontier,
                    explored_nodes=closed_set,
                    step_logs=step_logs,
                    metadata={"jump_nodes_count": len(jump_path)}
                )

            curr_parent = parent_map.get(current)
            successors = self._get_jump_successors(grid, current, curr_parent, goal)

            for neighbor, step_cost in successors:
                if neighbor in closed_set:
                    continue

                tentative_g = g_score[current] + step_cost
                if tentative_g < g_score.get(neighbor, float('inf')):
                    parent_map[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h_val = calculate_heuristic(self.heuristic_type, neighbor, goal)
                    f_val = tentative_g + h_val
                    f_score[neighbor] = f_val

                    tie_counter += 1
                    heapq.heappush(open_heap, (f_val, h_val, tie_counter, neighbor))
                    open_set.add(neighbor)

        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
        return SearchResult(
            algorithm_name=self.name,
            success=False,
            path=[],
            path_cost=0.0,
            step_count=steps,
            expanded_nodes_count=len(closed_set),
            expanded_density=len(closed_set) / total_walkable if total_walkable > 0 else 0.0,
            runtime_ms=elapsed_ms,
            peak_frontier=peak_frontier,
            explored_nodes=closed_set,
            step_logs=step_logs
        )

    def _interpolate_path(self, jump_path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if not jump_path:
            return []
        dense = [jump_path[0]]
        for i in range(len(jump_path) - 1):
            r1, c1 = jump_path[i]
            r2, c2 = jump_path[i + 1]
            dr = 0 if r2 == r1 else (1 if r2 > r1 else -1)
            dc = 0 if c2 == c1 else (1 if c2 > c1 else -1)
            curr_r, curr_c = r1 + dr, c1 + dc
            while (curr_r, curr_c) != (r2, c2):
                dense.append((curr_r, curr_c))
                curr_r += dr
                curr_c += dc
            dense.append((r2, c2))
        return dense

    def step_generator(self, grid: Any, allow_diagonal: bool = True, **kwargs) -> Generator[Dict[str, Any], None, SearchResult]:
        # Fallback to direct search with complete result yield
        result = self.search(grid, allow_diagonal=allow_diagonal, **kwargs)
        yield {"type": "init", "open": [grid.start], "closed": [], "current": grid.start}
        for i, node in enumerate(result.explored_nodes):
            if i % 5 == 0:
                yield {"type": "step", "current": node, "open": [], "closed": list(result.explored_nodes)[:i], "steps": i}
        yield {"type": "complete", "result": result, "path": result.path}
        return result
