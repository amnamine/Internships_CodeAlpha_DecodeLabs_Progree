"""
Breadth-First Search (BFS) and Depth-First Search (DFS) implementations.
Provides baseline unweighted graph search comparisons.
"""

from collections import deque
import time
from typing import List, Tuple, Dict, Any, Generator, Optional, Set
from .base import (
    BaseSearchAlgorithm, SearchResult, StepLog,
    reconstruct_path, calculate_path_cost
)

class BreadthFirstSearch(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("Breadth-First Search (BFS)")

    def search(self, grid: Any, allow_diagonal: bool = False, **kwargs) -> SearchResult:
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

        queue = deque([start])
        visited: Set[Tuple[int, int]] = {start}
        parent_map: Dict[Tuple[int, int], Tuple[int, int]] = {}
        steps = 0
        peak_frontier = 1
        step_logs: List[StepLog] = []

        while queue:
            current = queue.popleft()
            steps += 1
            peak_frontier = max(peak_frontier, len(queue))

            step_logs.append(StepLog(
                step_num=steps,
                current_node=current,
                action="expand",
                open_nodes=list(queue),
                closed_nodes=list(visited),
                parent_map=parent_map.copy()
            ))

            if current == goal:
                elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
                path = reconstruct_path(parent_map, start, goal)
                path_cost = calculate_path_cost(grid, path)
                expanded_count = len(visited)
                density = expanded_count / total_walkable if total_walkable > 0 else 0.0

                return SearchResult(
                    algorithm_name=self.name,
                    success=True,
                    path=path,
                    path_cost=path_cost,
                    step_count=steps,
                    expanded_nodes_count=expanded_count,
                    expanded_density=density,
                    runtime_ms=elapsed_ms,
                    peak_frontier=peak_frontier,
                    explored_nodes=visited,
                    step_logs=step_logs
                )

            for neighbor in grid.get_neighbors(current, allow_diagonal=allow_diagonal):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)

        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
        return SearchResult(
            algorithm_name=self.name,
            success=False,
            path=[],
            path_cost=0.0,
            step_count=steps,
            expanded_nodes_count=len(visited),
            expanded_density=len(visited) / total_walkable if total_walkable > 0 else 0.0,
            runtime_ms=elapsed_ms,
            peak_frontier=peak_frontier,
            explored_nodes=visited,
            step_logs=step_logs
        )

    def step_generator(self, grid: Any, allow_diagonal: bool = False, **kwargs) -> Generator[Dict[str, Any], None, SearchResult]:
        start_time = time.perf_counter_ns()
        start = grid.start
        goal = grid.goal
        total_walkable = grid.total_walkable_cells

        if start == goal:
            res = SearchResult(
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
            yield {"type": "complete", "result": res}
            return res

        queue = deque([start])
        visited: Set[Tuple[int, int]] = {start}
        parent_map: Dict[Tuple[int, int], Tuple[int, int]] = {}
        steps = 0
        peak_frontier = 1
        step_logs: List[StepLog] = []

        yield {"type": "init", "open": [start], "closed": [], "current": start}

        while queue:
            current = queue.popleft()
            steps += 1
            peak_frontier = max(peak_frontier, len(queue))

            log = StepLog(
                step_num=steps,
                current_node=current,
                action="expand",
                open_nodes=list(queue),
                closed_nodes=list(visited),
                parent_map=parent_map.copy()
            )
            step_logs.append(log)

            yield {
                "type": "step",
                "current": current,
                "open": list(queue),
                "closed": list(visited),
                "steps": steps,
            }

            if current == goal:
                elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
                path = reconstruct_path(parent_map, start, goal)
                path_cost = calculate_path_cost(grid, path)
                expanded_count = len(visited)
                density = expanded_count / total_walkable if total_walkable > 0 else 0.0

                result = SearchResult(
                    algorithm_name=self.name,
                    success=True,
                    path=path,
                    path_cost=path_cost,
                    step_count=steps,
                    expanded_nodes_count=expanded_count,
                    expanded_density=density,
                    runtime_ms=elapsed_ms,
                    peak_frontier=peak_frontier,
                    explored_nodes=visited,
                    step_logs=step_logs
                )
                yield {"type": "complete", "result": result, "path": path}
                return result

            for neighbor in grid.get_neighbors(current, allow_diagonal=allow_diagonal):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)

        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
        result = SearchResult(
            algorithm_name=self.name,
            success=False,
            path=[],
            path_cost=0.0,
            step_count=steps,
            expanded_nodes_count=len(visited),
            expanded_density=len(visited) / total_walkable if total_walkable > 0 else 0.0,
            runtime_ms=elapsed_ms,
            peak_frontier=peak_frontier,
            explored_nodes=visited,
            step_logs=step_logs
        )
        yield {"type": "complete", "result": result, "path": []}
        return result


