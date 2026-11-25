"""
Automated Verification and Integrity Test Suite.
Tests algorithms, maze generators, and telemetry serialization.
"""

import os
import json
import time
from environment.grid import Grid, CellType
from environment.maze_generators import (
    generate_recursive_backtracker,
    generate_prims,
    generate_recursive_division,
    generate_random_obstacles,
    generate_cellular_automata,
    generate_weighted_terrain_map,
)
from algorithms.base import HeuristicType
from algorithms.astar import AStar
from algorithms.dijkstra import Dijkstra
from algorithms.greedy_best_first import GreedyBestFirstSearch
from algorithms.bfs_dfs import BreadthFirstSearch, DepthFirstSearch
from algorithms.bidirectional_astar import BidirectionalAStar
from algorithms.jump_point_search import JumpPointSearch
from algorithms.q_learning import QLearningAgent

def test_all():
    print("==================================================")
    print(" Running Pathfinding Search Engine Test Suite ")
    print("==================================================")

    # 1. Test Grid Model
    grid = Grid(rows=15, cols=20)
    assert grid.rows == 15 and grid.cols == 20
    assert grid.is_walkable(grid.start[0], grid.start[1])
    assert grid.is_walkable(grid.goal[0], grid.goal[1])
    print("[PASS] Grid model initialized properly.")

    # 2. Test Maze Generators
    for gen_fn in [
        generate_recursive_backtracker,
        generate_prims,
        generate_recursive_division,
        generate_random_obstacles,
        generate_cellular_automata,
        generate_weighted_terrain_map,
    ]:
        gen_fn(grid)
        assert grid.is_walkable(grid.start[0], grid.start[1])
        assert grid.is_walkable(grid.goal[0], grid.goal[1])
        print(f"[PASS] Maze generator {gen_fn.__name__} passed.")

    # 3. Test Search Algorithms on open grid
    grid.clear_all()
    # Add an obstacle wall with a passage
    for r in range(grid.rows):
        if r != 7:
            grid.set_cell(r, 10, CellType.WALL)

    algorithms = [
        AStar(HeuristicType.MANHATTAN),
        AStar(HeuristicType.EUCLIDEAN),
        Dijkstra(),
        BidirectionalAStar(HeuristicType.MANHATTAN),
        GreedyBestFirstSearch(HeuristicType.MANHATTAN),
        BreadthFirstSearch(),
        DepthFirstSearch(),
        JumpPointSearch(HeuristicType.OCTILE),
        QLearningAgent(episodes=150, max_steps_per_episode=150)
    ]

    for algo in algorithms:
        res = algo.search(grid, allow_diagonal=False)
        print(f"[ALGO TEST] {algo.name:32} | Success: {str(res.success):5} | Path Len: {len(res.path):2} | Cost: {res.path_cost:6.2f} | Exp Nodes: {res.expanded_nodes_count:3} | Time: {res.runtime_ms:.3f} ms")
        assert res.success, f"Algorithm {algo.name} failed to find path!"
        assert len(res.path) > 0, f"Path empty for {algo.name}!"

    # 4. Test Step Generators
    for algo in [AStar(HeuristicType.MANHATTAN), Dijkstra(), BreadthFirstSearch()]:
        gen = algo.step_generator(grid, allow_diagonal=False)
        step_count = 0
        final_res = None
        for step in gen:
            step_count += 1
            if step.get("type") == "complete":
                final_res = step.get("result")
                break
        assert final_res is not None and final_res.success
        print(f"[PASS] Step generator for {algo.name} yielded {step_count} frames.")

    # 5. Test JSON & Dict Serialization
    sample_res = algorithms[0].search(grid)
    json_data = json.dumps(sample_res.to_dict(), indent=2)
    assert len(json_data) > 100
    print("[PASS] SearchResult dictionary and JSON serialization passed.")

    print("==================================================")
    print(" ALL UNIT TESTS PASSED SUCCESSFULLY! ")
    print("==================================================")

if __name__ == "__main__":
    test_all()
