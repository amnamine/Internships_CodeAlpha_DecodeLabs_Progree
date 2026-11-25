# Generative AI & Autonomous Agents Hub

Welcome to the **Generative AI & Autonomous Agents Hub**! This repository contains a collection of four cutting-edge projects leveraging state-of-the-art Large Language Models (LLMs) and Image Generation APIs. These projects range from conversational web apps and multi-stage autonomous copywriters to AI-powered image generators and reasoning-budget-controlled code reviewers.

---

## 📂 Repository Structure

```directory
GenAI/
├── README.md                          # Main repository documentation
├── Generative AI Project 1.pdf        # Task 1 specification
├── Generative AI project 2.pdf        # Task 2 specification
├── Generative AI project 3.pdf        # Task 3 specification
├── Generative AI project 4.pdf        # Task 4 specification
├── Task 1/                            # Task 1 source directory
│   ├── app.py                         # Flask application entry point
│   ├── templates/                     # Flask HTML templates
│   └── static/                        # CSS, JS, and asset files
├── Task 2/                            # Task 2 source directory
│   └── app.py                         # CustomTkinter GUI application
├── Task 3/                            # Task 3 source directory
│   └── app.py                         # Cyberpunk-themed Tkinter app
└── Task 4/                            # Task 4 source directory
    └── app.py                         # Advanced Code Reviewer CustomTkinter app
```

---

## 🛠️ General Prerequisites & Setup

To run any of the projects, ensure you have Python 3.8+ installed on your system. 

### 1. Install Dependencies
Run the following command to install the required libraries globally or inside a virtual environment:
```bash
pip install flask groq customtkinter pillow requests pygments openai
```

---

## 🚀 Projects Overview

---

### 💬 Task 1: AI Chat Assistant Web App

A clean, responsive web interface built on Flask that interacts with the high-performance **Groq API**. It features custom system instructions, real-time conversation history maintenance, and flexible model selection.

#### ✨ Key Features
- **Flexible Models**: Choose between `Llama 3.3 70B Versatile` (for deep reasoning) and `Llama 3.1 8B Instant` (for speed).
- **System Prompt Customization**: Alter the system prompt on the fly to change the AI's persona and instructions.
- **Persistent In-Memory History**: Maintained via unique chat sessions (`chat_id`), ensuring the model retains full context during multi-turn interactions.
- **Robust Error Handling**: Handles API failures gracefully by preserving the history payload and popping un-responded prompts.

#### 🔧 Technology Stack
- **Backend**: Flask (Python)
- **API Client**: Groq SDK (Model: Llama 3)
- **Frontend**: HTML5, Vanilla CSS, and modern asynchronous JavaScript (`fetch`).

#### 🏃 How to Run
1. Navigate to the `Task 1` directory:
   ```bash
   cd "Task 1"
   ```
2. Run the Flask development server:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to `http://127.0.0.1:5000`.

---

### ✍️ Task 2: Automated Copywriting & Tone Transformer

An autonomous desktop agent built with **CustomTkinter** designed to produce high-impact marketing copy. This application implements a **Multi-Stage Agentic Loop** to critique, refine, and grade its own outputs.

#### ✨ Key Features
- **Dynamic Prompt Compilation**: Generates tailored prompts based on Product Name, Key Features, Platform (LinkedIn, Email, Instagram, etc.), and Tone.
- **Autonomous Multi-Stage Refinement (Agentic Loop)**:
  1. **Draft Generation**: Creates an initial copywriting proposal.
  2. **Critique Stage**: The agent behaves as a critical senior editor, evaluating the draft's length, buzzwords, and platform tone.
  3. **Refinement Stage**: Refines the copywriting to produce the final version based on the feedback.
- **In-Depth Quality Scorecard**: Computes numerical scores (out of 10) for Tone Match, Platform Compatibility, and Engagement, detailing actionable insights.
- **Hyperparameter Tuning**: Sliders to adjust inference `Temperature` and `Top P` variables.

#### 🔧 Technology Stack
- **GUI Engine**: CustomTkinter
- **API Client**: Groq SDK (Model: `llama-3.3-70b-versatile`)
- **Execution**: Python Threading (keeps the UI fully responsive during async inference).

#### 🏃 How to Run
1. Navigate to the `Task 2` directory:
   ```bash
   cd "Task 2"
   ```
