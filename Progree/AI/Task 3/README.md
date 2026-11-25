# ⚡ Heuristic Graph Pathfinding & RL Agent Search Engine

A desktop GUI application built with **Python**, **CustomTkinter**, and **Tkinter Canvas** for interactive visualization, heuristic optimization, reinforcement learning, and multi-agent benchmarking across complex grid mazes.

---

## 🌟 Key Features

### 1. 🤖 Graph Search & RL Algorithms (Coded from Scratch)
- **A\* Search**: Configurable with Manhattan ($L_1$), Euclidean ($L_2$), Chebyshev ($L_\infty$), and Octile distance heuristics, tie-breaking, and heuristic weighting ($\epsilon \ge 1.0$).
- **Dijkstra's Algorithm (Uniform Cost Search)**: Guaranteed optimal path on weighted terrain.
- **Bi-directional A\* Search**: Simultaneous two-way frontier expansion meeting at intersection.
- **Greedy Best-First Search (GBFS)**: High-speed heuristic-driven goal directed exploration.
- **Breadth-First Search (BFS) & Depth-First Search (DFS)**: Unweighted baseline comparisons.
- **Jump Point Search (JPS)**: Symmetry-pruning heuristic acceleration for uniform grids.
- **Tabular Q-Learning Agent (RL)**: Bellman optimality updates with potential-based heuristic reward shaping and interactive policy extraction.

### 2. 🎨 Rich Modern Cyberpunk / Dark UI & UX
- Modern dark mode styling (`#090d16`, `#0f172a`, `#1e293b`) with neon color palettes.
- Smooth step-by-step exploration animations with playback controls (Play, Pause, Step Next, Speed Slider 1x–100x, Instant Solve).
- Glowing optimal paths + Virtual agent token smoothly walking the final trajectory.
- Weighted terrain visualization (Mud $3\times$, Water $5\times$, Forest $2\times$).

### 3. 🎲 Procedural Maze & Terrain Generators
- **Recursive Backtracker** (Deep winding corridors)
- **Randomized Prim's** (Branching tree mazes)
- **Recursive Division** (Rooms & chambers)
- **Random Obstacle Arrays** (20%, 35%, 50% density)
- **Cellular Automata Caves** (Smooth organic cavern layouts)
- **Weighted Terrain Maps** (Natural Mud/Water/Forest clusters)

### 4. 📊 Real-Time Metrics HUD & Multi-Agent Benchmark Suite
- Real-time HUD tracking: Step count, Path length, Path total cost, Nodes expanded, Expanded Node Density %, Microsecond/millisecond execution time, Peak frontier size.
- **Benchmark Window**: Side-by-side performance evaluation of all 9 algorithms with embedded **Matplotlib charts** (Runtime, Expanded Nodes, Path Cost).

### 5. 💾 Telemetry Logging & Exporter
- **JSON Telemetry Log**: Full step-by-step exploration history with $f, g, h$ scores, parent mappings, and path coordinates.
- **CSV Summary**: Tabular performance metrics for spreadsheet analysis.
- **High-Resolution PNG Snapshot**: Render and export pixel-perfect map images.
- **Blueprint Save/Load**: Save custom maze layouts to JSON and load them at any time.

---

## 🚀 How to Run

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Launch the Application
```bash
python main.py
```

### Run Automated Tests
```bash
python test_suite.py
```

---

## 🎮 Controls & Interactions
- **Left Mouse Click / Drag**: Draw selected brush (Wall, Mud, Water, Forest).
- **Right Mouse Click / Drag**: Erase cells.
- **Drag Start Pin (S) / Goal Pin (G)**: Move start and target positions dynamically.
- **8-Way Diagonal Switch**: Toggle between 4-directional and 8-directional movement.
- **Heuristic Weight Slider**: Scale $w \in [1.0, 3.0]$ for weighted sub-optimal A* search.
