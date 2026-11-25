"""
Base architecture for Graph Pathfinding and Search Algorithms.
Includes Heuristic calculators, SearchResult container, and StepLog tracking.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple, Dict, Any, Optional, Generator, Callable, Set
import math
import time
from dataclasses import dataclass, field

class HeuristicType(str, Enum):
    MANHATTAN = "Manhattan (L1)"
    EUCLIDEAN = "Euclidean (L2)"
    CHEBYSHEV = "Chebyshev (Linf)"
    OCTILE = "Octile (Diagonal)"

def calculate_heuristic(h_type: HeuristicType, a: Tuple[int, int], b: Tuple[int, int], weight: float = 1.0) -> float:
    """Computes heuristic distance between two 2D points (r1, c1) and (r2, c2)."""
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])

    if h_type == HeuristicType.MANHATTAN:
        val = dr + dc
    elif h_type == HeuristicType.EUCLIDEAN:
        val = math.sqrt(dr * dr + dc * dc)
    elif h_type == HeuristicType.CHEBYSHEV:
        val = max(dr, dc)
    elif h_type == HeuristicType.OCTILE:
        # Octile: orthogonal step is 1, diagonal step is sqrt(2)
        val = (dr + dc) + (math.sqrt(2) - 2.0) * min(dr, dc)
    else:
        val = dr + dc

    return val * weight

@dataclass
class StepLog:
    """Represents the search state snapshot at a single iteration."""
    step_num: int
    current_node: Tuple[int, int]
    action: str  # 'expand', 'open_neighbor', 'close_node', 'path_found', 'q_update'
    open_nodes: List[Tuple[int, int]] = field(default_factory=list)
    closed_nodes: List[Tuple[int, int]] = field(default_factory=list)
    f_scores: Dict[Tuple[int, int], float] = field(default_factory=dict)
    g_scores: Dict[Tuple[int, int], float] = field(default_factory=dict)
    h_scores: Dict[Tuple[int, int], float] = field(default_factory=dict)
    parent_map: Dict[Tuple[int, int], Tuple[int, int]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_num": self.step_num,
            "current_node": list(self.current_node) if self.current_node else None,
            "action": self.action,
            "open_count": len(self.open_nodes),
            "closed_count": len(self.closed_nodes),
            "g_score": self.g_scores.get(self.current_node, 0.0) if self.current_node else 0.0,
            "h_score": self.h_scores.get(self.current_node, 0.0) if self.current_node else 0.0,
            "f_score": self.f_scores.get(self.current_node, 0.0) if self.current_node else 0.0,
        }

@dataclass
class SearchResult:
    """Encapsulates all outcome metrics and playback step history."""
    algorithm_name: str
    success: bool
    path: List[Tuple[int, int]] = field(default_factory=list)
    path_cost: float = 0.0
    step_count: int = 0
    expanded_nodes_count: int = 0
    expanded_density: float = 0.0  # percentage of total walkable cells
    runtime_ms: float = 0.0        # milliseconds
    peak_frontier: int = 0
    explored_nodes: Set[Tuple[int, int]] = field(default_factory=set)
    step_logs: List[StepLog] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_name": self.algorithm_name,
            "success": self.success,
            "path_length": len(self.path),
            "path_cost": round(self.path_cost, 4),
            "step_count": self.step_count,
            "expanded_nodes_count": self.expanded_nodes_count,
            "expanded_density_percent": round(self.expanded_density * 100, 2),
            "runtime_ms": round(self.runtime_ms, 4),
            "peak_frontier": self.peak_frontier,
            "path_coordinates": [list(node) for node in self.path],
            "metadata": self.metadata,
            "total_logged_steps": len(self.step_logs)
        }

class BaseSearchAlgorithm(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def search(self, grid: Any, allow_diagonal: bool = False, **kwargs) -> SearchResult:
        """Executes full search and returns the SearchResult."""
        pass

    @abstractmethod
    def step_generator(self, grid: Any, allow_diagonal: bool = False, **kwargs) -> Generator[Dict[str, Any], None, SearchResult]:
        """Yields frame-by-frame dictionaries for animated visualization, finally returning SearchResult."""
        pass

def reconstruct_path(parent_map: Dict[Tuple[int, int], Tuple[int, int]], start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Backtracks from goal to start using parent pointers."""
    if goal not in parent_map and goal != start:
        return []
    path = [goal]
    curr = goal
    while curr in parent_map and curr != start:
        curr = parent_map[curr]
        path.append(curr)
    if curr != start and start != goal:
        return []
    path.reverse()
    return path

def calculate_path_cost(grid: Any, path: List[Tuple[int, int]]) -> float:
    """Calculates cumulative movement cost of a path across weighted grid cells."""
    if not path or len(path) <= 1:
        return 0.0
    cost = 0.0
    for i in range(len(path) - 1):
        cost += grid.get_move_cost(path[i], path[i + 1])
    return cost
