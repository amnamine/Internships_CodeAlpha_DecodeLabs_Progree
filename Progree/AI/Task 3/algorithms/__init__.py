from .base import (
    BaseSearchAlgorithm,
    SearchResult,
    StepLog,
    HeuristicType,
    calculate_heuristic,
    reconstruct_path,
    calculate_path_cost,
)
from .astar import AStar
from .dijkstra import Dijkstra
from .greedy_best_first import GreedyBestFirstSearch
from .bfs_dfs import BreadthFirstSearch, DepthFirstSearch
from .bidirectional_astar import BidirectionalAStar
from .jump_point_search import JumpPointSearch
from .q_learning import QLearningAgent

ALGORITHMS_REGISTRY = {
    "A* Search": AStar,
    "Dijkstra's Algorithm": Dijkstra,
    "Greedy Best-First": GreedyBestFirstSearch,
    "Breadth-First Search (BFS)": BreadthFirstSearch,
    "Depth-First Search (DFS)": DepthFirstSearch,
    "Bi-directional A*": BidirectionalAStar,
    "Jump Point Search (JPS)": JumpPointSearch,
    "Q-Learning Agent (RL)": QLearningAgent,
}
