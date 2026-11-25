# DecodeLabs AI Industrial Training Kit 🤖 (Batch 2026)

Welcome to the **DecodeLabs AI Industrial Training Kit** repository. This workspace contains four progressive hands-on projects designed to build, validate, and scale artificial intelligence applications. Each week represents a milestone—from foundation logic-building using rule-based algorithms to advanced deep learning models for recommendations and computer vision.

---

## 📂 Repository Structure

The workspace is organized into components representing each training phase, along with references and datasets:

*   **[pdfs/](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/pdfs)**: Contains the training guidelines and specifications for each project.
*   **[week1/](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week1)**:
    *   **[main.py](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week1/main.py)**: The source code for the animated rule-based chatbot application.
*   **[week2/](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week2)**:
    *   **[diabetes_classification.ipynb](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week2/diabetes_classification.ipynb)**: Data classification workflow using Logistic Regression.
    *   **[diabetes.csv](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week2/diabetes.csv)**: Pima Indians Diabetes database.
*   **[week3/](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week3)**:
    *   **[recommender_system.ipynb](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week3/recommender_system.ipynb)**: Implementation of popularity, content-based, SVD, and PyTorch Neural CF recommendation models.
    *   **[Books.csv](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week3/Books.csv)** / **[Ratings.csv](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week3/Ratings.csv)** / **[Users.csv](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week3/Users.csv)**: Book-Crossing dataset.
*   **[week4/](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week4)**:
    *   **[mnist_recognition.ipynb](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/week4/mnist_recognition.ipynb)**: TensorFlow/Keras Convolutional Neural Network (CNN) pipeline for handwritten digit recognition.

---

## 🛠️ Project Breakdown & Architecture

### 🤖 Project 1: Aura AI - Rule-Based Intelligent Chatbot
*   **Objective**: Build a continuous digital loop representing user interaction using explicit control flow and conditional rules.
*   **Core Features**:
    *   **Multi-Persona Dynamics**: Implements three conversation personalities: **Sage** (academic and formal), **Nova** (witty and sarcastic), and **Zen** (philosophical and calm).
    *   **Interactive Animated UI**: Designed with `customtkinter`. Features a floating canvas-based avatar that blinks randomly, changes mouth structures depending on typing/thinking states, and tracks live conversation statistics (active elapsed time, message counts).
    *   **Topic Engine**: Handles pre-defined intents such as greetings, exits, definitions of Python/ML, jokes, weather fallbacks, and developer information.
*   **Key Skills**: Python syntax, `customtkinter` layout grids, canvas drawing, multithreading events, decision control flow.

### 📈 Project 2: Supervised Machine Learning - Diabetes Classification
*   **Objective**: Design a supervised classification pipeline to identify patient risks using biometric patterns.
*   **Pipeline Details**:
    *   **Exploratory Data Analysis (EDA)**: Profiling dimensions, null checks, and statistical descriptions.
    *   **Preprocessing**: Normalizing input scale variance across predictors (Age, Glucose, BMI, Blood Pressure) using `StandardScaler` to ensure stable optimization gradient updates.
    *   **Model Training**: Logistic Regression trained on a stratified 80-20 dataset split to handle output category representation.
    *   **Performance Metrics**: Evaluated using Precision-Recall F1-scores, Confusion Matrix plots via Seaborn, and Area Under the ROC Curve (**ROC AUC score: 0.8230**).
*   **Key Skills**: Scikit-Learn pipelines, supervised training workflows, evaluation curves, classification heuristics.

