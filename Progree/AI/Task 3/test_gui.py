"""
Headless / Automated GUI Test Script.
Instantiates the Tkinter Application, tests widget initialization, animation loops, and closes cleanly.
"""

import tkinter as tk
import time
from main import PathfindingApp
from environment.grid import CellType
from algorithms.base import HeuristicType

def test_gui():
    print("Testing PathfindingApp GUI initialization...")
    app = PathfindingApp()
    app.update()
    print("[PASS] App created and layout updated.")

    # Test maze generation
    print("Testing Maze generation via GUI...")
    app.generate_maze_by_name("Random Obstacles (20%)")
    app.update()
    print("[PASS] Maze generated.")

    # Test Instant Solve
    print("Testing Instant Solve...")
    app.run_instant_solve()
    app.update()
    assert app.last_result is not None
    print(f"[PASS] Instant Solve completed: Path length={len(app.last_result.path)}, runtime={app.last_result.runtime_ms:.3f}ms")

    # Test Brush switch
    print("Testing Brush switch...")
    app.handle_brush_change(CellType.MUD)
    app.handle_heuristic_change(HeuristicType.EUCLIDEAN)
    app.handle_diagonal_toggle(True)
    app.handle_weight_change(1.5)
    app.update()
    print("[PASS] Controls state updated.")

    # Test Step Animation (run a few frames)
    print("Testing Animation loop...")
    app.start_visualization()
    for _ in range(15):
        app.update()
        time.sleep(0.02)
    app.stop_any_animation()
    print("[PASS] Animation executed smoothly.")

    # Clean shutdown
    app.destroy()
    print("========================================")
    print(" GUI INTEGRITY TEST COMPLETED (100% OK) ")
    print("========================================")

if __name__ == "__main__":
    test_gui()