2. Run the application:
   ```bash
   python app.py
   ```

---

### 🎨 Task 3: Pollinations.ai Image Generation Studio

A modern desktop application featuring a dark cyberpunk theme for producing artistic, high-definition images using the free, keyless **Pollinations.ai API**.

#### ✨ Key Features
- **Multiple Generative Engines**: Choose between cutting-edge models like `flux`, `grok-imagine`, `ideogram-v4-turbo`, `nanobanana`, and `nanobanana-pro`.
- **Aspect Ratio Formatting**: Built-in support for `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, and `21:9` ratios mapped to standard canvas sizes.
- **Batch Generation Control**: Generate a single image or up to a batch size of 4.
- **Interactive Carousel & Image Export**: Smoothly scroll through batch images in the preview box and save them to your computer as PNG/JPEG files.
- **Template Presets**: Quick-load predefined prompts like "Cyberpunk City," "Fantasy Forest," "3D Cartoon," or "Oil Painting."

#### 🔧 Technology Stack
- **GUI Engine**: Tkinter (stylized with custom background configurations, custom cards, and layout bindings)
- **API integration**: Asynchronous HTTP Requests to `image.pollinations.ai`
- **Image Processing**: Pillow (PIL)

#### 🏃 How to Run
1. Navigate to the `Task 3` directory:
   ```bash
   cd "Task 3"
   ```
2. Run the application:
   ```bash
   python app.py
   ```

---

### 🔍 Task 4: Intelligent Code Reviewer & Explainer Agent

A state-of-the-art desktop code analysis platform using the **NVIDIA NIM API** and the `nvidia/nemotron-3-super-120b-a12b` model. It features a live thinking logger, token budget control, and interactive chat.

#### ✨ Key Features
- **File Ingestion Editor**: Load local code files directly into a custom editor featuring sync-scrollable line numbers and real-time syntax highlighting.
- **NVIDIA reasoning_budget Control**: Control the reasoning budget (up to 16,384 tokens) allowing the NVIDIA model to run deep, structured mental checks before answering.
- **Live Streamed Output**:
  - **Thinking Log Tab**: Streams the model's internal step-by-step reasoning (`reasoning_content`) as it works.
  - **Analysis Report Tab**: Renders final markdown content dynamically with a custom markdown processor (supports headers, inline formatting, code blocks, and language syntax coloring).
- **Interactive Contextual Chat**: Chat with the agent directly. The agent retains full context of the loaded code block and answers follow-up questions in real-time.
- **4 Custom Analysis Pipelines**: 
  - *Full Review*: Detailed bug audits, explanations, and optimized code templates.
  - *Identify Bugs*: Bullet points of flaws and security risks.
  - *Plain Explanation*: Line-by-line algorithm descriptions.
  - *Code Optimization*: Algorithmic time/space optimizations.

#### 🔧 Technology Stack
- **GUI Engine**: CustomTkinter
- **API Client**: OpenAI SDK pointing to NVIDIA integrate endpoint (`https://integrate.api.nvidia.com/v1`)
- **Syntax Highlighter**: Pygments (for parsing editor inputs and markdown code blocks)

#### 🏃 How to Run
1. Navigate to the `Task 4` directory:
   ```bash
   cd "Task 4"
   ```
2. Run the application:
   ```bash
   python app.py
   ```

---

## 🌟 Features Breakdown Comparison

| Feature | Task 1 (Chat Web App) | Task 2 (Copywriter Agent) | Task 3 (Image Studio) | Task 4 (Code Reviewer) |
| :--- | :---: | :---: | :---: | :---: |
| **API Provider** | Groq | Groq | Pollinations.ai | NVIDIA NIM |
| **User Interface** | Web (Flask + JS) | GUI (CustomTkinter) | GUI (Tkinter Cyberpunk) | GUI (CustomTkinter) |
| **Primary Focus** | Conversations | Multi-stage copywriting | Image Generation | Code Analysis & Explanation |
| **Asynchronous Logic** | Yes (JS Fetch) | Yes (Python Threading) | Yes (Python Threading) | Yes (Python Threading + Queue) |
| **Key Highlights** | Dynamic System Prompt | Critique & Scorecards | Carousel Viewer & Seeds | Reasoning Budget & Live Thinking Log |
