# 🧠 Artificial Intelligence Internship - Project Repository

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![PyTorch / Ultralytics](https://img.shields.io/badge/YOLO-Ultralytics-00ffff.svg?style=for-the-badge&logo=yolo&logoColor=black)
![NLP](https://img.shields.io/badge/NLP-NLTK%20%7C%20Scikit--Learn-orange.svg?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-CustomTkinter%20%26%20Tkinter-blueviolet.svg?style=for-the-badge)
![License](https://img.shields.io/badge/License-Academic%20Internship-success.svg?style=for-the-badge)

Welcome to the **Artificial Intelligence Internship & Laboratory Workspace**. This repository houses a comprehensive suite of practical AI projects spanning **Natural Language Processing (NLP)**, **Heuristic Search & Reinforcement Learning**, and **Real-Time Computer Vision / Object Detection**.

---

## 📑 Repository Structure & Overview

```text
├── Task 2/                              # NLP: Multi-Class Sentiment Classifier
│   ├── Tweets.csv                       # US Airline Sentiment Dataset
│   └── sentiment_classifier_task2.ipynb # Full end-to-end Jupyter Notebook pipeline
│
├── Task 3/                              # Search & RL: Heuristic Pathfinding Engine
│   ├── algorithms/                      # A*, Dijkstra, Bi-A*, GBFS, BFS, DFS, JPS, Q-Learning
│   ├── environment/                     # Grid world, maze generators, and terrain systems
│   ├── ui/                              # Cyberpunk Canvas GUI, controls, and benchmark dashboard
│   ├── main.py                          # Desktop Application Entrypoint
│   ├── test_suite.py                    # Automated test & benchmark validator
│   ├── requirements.txt                 # Dependencies for Task 3
│   └── README.md                        # Task 3 documentation
│
├── Task 4/                              # Computer Vision: YOLO Detection Studio
│   ├── images/                          # Sample test images (crowd, street, objects)
│   ├── app.py                           # Full-featured Tkinter/OpenCV Object Detection Studio
│   └── yolo26n.pt                       # Pre-trained YOLO weights
│
└── Artificial Intelligence Tasks & Instructions.pdf  # Formal internship task specifications
```

---

## 📂 Project Breakdowns

### 📝 Task 2: Multi-Class Sentiment Analysis Pipeline
> **Domain**: Natural Language Processing (NLP) & Statistical Machine Learning  
> **Location**: [`Task 2/`](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/AI/Task%202)

An end-to-end NLP workflow classifying unstructured social media statements into **positive**, **neutral**, or **negative** sentiment classes using the US Airline Sentiment dataset.

#### ✨ Features & Workflow:
- **Data Preprocessing**: Regex text cleaning (URLs, user mentions `@`, hashtags `#`, punctuation, emoji handling), tokenization, NLTK stop-word removal, and `WordNetLemmatizer` normalization.
- **Feature Engineering**: TF-IDF Vectorizer with unigram/bigram `ngram_range=(1,2)`, sublinear term frequency scaling, and document frequency filtering.
- **Model Comparison**:
  - **Multinomial Naïve Bayes** (Fast statistical baseline)
  - **Logistic Regression** (Multinomial / OvR with L2 regularization)
  - **Linear Support Vector Machine (LinearSVC)** (Calibrated probabilities via Platt scaling)
  - **Random Forest Classifier** (Ensemble tree learner)
- **Evaluation & Diagnostics**:
  - Precision, Recall, Macro/Weighted F1-score matrices.
  - Dual Confusion Matrices (Raw counts & normalized percentages).
  - Multi-class ROC curves with One-vs-Rest (OvR) Micro/Macro AUC scores.
  - Interactive prediction prompt for live, arbitrary sentence inference.

---

### ⚡ Task 3: Heuristic Graph Pathfinding & RL Agent Engine
> **Domain**: Classical AI, Heuristic Search & Reinforcement Learning  
> **Location**: [`Task 3/`](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/AI/Task%203)

A high-performance, modular desktop GUI application built with **CustomTkinter** and **Tkinter Canvas** for pathfinding visualization, heuristic experimentation, multi-agent benchmarking, and Reinforcement Learning.

#### ✨ Core Capabilities:
- **9 Graph Search & RL Algorithms** (Implemented from scratch):
  - **A\* Search**: Configurable with Manhattan ($L_1$), Euclidean ($L_2$), Chebyshev ($L_\infty$), and Octile heuristics, tie-breakers, and heuristic inflation weights ($\epsilon \ge 1.0$).
  - **Dijkstra's Algorithm**: Guaranteed optimal path on non-uniform weighted terrain.
  - **Bi-directional A\***: Simultaneous frontier expansions from start and goal.
  - **Greedy Best-First Search (GBFS)**: Ultra-fast greedy heuristic expansion.
  - **BFS & DFS**: Unweighted graph search baselines.
  - **Jump Point Search (JPS)**: Symmetry pruning heuristic optimization for uniform grids.
  - **Tabular Q-Learning (RL)**: Bellman optimality updates with potential-based heuristic reward shaping and policy extraction.
- **Procedural Maze & Environment Generators**:
  - Recursive Backtracker, Prim's Algorithm, Recursive Division, Cellular Automata Caves, Random Density Fields, and Clustered Weighted Terrain (Mud $3\times$, Water $5\times$, Forest $2\times$).
- **Multi-Agent Benchmark Suite**:
  - Side-by-side performance evaluation window with embedded **Matplotlib charts** (Runtime, Node Expansion %, Total Cost, Frontier Peak).
- **Telemetry & Exporter**:
  - Full step-by-step telemetry export to JSON, summary metrics to CSV, pixel-perfect PNG map snapshots, and map blueprint serialization.

---

### 👁️ Task 4: Real-Time YOLO Object Detection Studio
> **Domain**: Deep Learning, Computer Vision & Edge AI  
> **Location**: [`Task 4/`](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/AI/Task%204)

A desktop Computer Vision Studio with a dark UI built on **Tkinter**, **OpenCV**, and **Ultralytics YOLO** supporting multi-source inference, dynamic confidence/IoU filtering, class selection, analytics, and annotation export.

#### ✨ Key Features:
- **Multi-Source Inference Pipeline**:
  - **Images**: Batch image browsing, gallery navigation, and detection.
  - **Video Files**: MP4/AVI playback with real-time bounding box rendering and live FPS.
  - **Live Webcam**: Low-latency camera streaming and instant detection.
- **Interactive Control Deck**:
  - Real-time sliders for Confidence Threshold ($0.05 - 1.0$) and NMS IoU Threshold ($0.1 - 1.0$).
  - Interactive multi-class filter panel (Filter by Person, Car, Dog, etc., dynamically).
  - Toggles for Confidence Labels, Class Names, Centroid tracking points, and High-Contrast Color palettes.
- **Analytics & Telemetry**:
  - Live Detection HUD: Total object count, FPS counter, inference latency (ms), and class distribution pills.
- **Export & Serialization**:
  - Save annotated images with rendered bounding boxes.
  - Export structured bounding box detections to **JSON** and **CSV** (Class, Bounding Box coordinates $[x_1, y_1, x_2, y_2]$, and Confidence scores).

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Environment Setup (Recommended: Virtual Environment)
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows:
.\venv\Scripts\activate
# Activate on Linux/macOS:
source venv/bin/activate
```

### 3. Install Requirements
For the complete suite of tasks:
```bash
pip install numpy pandas scikit-learn nltk matplotlib seaborn opencv-python pillow ultralytics customtkinter
```

Or install specific task dependencies:
```bash
# For Task 3
cd "Task 3"
pip install -r requirements.txt
cd ..
```

---

## 🚀 Running the Projects

### Running Task 2 (NLP Sentiment Classifier)
Launch Jupyter Notebook or Jupyter Lab:
```bash
jupyter notebook "Task 2/sentiment_classifier_task2.ipynb"
```

### Running Task 3 (Heuristic Pathfinding & RL Engine)
```bash
cd "Task 3"
python main.py
```
*Run automated benchmark and algorithm tests:*
```bash
python test_suite.py
```

### Running Task 4 (YOLO Object Detection Studio)
```bash
cd "Task 4"
python app.py
```

---

## 📊 Summary of AI Concepts Demonstrated

| Concept | Implemented In | Key Technologies & Algorithms |
| :--- | :--- | :--- |
| **NLP & Text Mining** | Task 2 | TF-IDF, Lemmatization, Stopwords, Naïve Bayes, Logistic Regression, LinearSVC, Random Forest |
| **Model Evaluation** | Task 2, 3, 4 | Confusion Matrix, Macro/Micro ROC-AUC, Benchmark Plots, Latency/FPS Counters |
| **Heuristic Graph Search** | Task 3 | A\*, Dijkstra, Bi-directional A\*, GBFS, BFS, DFS, JPS, Multi-metric heuristics |
| **Reinforcement Learning** | Task 3 | Tabular Q-Learning, Epsilon-Greedy, Bellman Value Iteration, Reward Shaping |
| **Procedural Generation** | Task 3 | Prim's, Recursive Backtracker, Recursive Division, Cellular Automata |
| **Object Detection & CV** | Task 4 | YOLO (Ultralytics), OpenCV, Non-Maximum Suppression (NMS), Multi-threaded Video Processing |
| **UI/UX Engineering** | Task 3, 4 | CustomTkinter, Tkinter Canvas, Real-Time HUDs, Interactive Dashboards, Telemetry Export |

---

## 👨‍💻 Author & Acknowledgements
- **Author**: Internship Project
- Developed as part of the AI Engineering Internship curriculum.
