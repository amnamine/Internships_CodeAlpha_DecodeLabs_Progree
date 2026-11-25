"""
Bi-directional A* Search.
Conducts two simultaneous A* searches: one forward from start to goal, and one backward from goal to start.
Merges paths at the intersection node for accelerated search efficiency.
"""

import heapq
import time
from typing import List, Tuple, Dict, Any, Generator, Optional, Set
from .base import (
    BaseSearchAlgorithm, SearchResult, StepLog, HeuristicType,
    calculate_heuristic, calculate_path_cost
)

class BidirectionalAStar(BaseSearchAlgorithm):
    def __init__(self, heuristic_type: HeuristicType = HeuristicType.MANHATTAN):
        super().__init__(f"Bi-directional A* ({heuristic_type.value})")
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
                peak_frontier=2
            )

        # Forward search data structures
        forward_heap: List[Tuple[float, float, int, Tuple[int, int]]] = []
        forward_open: Set[Tuple[int, int]] = {start}
        forward_closed: Set[Tuple[int, int]] = set()
        forward_g: Dict[Tuple[int, int], float] = {start: 0.0}
        forward_parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        # Backward search data structures
        backward_heap: List[Tuple[float, float, int, Tuple[int, int]]] = []
        backward_open: Set[Tuple[int, int]] = {goal}
        backward_closed: Set[Tuple[int, int]] = set()
        backward_g: Dict[Tuple[int, int], float] = {goal: 0.0}
        backward_parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        tie_counter = 0
        h_fwd = calculate_heuristic(self.heuristic_type, start, goal)
        heapq.heappush(forward_heap, (h_fwd, h_fwd, tie_counter, start))

        tie_counter += 1
        h_bwd = calculate_heuristic(self.heuristic_type, goal, start)
        heapq.heappush(backward_heap, (h_bwd, h_bwd, tie_counter, goal))

        steps = 0
        peak_frontier = 2
        step_logs: List[StepLog] = []
        meeting_node = None

        while forward_heap and backward_heap:
            steps += 1
            peak_frontier = max(peak_frontier, len(forward_heap) + len(backward_heap))

            # Step Forward
            _, _, _, curr_fwd = heapq.heappop(forward_heap)
            if curr_fwd in forward_open:
                forward_open.remove(curr_fwd)
            forward_closed.add(curr_fwd)

            # Check if forward hit backward
            if curr_fwd in backward_closed or curr_fwd in backward_open:
                meeting_node = curr_fwd
                break

            for neighbor in grid.get_neighbors(curr_fwd, allow_diagonal=allow_diagonal):
                if neighbor in forward_closed:
                    continue
                tentative_g = forward_g[curr_fwd] + grid.get_move_cost(curr_fwd, neighbor)
                if tentative_g < forward_g.get(neighbor, float('inf')):
                    forward_parent[neighbor] = curr_fwd
                    forward_g[neighbor] = tentative_g
                    h_val = calculate_heuristic(self.heuristic_type, neighbor, goal)
                    f_val = tentative_g + h_val
                    tie_counter += 1
                    heapq.heappush(forward_heap, (f_val, h_val, tie_counter, neighbor))
                    forward_open.add(neighbor)

            # Step Backward
            _, _, _, curr_bwd = heapq.heappop(backward_heap)
            if curr_bwd in backward_open:
                backward_open.remove(curr_bwd)
            backward_closed.add(curr_bwd)

            # Check if backward hit forward
            if curr_bwd in forward_closed or curr_bwd in forward_open:
                meeting_node = curr_bwd
                break

            for neighbor in grid.get_neighbors(curr_bwd, allow_diagonal=allow_diagonal):
                if neighbor in backward_closed:
                    continue
                tentative_g = backward_g[curr_bwd] + grid.get_move_cost(curr_bwd, neighbor)
                if tentative_g < backward_g.get(neighbor, float('inf')):
                    backward_parent[neighbor] = curr_bwd
                    backward_g[neighbor] = tentative_g
                    h_val = calculate_heuristic(self.heuristic_type, neighbor, start)
                    f_val = tentative_g + h_val
                    tie_counter += 1
                    heapq.heappush(backward_heap, (f_val, h_val, tie_counter, neighbor))
                    backward_open.add(neighbor)

        all_closed = forward_closed.union(backward_closed)
        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6

        if meeting_node is not None:
            # Reconstruct forward path start -> meeting
            path_fwd = []
            curr = meeting_node
            while curr in forward_parent:
                path_fwd.append(curr)
                curr = forward_parent[curr]
            path_fwd.append(start)
            path_fwd.reverse()

            # Reconstruct backward path meeting -> goal
            path_bwd = []
            curr = meeting_node
            while curr in backward_parent:
                curr = backward_parent[curr]
                path_bwd.append(curr)

            full_path = path_fwd + path_bwd
            path_cost = calculate_path_cost(grid, full_path)
            expanded_count = len(all_closed)
            density = expanded_count / total_walkable if total_walkable > 0 else 0.0

            return SearchResult(
                algorithm_name=self.name,
                success=True,
                path=full_path,
                path_cost=path_cost,
                step_count=steps,
                expanded_nodes_count=expanded_count,
                expanded_density=density,
                runtime_ms=elapsed_ms,
                peak_frontier=peak_frontier,
                explored_nodes=all_closed,
                metadata={"meeting_node": list(meeting_node)}
            )

        return SearchResult(
            algorithm_name=self.name,
            success=False,
            path=[],
            path_cost=0.0,
            step_count=steps,
            expanded_nodes_count=len(all_closed),
            expanded_density=len(all_closed) / total_walkable if total_walkable > 0 else 0.0,
            runtime_ms=elapsed_ms,
            peak_frontier=peak_frontier,
            explored_nodes=all_closed
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
                peak_frontier=2
            )
            yield {"type": "complete", "result": res}
            return res

        forward_heap: List[Tuple[float, float, int, Tuple[int, int]]] = []
        forward_open: Set[Tuple[int, int]] = {start}
        forward_closed: Set[Tuple[int, int]] = set()
        forward_g: Dict[Tuple[int, int], float] = {start: 0.0}
        forward_parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        backward_heap: List[Tuple[float, float, int, Tuple[int, int]]] = []
        backward_open: Set[Tuple[int, int]] = {goal}
        backward_closed: Set[Tuple[int, int]] = set()
        backward_g: Dict[Tuple[int, int], float] = {goal: 0.0}
        backward_parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        tie_counter = 0
        h_fwd = calculate_heuristic(self.heuristic_type, start, goal)
        heapq.heappush(forward_heap, (h_fwd, h_fwd, tie_counter, start))

        tie_counter += 1
        h_bwd = calculate_heuristic(self.heuristic_type, goal, start)
        heapq.heappush(backward_heap, (h_bwd, h_bwd, tie_counter, goal))

        steps = 0
        peak_frontier = 2
        meeting_node = None

        yield {
            "type": "init",
            "open": list(forward_open.union(backward_open)),
            "closed": [],
            "current": start
        }

        while forward_heap and backward_heap:
            steps += 1
            peak_frontier = max(peak_frontier, len(forward_heap) + len(backward_heap))

            # Forward Pop
            _, _, _, curr_fwd = heapq.heappop(forward_heap)
            if curr_fwd in forward_open:
                forward_open.remove(curr_fwd)
            forward_closed.add(curr_fwd)

            yield {
                "type": "step",
                "current": curr_fwd,
                "open": list(forward_open.union(backward_open)),
                "closed": list(forward_closed.union(backward_closed)),
                "steps": steps
            }

            if curr_fwd in backward_closed or curr_fwd in backward_open:
                meeting_node = curr_fwd
                break

            for neighbor in grid.get_neighbors(curr_fwd, allow_diagonal=allow_diagonal):
                if neighbor in forward_closed:
                    continue
                tentative_g = forward_g[curr_fwd] + grid.get_move_cost(curr_fwd, neighbor)
                if tentative_g < forward_g.get(neighbor, float('inf')):
                    forward_parent[neighbor] = curr_fwd
                    forward_g[neighbor] = tentative_g
                    h_val = calculate_heuristic(self.heuristic_type, neighbor, goal)
                    f_val = tentative_g + h_val
                    tie_counter += 1
                    heapq.heappush(forward_heap, (f_val, h_val, tie_counter, neighbor))
                    forward_open.add(neighbor)

            # Backward Pop
            _, _, _, curr_bwd = heapq.heappop(backward_heap)
            if curr_bwd in backward_open:
                backward_open.remove(curr_bwd)
            backward_closed.add(curr_bwd)

            yield {
                "type": "step",
                "current": curr_bwd,
                "open": list(forward_open.union(backward_open)),
                "closed": list(forward_closed.union(backward_closed)),
                "steps": steps
            }

            if curr_bwd in forward_closed or curr_bwd in forward_open:
                meeting_node = curr_bwd
                break

            for neighbor in grid.get_neighbors(curr_bwd, allow_diagonal=allow_diagonal):
                if neighbor in backward_closed:
                    continue
                tentative_g = backward_g[curr_bwd] + grid.get_move_cost(curr_bwd, neighbor)
                if tentative_g < backward_g.get(neighbor, float('inf')):
                    backward_parent[neighbor] = curr_bwd
                    backward_g[neighbor] = tentative_g
                    h_val = calculate_heuristic(self.heuristic_type, neighbor, start)
                    f_val = tentative_g + h_val
                    tie_counter += 1
                    heapq.heappush(backward_heap, (f_val, h_val, tie_counter, neighbor))
                    backward_open.add(neighbor)

        all_closed = forward_closed.union(backward_closed)
        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6

        if meeting_node is not None:
            path_fwd = []
            curr = meeting_node
            while curr in forward_parent:
                path_fwd.append(curr)
                curr = forward_parent[curr]
            path_fwd.append(start)
            path_fwd.reverse()

            path_bwd = []
            curr = meeting_node
            while curr in backward_parent:
                curr = backward_parent[curr]
                path_bwd.append(curr)

            full_path = path_fwd + path_bwd
            path_cost = calculate_path_cost(grid, full_path)
            expanded_count = len(all_closed)
            density = expanded_count / total_walkable if total_walkable > 0 else 0.0

            result = SearchResult(
                algorithm_name=self.name,
                success=True,
                path=full_path,
                path_cost=path_cost,
                step_count=steps,
                expanded_nodes_count=expanded_count,
                expanded_density=density,
                runtime_ms=elapsed_ms,
                peak_frontier=peak_frontier,
                explored_nodes=all_closed,
                metadata={"meeting_node": list(meeting_node)}
            )
            yield {"type": "complete", "result": result, "path": full_path}
            return result

        result = SearchResult(
            algorithm_name=self.name,
            success=False,
            path=[],
            path_cost=0.0,
            step_count=steps,
            expanded_nodes_count=len(all_closed),
            expanded_density=len(all_closed) / total_walkable if total_walkable > 0 else 0.0,
            runtime_ms=elapsed_ms,
            peak_frontier=peak_frontier,
            explored_nodes=all_closed
        )
        yield {"type": "complete", "result": result, "path": []}
        return result
