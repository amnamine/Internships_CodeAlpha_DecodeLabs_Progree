# CodeAlpha Frontend Development Internship

Welcome to my repository for the **CodeAlpha Frontend Development Internship** (Module 1). This repository contains four distinct web applications, demonstrating solid frontend development practices using modern styling, advanced responsiveness, interactive elements, and accessible structure.

---

## 📂 Repository Directory Structure

```text
├── Task1/             # Lumière — Interactive Image Gallery
│   ├── index.html     # HTML structure
│   ├── styles.css     # Premium styling & layouts
│   └── script.js      # Carousel, filters, and lightbox logic
├── Task2/             # QuantumCalc — Advanced Scientific Calculator
│   ├── index.html     # Calculator UI structure
│   ├── styles.css     # Dynamic themes, keyboard-focused UI
│   └── script.js      # Scientific operations & display management
├── Task3/             # Personal Portfolio — Developer Showcase
│   ├── index.html     # Portfolio markup
│   ├── styles.css     # Theme toggling, responsive layout, layout systems
│   └── script.js      # Typewriter effect & interactive animations
├── Task4/             # AURA — Premium Music Player
│   ├── index.html     # Music player interface
│   ├── styles.css     # Vinyl disc rotation, glassmorphism, responsive grid
│   ├── script.js      # Web Audio API canvas visualizer, player controls
│   └── assets/        # Audios & album cover assets
└── README.md          # Main repository documentation
```

---

## 🎯 Internship Tasks Overview

Here is a detailed breakdown of each task built during this internship:

### 🖼️ Task 1: Lumière — Interactive Image Gallery
A curated photography gallery using glassmorphism designs and clean interactions.
- **Key Features**:
  - **Category Filters**: Instant category-based image filtering (Nature, Architecture, People, Abstract) with smooth transition animations.
  - **Featured Image Carousel**: Interactive pagination, navigation buttons, autoplay functionality, and slide indicator dots.
  - **Premium Lightbox**: Enlarged image overlay with full metadata (title, caption, category), navigation inside the lightbox, and swipe/keyboard event listeners (`Esc`, `ArrowLeft`, `ArrowRight`).
  - **Modern Aesthetics**: Frosted glass panels, customized modern typography, grain background effects, and fluid micro-interactions.

### 🧮 Task 2: QuantumCalc — The Ultimate Calculator
A feature-rich standard and scientific calculator designed for both desktop and mobile users.
- **Key Features**:
  - **Scientific Operator Panel**: Expandable scientific math drawer supporting trigonometry (sin, cos, tan), logarithmic functions (log, ln), constants ($\pi$, $e$), exponents ($x^y$), square roots ($\sqrt{x}$), and factorials ($x!$).
  - **Multiple Themes**: Instantly switch between three designed themes:
    - `Aurora`: Sleek midnight green with neon highlights.
    - `Solar`: Professional warm contrast style.
    - `Cyberpunk`: Neon yellow, pink, and dark violet theme.
  - **Calculation History**: Persistent, slide-in ledger track of previous evaluations.
  - **Keyboard Support**: Full numpad and operator keyboard shortcuts with visual active feedback states.

### 🌐 Task 3: Personal Portfolio Site
A stunning developer portfolio showcasing projects, skills, and online channels.
- **Key Features**:
  - **Dynamic Code Terminal**: Interactive terminal box rendering user data in JSON, mock console logs, and visual representation.
  - **Interactive Typewriter**: Animates skills like *"Fullstack Developer"*, *"AI Engineer"*, *"Mobile Developer"*, and *"Game Creator"*.
  - **Dual Theme Support**: Light/Dark mode toggling built with native CSS Custom Variables.
  - **Scroll Progress & Animations**: Custom scroll indicator bar, smooth viewport scrolling, and fade-in section load animation.

### 🎵 Task 4: AURA — Premium Music Player
A premium, responsive music player combining local file handling and visual representation.
- **Key Features**:
  - **Canvas Visualizer**: Harnesses the HTML5 **Web Audio API** to render real-time frequency data bar visualizers directly from the active audio stream.
  - **Vinyl CD Deck Rotation**: Seamless turntable rotate animations synced perfectly with the play/pause states.
  - **Robust Audio Deck**: Complete shuffle, repeat, prev, next, mute/unmute, and progress-handle seeking capabilities.
  - **Interactive Playlists**: Custom track listings showing individual song titles, durations, artists, and live playing highlights.

---

## 🚀 How to Run the Projects Locally

To view any of the applications on your local machine, follow these steps:

### Option A: Local Browser Launch
1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/CodeAlpha_ProjectName.git
   ```
2. Navigate to any of the task folders (e.g., `Task1`).
3. Open the corresponding `index.html` file in any modern web browser (Chrome, Firefox, Safari, Edge).

### Option B: Local Live Server (Recommended)
Using a live server environment ensures absolute file paths and Web Audio API permissions resolve flawlessly.
1. Install a local server globally or via extension (e.g., VS Code **Live Server** extension, or `http-server` via npm).
2. Start the server from the root directory:
   ```bash
   npx http-server -p 8080
   ```
3. Open your browser and navigate to:
   - Task 1: `http://localhost:8080/Task1`
   - Task 2: `http://localhost:8080/Task2`
   - Task 3: `http://localhost:8080/Task3`
   - Task 4: `http://localhost:8080/Task4`

---

## 🛠️ Technologies Used
- **Semantic HTML5**: Full accessibility compliance with ARIA landmark and role attributes.
- **Vanilla CSS3**: Tailored Grid, Flexbox, transitions, custom keyframe animations, and custom CSS variables.
- **Modern JS (ES6+)**: LocalStorage integration, Web Audio API context, event listeners, keyboard tracking, and canvas rendering.

---

## 💎 Internship Information
* **Company**: CodeAlpha
* **Program**: Frontend Development Internship
* **Intern**: Mohamed El Amine
* **Submission Module**: Module 1 Tasks