### 📚 Project 3: Personalization Phase - Book Recommendation System
*   **Objective**: Bridge raw user rating interactions and item descriptions to predict user preferences.
*   **Implemented Methodologies**:
    1.  **Popularity-Based Recommender**: Establishing a baseline model using a **Weighted Rating (WR)** IMDb formula:
        $$WR = \left(\frac{v}{v+m} \cdot R\right) + \left(\frac{m}{v+m} \cdot C\right)$$
        *Where $v$ is the rating count, $m$ is the 90th percentile threshold, $R$ is the average rating, and $C$ is the global mean.*
    2.  **Content-Based Filtering**: Combining item metadata fields (Book-Title, Book-Author, Publisher), translating metadata into high-dimensional vector representations using **TF-IDF Vectorizer**, and computing **Cosine Similarity** rankings against search queries.
    3.  **Collaborative Filtering (Matrix Factorization)**: Decomposing a filtered, low-sparsity user-item interaction matrix into lower-rank latent factor representations using **Singular Value Decomposition (SVD)**.
    4.  **Neural Collaborative Filtering (Deep Learning)**: Constructing a PyTorch Neural Network architecture that maps user indices and book indices into parallel dense **Embedding layers**, concatenates the latent representation vectors, and feeds them through Fully Connected Linear layers with **Dropout** and **ReLU** activations to learn complex non-linear similarity dependencies.
    5.  **Unified Routing API**: A single interface that maps arguments to specific models with robust empty query / cold-start fallbacks.
*   **Key Skills**: PyTorch model development, matrix decomposition, sparse indexing, text vectorization.

### 👁️ Project 4: Computer Vision - MNIST Digit Recognition
*   **Objective**: Train a deep Convolutional Neural Network (CNN) to categorize handwritten digits.
*   **Model Architecture**:
    *   **Input Layer**: Accepts normalized inputs reshaped to single-channel 3D tensors: `(28, 28, 1)`.
    *   **Convolutional Layer 1**: 32 filters, $3\times3$ kernel, ReLU activation to capture local spatial edges.
    *   **MaxPooling 1**: $2\times2$ stride to reduce spatial dimensions and compute translational invariance.
    *   **Convolutional Layer 2**: 64 filters, $3\times3$ kernel, ReLU activation for complex feature hierarchies.
    *   **MaxPooling 2**: $2\times2$ pooling.
    *   **Flattening Layer**: Transforms 2D feature grids into a 1D vector (`1600` features).
    *   **Dense Layer**: 64 dense nodes, ReLU activation.
    *   **Regularization**: Dropout layer ($0.3$ rate) to prevent co-adaptation of weights.
    *   **Output Layer**: 10 dense nodes, softmax activation representing probability distributions for digits 0-9.
*   **Training & Compilation**: Uses `Adam` optimizer, `Sparse Categorical Crossentropy` loss, and `EarlyStopping` callback tracking validation metrics.
*   **Key Skills**: CNN architecture, image scaling/reshaping, regularization layers, TensorFlow model serving.

---

## 🚀 Getting Started & Execution Guide

### 📋 Prerequisites

Create a virtual environment and install the required dependencies:

```bash
# Clone or navigate to the workspace
# Install the required packages
pip install customtkinter pandas numpy matplotlib seaborn scikit-learn scipy torch tensorflow
```

### 💻 Running the Projects

#### 1. Aura AI Chatbot
Execute the Python script to open the CustomTkinter GUI:
```bash
python week1/main.py
```

#### 2. Diabetes Classification
Start Jupyter Notebook or open VS Code and run the cells in:
```bash
jupyter notebook week2/diabetes_classification.ipynb
```

#### 3. Recommender System
Download the Book-Crossing dataset files and place them in the `week3/` directory, then execute the cells in:
```bash
jupyter notebook week3/recommender_system.ipynb
```

#### 4. MNIST Digit Recognition
Run the Keras/TensorFlow model code in:
```bash
jupyter notebook week4/mnist_recognition.ipynb
```

---

## 📖 Training Documentation & Kits

For detailed assignments, qualification criteria, and weekly milestones, refer to the PDF manuals in the reference folder:
*   **[Artificial intelligence P1.pdf](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/pdfs/Artificial%20intelligence%20P1.pdf)**: Week 1 Guide.
*   **[Artificial intelligence P2.pdf](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/pdfs/Artificial%20intelligence%20P2.pdf)**: Week 2 Guide.
*   **[Artificial Intelligence Project 3.pdf](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/pdfs/Artificial%20Intelligence%20Project%203.pdf)**: Week 3 Guide.
*   **[Artificial Intelligence Project 4.pdf](file:///d:/AMINE2/COURS%20FAC/travaux/DECODELABSINTERNSHIP/AI/weeksAI/pdfs/Artificial%20Intelligence%20Project%204.pdf)**: Week 4 Guide.
