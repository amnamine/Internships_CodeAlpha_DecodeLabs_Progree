# Advanced Prompt Engineering & Guardrail AI Suite

An enterprise-grade, interactive Python suite showcasing **Advanced Prompt Engineering Methodologies**, **Structured Data Extraction**, **Chain-of-Thought (CoT) Logic Engines**, **Context-Anchored RAG Systems**, and **Multi-Layer System Persona & Input/Output Guardrails**.

Powered by the **Groq API** with ultra-fast inference utilizing **Meta Llama 3.3 70B Versatile** and built with modern **CustomTkinter** / **Tkinter** GUIs.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Repository Architecture & Task Summary](#repository-architecture--task-summary)
- [Detailed Project Breakdown](#detailed-project-breakdown)
  - [Project 1: Structured Information Extraction Engine (Zero-Shot & Few-Shot)](#project-1-structured-information-extraction-engine-zero-shot--few-shot)
  - [Project 2: Chain-of-Thought (CoT) Logic Engine & Trap Verification](#project-2-chain-of-thought-cot-logic-engine--trap-verification)
  - [Project 3: Context-Anchored Closed-Book RAG Chatbot](#project-3-context-anchored-closed-book-rag-chatbot)
  - [Project 4: System Persona Architecture & Multi-Layer Guardrail Bot](#project-4-system-persona-architecture--multi-layer-guardrail-bot)
- [Key Engineering Concepts & Methodologies](#key-engineering-concepts--methodologies)
- [Installation & Setup Guide](#installation--setup-guide)
- [Usage Guide](#usage-guide)
- [Technologies & Dependencies](#technologies--dependencies)

---

## 🌐 Overview

This repository represents a comprehensive portfolio of practical Prompt Engineering and AI Safety projects developed during the DecodeLabs Internship. It bridges the gap between raw LLM capabilities and robust software applications by implementing production-ready patterns:

1. **Deterministic Structured Outputs**: Enforcing zero-shot and few-shot JSON compliance with auto-validation.
2. **Step-by-Step Reasoning**: Utilizing Chain-of-Thought prompts and automated logic verification to bypass LLM cognitive traps and hallucinations.
3. **Grounding & RAG Systems**: Implementing context-anchored closed-book answering with exact paragraph citations and TF-IDF / FAISS semantic vector search.
4. **Safety & Deflection Guardrails**: Designing multi-layered defense architecture (pre-filtering, post-filtering, red teaming, real-time security audit logging, and persona locking).

---

## 📁 Repository Architecture & Task Summary

The repository is structured into 4 main task directories alongside theoretical documentation project PDFs:

```text
DECODELABSINTERNSHIP/Prompts/
├── Prompt Engineering Project 1.pdf   # Theoretical & conceptual manual for Task 1
├── Prompt Engineering Project 2 .pdf  # Theoretical & conceptual manual for Task 2
├── Prompt Engineering Project 3.pdf   # Theoretical & conceptual manual for Task 3
├── Prompt Engineering Project 4.pdf   # Theoretical & conceptual manual for Task 4
├── Task 1/
│   └── app.py                        # GUI & Logic: Zero-Shot / Few-Shot Extraction Engine
├── Task 2/
│   └── app.py                        # GUI & Logic: Chain-of-Thought Logic Engine
├── Task 3/
│   ├── app.py                        # GUI & Logic: RAG Engine with FAISS & TF-IDF Vector Search
│   ├── precache.py                   # Pre-computes FAISS embeddings & caches local indexes
│   └── rag_cache/                    # Local cache directory for FAISS vector index & pickles
└── Task 4/
    ├── app.py                        # CustomTkinter GUI: Guardrail & Persona Management Dashboard
    ├── guardrail_engine.py           # Core Security Engine: Pre/Post Guardrails & Red Teaming
    └── test_app.py                   # Unit test suite for Guardrail Engine verification
```

---

## 🔬 Detailed Project Breakdown

### Project 1: Structured Information Extraction Engine (Zero-Shot & Few-Shot)
* **Directory**: [`Task 1/`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%201)
* **Main Script**: [`Task 1/app.py`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%201/app.py)

#### Core Purpose & Features
Translates unstructured raw text (medical notes, e-commerce orders, legal notices, resume data) into strictly typed, schema-compliant JSON structures.
* **Extraction Modes**: Supports **Zero-Shot** (relying on clear schema directives) and **Few-Shot** (incorporating past input/output examples to maximize extraction accuracy).
* **Automated JSON Validation**: Intercepts LLM outputs, cleans markdown code blocks, validates JSON syntax, and reports structural compliance or parsing errors.
* **Preloaded Datasets**: Features built-in sample presets (Medical Consultation Notes, E-Commerce Receipts, Legal Summaries).

---

### Project 2: Chain-of-Thought (CoT) Logic Engine & Trap Verification
* **Directory**: [`Task 2/`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%202)
* **Main Script**: [`Task 2/app.py`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%202/app.py)

#### Core Purpose & Features
Forces the LLM to perform explicit, multi-step logical reasoning before producing a final answer, eliminating intuitive cognitive biases.
* **Preloaded Logic Traps Library**: Contains iconic logic puzzles that trip up standard LLMs (e.g., *Bat & Ball Intuition Trap*, *Lily Pad Exponential Growth*, *The Monty Hall Paradox*, *River Crossing*, *3 Light Bulbs*, *Knights & Knaves*).
* **Automated Step Verification**: Evaluates generated reasoning against expected intermediate steps and sanity checks (e.g., verifying $0.05 ball price instead of $0.10 intuition).
* **Comparative View**: Side-by-side execution comparison between **Direct Prompting** (prone to instant hallucination/errors) and **Chain-of-Thought Prompting** (structured step-by-step resolution).

---

### Project 3: Context-Anchored Closed-Book RAG Chatbot
* **Directory**: [`Task 3/`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%203)
* **Scripts**: [`Task 3/app.py`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%203/app.py), [`Task 3/precache.py`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%203/precache.py)

#### Core Purpose & Features
Guarantees absolute factual grounding by restricting the LLM exclusively to retrieved context documents.
* **Dual Retrieval Engine**:
  * **TF-IDF Vector Space Model**: Lightweight keyword/frequency retrieval.
  * **FAISS + SentenceTransformers**: High-performance semantic dense vector search (`all-MiniLM-L6-v2` embeddings).
* **Strict Negative Constraints**: If the requested answer is not present in the provided context, the model is strictly constrained to output **`"Information Not Found"`** without hallucinating external world knowledge.
* **Exact Paragraph Citations**: Enforces structured citation metadata (e.g., `[Paragraph 1]`, `[Source: CSV Row 3]`) for every claim made.
* **Local Index Caching**: Offline pre-caching mechanism (`precache.py`) for rapid startup.

---

### Project 4: System Persona Architecture & Multi-Layer Guardrail Bot
* **Directory**: [`Task 4/`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%204)
* **Scripts**: [`Task 4/app.py`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%204/app.py), [`Task 4/guardrail_engine.py`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%204/guardrail_engine.py), [`Task 4/test_app.py`](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/Prompts/Task%204/test_app.py)

#### Core Purpose & Features
Provides an enterprise AI Safety framework that enforces strict system personas and protects against prompt injection, jailbreaks, and sensitive data leakage.
* **Multi-Layer Defense Pipeline**:
  1. **Pre-Execution Guardrail**: Filters inputs for PII, system prompt extraction, jailbreak patterns, and illegal/harmful intent prior to API calls.
  2. **Persona Lock System**: Enforces strict persona guidelines (e.g., *Socratic Coding Tutor* who refuses to write full code and guides via questions, or *AI Safety Advisor*).
  3. **Post-Execution Guardrail**: Scans generated outputs before rendering to ensure no leaked API keys, forbidden code blocks, or character breaks occurred.
* **Adversarial Red Teaming Engine**: Automated test suite executing famous jailbreak vectors (DAN 11.0, Developer Mode bypass, System Prompt Extraction, Oppositional Roleplay).
* **Real-time Telemetry & Security Audit Logs**: Graphical dashboard displaying block rate percentages, threat classifications, and latency metrics.

---

## 🛠️ Key Engineering Concepts & Methodologies

| Methodology | Description | Implementation |
| :--- | :--- | :--- |
| **Zero-Shot Prompting** | Instructing the model using precise task definitions without exemplars. | `Task 1` Schema Enforcement |
| **Few-Shot In-Context Learning** | Providing input-output pairs in prompt context to guide layout & edge-cases. | `Task 1` JSON Extractor |
| **Chain-of-Thought (CoT)** | Directing the model to write explicit intermediate logic (`<reasoning>` steps). | `Task 2` Logic Engine |
| **RAG & Context Anchoring** | Combining vector database search (FAISS) with strict negative prompt constraints. | `Task 3` Closed-Book QA |
| **Input/Output Guardrails** | RegEx & semantic regex scanning for prompt injections, PII, and unsafe content. | `Task 4` Guardrail Engine |
| **Red Team Jailbreaking** | Automated penetration testing of LLM prompt robustness against malicious prompts. | `Task 4` Red Team Suite |

---

## 🚀 Installation & Setup Guide

### Prerequisites
* **Python 3.9+** installed on your system.
* **Groq API Key**: A free or enterprise API key from [Groq Console](https://console.groq.com/).

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/Prompt-Engineering-Suite.git
   cd Prompt-Engineering-Suite
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install customtkinter groq sentence-transformers faiss-cpu pandas numpy scikit-learn
   ```

4. **(Optional) Run FAISS Pre-Caching for Task 3**
   ```bash
   python "Task 3/precache.py"
   ```

---

## 💻 Usage Guide

You can launch any of the interactive GUI applications independently:

### Run Task 1 (Extraction Engine)
```bash
python "Task 1/app.py"
```

### Run Task 2 (Chain-of-Thought Engine)
```bash
python "Task 2/app.py"
```

### Run Task 3 (Context-Anchored RAG Chatbot)
```bash
python "Task 3/app.py"
```

### Run Task 4 (Guardrail & Persona System)
```bash
python "Task 4/app.py"
```

### Run Task 4 Security Unit Tests
```bash
python "Task 4/test_app.py"
```

---

## 📦 Technologies & Dependencies

* **Core Framework**: Python 3.9+
* **LLM Provider**: [Groq API](https://groq.com/) (Meta Llama 3.3 70B Versatile, Llama 3 8B, Mixtral)
* **GUI Frameworks**: `CustomTkinter` (Modern Dark UI), `Tkinter`
* **Vector Search & Retrieval**: `faiss-cpu`, `sentence-transformers`, `scikit-learn` (TF-IDF Vectorizer)
* **Data Processing**: `pandas`, `numpy`, `re`, `json`, `pickle`

---
*Created as part of the DecodeLabs Internship Prompt Engineering & AI Safety Curriculum.*
