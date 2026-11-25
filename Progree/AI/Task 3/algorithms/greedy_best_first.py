"""
Greedy Best-First Search (GBFS).
Expands nodes with lowest estimated heuristic distance h(n) to goal.
Fastest exploration, but does not guarantee shortest path cost.
"""

import heapq
import time
from typing import List, Tuple, Dict, Any, Generator, Optional, Set
from .base import (
    BaseSearchAlgorithm, SearchResult, StepLog, HeuristicType,
    calculate_heuristic, reconstruct_path, calculate_path_cost
)

class GreedyBestFirstSearch(BaseSearchAlgorithm):
    def __init__(self, heuristic_type: HeuristicType = HeuristicType.MANHATTAN):
        super().__init__(f"Greedy Best-First ({heuristic_type.value})")
        self.heuristic_type = heuristic_type

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

        tie_counter = 0
        open_heap: List[Tuple[float, int, Tuple[int, int]]] = []
        open_set: Set[Tuple[int, int]] = {start}
        closed_set: Set[Tuple[int, int]] = set()

        h_start = calculate_heuristic(self.heuristic_type, start, goal)
        parent_map: Dict[Tuple[int, int], Tuple[int, int]] = {}

        heapq.heappush(open_heap, (h_start, tie_counter, start))
        peak_frontier = 1
        steps = 0
        step_logs: List[StepLog] = []

        while open_heap:
            current_h, _, current = heapq.heappop(open_heap)
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
                action="expand",
                open_nodes=list(open_set),
                closed_nodes=list(closed_set),
                h_scores={current: current_h},
                f_scores={current: current_h},
                parent_map=parent_map.copy()
            ))

            if current == goal:
                elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
                path = reconstruct_path(parent_map, start, goal)
                path_cost = calculate_path_cost(grid, path)
                expanded_count = len(closed_set)
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
                    explored_nodes=closed_set,
                    step_logs=step_logs,
                    metadata={"heuristic": self.heuristic_type.value}
                )

            for neighbor in grid.get_neighbors(current, allow_diagonal=allow_diagonal):
                if neighbor in closed_set or neighbor in open_set:
                    continue

                parent_map[neighbor] = current
                h_val = calculate_heuristic(self.heuristic_type, neighbor, goal)
                tie_counter += 1
                heapq.heappush(open_heap, (h_val, tie_counter, neighbor))
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
            step_logs=step_logs,
            metadata={"heuristic": self.heuristic_type.value}
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

        tie_counter = 0
        open_heap: List[Tuple[float, int, Tuple[int, int]]] = []
        open_set: Set[Tuple[int, int]] = {start}
        closed_set: Set[Tuple[int, int]] = set()

        h_start = calculate_heuristic(self.heuristic_type, start, goal)
        parent_map: Dict[Tuple[int, int], Tuple[int, int]] = {}

        heapq.heappush(open_heap, (h_start, tie_counter, start))
        peak_frontier = 1
        steps = 0
        step_logs: List[StepLog] = []

        yield {
            "type": "init",
            "open": list(open_set),
            "closed": list(closed_set),
            "current": start,
            "f_score": h_start,
            "g_score": 0,
            "h_score": h_start
        }

        while open_heap:
            current_h, _, current = heapq.heappop(open_heap)
            if current in open_set:
                open_set.remove(current)

            if current in closed_set:
                continue

            closed_set.add(current)
            steps += 1
            peak_frontier = max(peak_frontier, len(open_heap))

            log = StepLog(
                step_num=steps,
                current_node=current,
                action="expand",
                open_nodes=list(open_set),
                closed_nodes=list(closed_set),
                h_scores={current: current_h},
                f_scores={current: current_h},
                parent_map=parent_map.copy()
            )
            step_logs.append(log)

            yield {
                "type": "step",
                "current": current,
                "open": list(open_set),
                "closed": list(closed_set),
                "steps": steps,
                "f_score": current_h,
                "g_score": 0,
                "h_score": current_h,
            }

            if current == goal:
                elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
                path = reconstruct_path(parent_map, start, goal)
                path_cost = calculate_path_cost(grid, path)
                expanded_count = len(closed_set)
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
                    explored_nodes=closed_set,
                    step_logs=step_logs,
                    metadata={"heuristic": self.heuristic_type.value}
                )
                yield {"type": "complete", "result": result, "path": path}
                return result

            for neighbor in grid.get_neighbors(current, allow_diagonal=allow_diagonal):
                if neighbor in closed_set or neighbor in open_set:
                    continue

                parent_map[neighbor] = current
                h_val = calculate_heuristic(self.heuristic_type, neighbor, goal)
                tie_counter += 1
                heapq.heappush(open_heap, (h_val, tie_counter, neighbor))
                open_set.add(neighbor)

        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6
        result = SearchResult(
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
            step_logs=step_logs,
            metadata={"heuristic": self.heuristic_type.value}
        )
        yield {"type": "complete", "result": result, "path": []}
        return result