class DepthFirstSearch(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("Depth-First Search (DFS)")

    def search(self, grid: Any, allow_diagonal: bool = False, **kwargs) -> SearchResult:
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

        stack = [start]
        visited: Set[Tuple[int, int]] = set()
        parent_map: Dict[Tuple[int, int], Tuple[int, int]] = {}
        steps = 0
        peak_frontier = 1
        step_logs: List[StepLog] = []

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            steps += 1
            peak_frontier = max(peak_frontier, len(stack))

            step_logs.append(StepLog(
                step_num=steps,
                current_node=current,
                action="expand",
                open_nodes=list(stack),
                closed_nodes=list(visited),
                parent_map=parent_map.copy()
            ))

            if current == goal:
                elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
                path = reconstruct_path(parent_map, start, goal)
                path_cost = calculate_path_cost(grid, path)
                expanded_count = len(visited)
                density = expanded_count / total_walkable if total_walkable > 0 else 0.0

                return SearchResult(
                    algorithm_name=self.name,
                    success=True,
                    path=path,
                    path_cost=path_cost,
                    step_count=steps,
                    expanded_nodes_count=expanded_count,
                    expanded_density=density,
                    runtime_ms=elapsed_ms,
                    peak_frontier=peak_frontier,
                    explored_nodes=visited,
                    step_logs=step_logs
                )

            for neighbor in grid.get_neighbors(current, allow_diagonal=allow_diagonal):
                if neighbor not in visited:
                    parent_map[neighbor] = current
                    stack.append(neighbor)

        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
        return SearchResult(
            algorithm_name=self.name,
            success=False,
            path=[],
            path_cost=0.0,
            step_count=steps,
            expanded_nodes_count=len(visited),
            expanded_density=len(visited) / total_walkable if total_walkable > 0 else 0.0,
            runtime_ms=elapsed_ms,
            peak_frontier=peak_frontier,
            explored_nodes=visited,
            step_logs=step_logs
        )

    def step_generator(self, grid: Any, allow_diagonal: bool = False, **kwargs) -> Generator[Dict[str, Any], None, SearchResult]:
        start_time = time.perf_counter_ns()
        start = grid.start
        goal = grid.goal
        total_walkable = grid.total_walkable_cells

        if start == goal:
            res = SearchResult(
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
            yield {"type": "complete", "result": res}
            return res

        stack = [start]
        visited: Set[Tuple[int, int]] = set()
        parent_map: Dict[Tuple[int, int], Tuple[int, int]] = {}
        steps = 0
        peak_frontier = 1
        step_logs: List[StepLog] = []

        yield {"type": "init", "open": [start], "closed": [], "current": start}

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            steps += 1
            peak_frontier = max(peak_frontier, len(stack))

            log = StepLog(
                step_num=steps,
                current_node=current,
                action="expand",
                open_nodes=list(stack),
                closed_nodes=list(visited),
                parent_map=parent_map.copy()
            )
            step_logs.append(log)

            yield {
                "type": "step",
                "current": current,
                "open": list(stack),
                "closed": list(visited),
                "steps": steps,
            }

            if current == goal:
                elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
                path = reconstruct_path(parent_map, start, goal)
                path_cost = calculate_path_cost(grid, path)
                expanded_count = len(visited)
                density = expanded_count / total_walkable if total_walkable > 0 else 0.0

                result = SearchResult(
                    algorithm_name=self.name,
                    success=True,
                    path=path,
                    path_cost=path_cost,
                    step_count=steps,
                    expanded_nodes_count=expanded_count,
                    expanded_density=density,
                    runtime_ms=elapsed_ms,
                    peak_frontier=peak_frontier,
                    explored_nodes=visited,
                    step_logs=step_logs
                )
                yield {"type": "complete", "result": result, "path": path}
                return result

            for neighbor in grid.get_neighbors(current, allow_diagonal=allow_diagonal):
                if neighbor not in visited:
                    parent_map[neighbor] = current
                    stack.append(neighbor)

        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
        result = SearchResult(
            algorithm_name=self.name,
            success=False,
            path=[],
            path_cost=0.0,
            step_count=steps,
            expanded_nodes_count=len(visited),
            expanded_density=len(visited) / total_walkable if total_walkable > 0 else 0.0,
            runtime_ms=elapsed_ms,
            peak_frontier=peak_frontier,
            explored_nodes=visited,
            step_logs=step_logs
        )
        yield {"type": "complete", "result": result, "path": []}
        return result
