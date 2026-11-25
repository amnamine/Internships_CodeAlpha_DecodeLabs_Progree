# CodeAlpha Python Programming Internship Projects

Welcome to the **CodeAlpha Python Programming Internship** repository. This repository contains a collection of professional-grade, feature-rich Python applications built to fulfill and exceed the requirements of the CodeAlpha Python Programming internship (Module 1).

Instead of basic terminal-based scripts, each task has been elevated into a **highly polished, GUI-driven application** featuring modern dark-theme aesthetics, responsive layouts, robust error handling, and advanced features.

---

## 📂 Repository Structure

The workspace is organized into four main task folders and includes the official task instructions:

```text
📁 CodeAlpha_INTERNSHIP/Python/
│
├── 📄 Python Programming Tasks & Instructions — CodeAlpha M1.pdf  # Official internship instructions
│
├── 📁 Task 1/                                                     # Hangman Game
│   └── 📄 hangman.py                                              # Pygame implementation with retro synth audio
│
├── 📁 Task 2/                                                     # Stock Portfolio Tracker
│   ├── 📄 portfolio_tracker.py                                    # Tkinter UI tracker with canvas charts
│   └── 📄 verify_tracker.py                                       # Utility script to test data loading
│
├── 📁 Task 3/                                                     # Task Automation Suite
│   ├── 📄 task_automator.py                                       # Tkinter Automation Suite (organizer, regex extractor, scraper)
│   └── 📁 demo_sandbox/                                           # Sandbox folder for testing automations
│
└── 📁 Task 4/                                                     # Advanced Pseudo-LLM Chatbot
    ├── 📄 chatbot_app.py                                          # Tkinter Chatbot GUI with quick command presets
    └── 📄 rule_engine.py                                          # State-based parsing engine with hundreds of rules
```

---

## 🛠️ Installation & Setup

### Prerequisites
Make sure you have Python 3.10+ installed.

### Dependencies
The projects utilize a few third-party libraries for audio synthesis, web scraping, and graphical layouts. Install them using `pip`:

```bash
pip install pygame requests beautifulsoup4
```

---

## 🕹️ Project Deep-Dives

### 🎮 Task 1: Elegant Pygame Hangman Game
* **Location**: [Task 1/hangman.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Python/Task%201/hangman.py)
* **Goal**: Create a word guessing game where players try to identify a hidden word one letter at a time.
* **Basic vs. Advanced Implementation**:
  | Feature | Basic Requirement (PDF) | Advanced Implementation |
  | :--- | :--- | :--- |
  | **UI/UX** | Console input/output (text-based) | Beautiful, responsive 1024x768 Pygame window with neon-slate themes and micro-animations |
  | **Audio** | No audio | Procedural retro synthesizer generating real-time sine/square wave sound effects |
  | **Word Base** | 5 predefined words | Broad multi-category word base (Technology, Animals, Countries, Food) |
  | **Visuals** | Basic text lines | Interactive keyboard, animated hangman stand/rope, smooth transitions, and win/lose screens |

#### How to Run
```bash
python "Task 1/hangman.py"
```

---

### 📈 Task 2: Stock Portfolio Tracker
* **Location**: [Task 2/portfolio_tracker.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Python/Task%202/portfolio_tracker.py)
* **Goal**: Track stock investments, input shares, and calculate portfolio value.
* **Basic vs. Advanced Implementation**:
  | Feature | Basic Requirement (PDF) | Advanced Implementation |
  | :--- | :--- | :--- |
  | **Interface** | Console prompt or simple script | Polished dark mode Tkinter application with custom Segoe UI typography |
  | **Data Management** | Hardcoded values | Add, edit, and delete real-time stock holdings; import and export portfolios from/to CSV files |
  | **Visual Charts** | Optional text output | Custom-drawn Tkinter Canvas pie chart representing portfolio distribution and percentage weight |
  | **Metrics** | Basic total value | Real-time calculations of total investment, portfolio change, and detailed tabular grid views |

#### How to Run
```bash
python "Task 2/portfolio_tracker.py"
```

---

### ⚡ Task 3: NovaAutomate - Task Automation Suite
* **Location**: [Task 3/task_automator.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Python/Task%203/task_automator.py)
* **Goal**: Automate a simple, repetitive daily task.
* **Basic vs. Advanced Implementation**:
  Instead of building just one automated script, **NovaAutomate** bundles **all three** proposed automation paths into a single interface:
  1. **File Organizer**: Scans any directory and automatically organizes files into subfolders (e.g., Documents, Images, Audio, Video, Code, Archives) based on their file extensions.
  2. **Pattern Extractor**: Uses advanced regex to scan text files for email addresses, phone numbers, and URLs, saving the results to a clean output text file.
  3. **Web Info Scraper**: Downloads web pages asynchronously, extracting titles, meta descriptions, and header tags (`<h1>`-`<h3>`), exporting them into structured reports.

  *Featuring canvas-rendered animated buttons, custom path pickers, asynchronous background worker threads, and live activity logging.*

#### How to Run
```bash
python "Task 3/task_automator.py"
```

---

### 🧠 Task 4: Antigravity - Advanced Pseudo-LLM Chatbot
* **Location**: [Task 4/chatbot_app.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Python/Task%204/chatbot_app.py) & [Task 4/rule_engine.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Python/Task%204/rule_engine.py)
* **Goal**: Build a simple rule-based conversational agent responding to core greetings.
* **Basic vs. Advanced Implementation**:
  | Feature | Basic Requirement (PDF) | Advanced Implementation |
  | :--- | :--- | :--- |
  | **Conversation** | basic responses (`hello`, `bye`) | Deep rule-based parser mimicking an actual AI model (hundreds of patterns and semantic branches) |
  | **State & Memory** | Stateless execution | Persistent state memory (stores user name, tracking history, and context switches) |
  | **Interface** | CLI prompts | Immersive futuristic GUI with bubble chats, blinking engine-online lights, and sidebar quick presets |
  | **Interactive Features** | None | Built-in text adventure game, riddles, math solvers, custom python snippet generator, and F11 Fullscreen mode |

#### How to Run
```bash
python "Task 4/chatbot_app.py"
```

---

## 🌟 Key Engineering Practices Used

* **Multithreading**: Prevents UI freezes in Tkinter during longer running background operations (e.g. web scraping, file organization).
* **Stateful Architectures**: Retaining states and variables inside the Rule Engine to simulate natural conversational flow.
* **Procedural Synthesis**: Using Python's `array` and Pygame's `mixer` to synthesize audio waveforms dynamically without relying on external `.wav` or `.mp3` files.
* **Custom UI widgets**: Overriding basic Tkinter layouts with customized canvas-drawn components, hover effects, and modern color palettes.
* **Clean Code & Error Handling**: Extensive `try-except` blocks, validation logic, and descriptive naming conventions.
