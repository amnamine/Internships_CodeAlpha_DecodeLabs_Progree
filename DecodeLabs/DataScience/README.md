# 🚀 Decode Labs Data Science Industrial Internship Kit (Batch 2026)

Welcome to the **Decode Labs Data Science Internship** repository. This workspace contains an industry-standard, production-grade portfolio of four end-to-end Data Science and Machine Learning projects covering **Advanced Exploratory Data Analysis & Feature Engineering**, **Imbalanced Classification & Fraud Detection Pipelines**, **Unsupervised Customer Segmentation & Business Intelligence**, and **Natural Language Processing (NLP) & Sentiment Analysis**.

---

## 📊 Internship Curriculum Overview

| Project | Domain / Topic | Primary Algorithms & Tools | Key Deliverables & Outcomes |
| :--- | :--- | :--- | :--- |
| **[Task 1](#-project-1-advanced-eda--feature-engineering)** | **Advanced EDA & Feature Engineering** | Pandas, NumPy, Scikit-Learn, KNN Imputation, IQR, Random Forest | Missing data imputation, outlier neutralization, 4 domain financial features, clean dataset export, baseline classifier. |
| **[Task 2](#-project-2-supervised-learning--credit-card-fraud-detection)** | **Supervised Learning (Imbalanced Classification)** | SMOTE, RobustScaler, Logistic Regression, Random Forest, XGBoost | Leak-free resampling pipelines, PR/ROC-AUC evaluation, decision threshold tuning for financial fraud prevention. |
| **[Task 3](#-project-3-unsupervised-learning--customer-segmentation)** | **Unsupervised Learning & Clustering** | PCA, K-Means Clustering, Elbow Method, Silhouette Analysis, Seaborn | Dimensionality reduction, mathematical cluster validation, actionable customer marketing personas. |
| **[Task 4](#-project-4-nlp--sentiment-analysis)** | **NLP & Computational Linguistics** | NLTK, TF-IDF Vectorization, MultinomialNB, LinearSVC, Logistic Regression | End-to-end NLP pipeline, negation-aware stopword filtering, unigram/bigram n-grams, saved deployment artifacts (`.joblib`). |

---

## 📁 Repository Directory Structure

```plaintext
Data Science/
├── Data Science Project 1.pdf        # Task 1 Industrial Brief & Guidelines
├── Data Science Project 2.pdf        # Task 2 Industrial Brief & Guidelines
├── Data Science Project 3.pdf        # Task 3 Industrial Brief & Guidelines
├── Data Science Project 4.pdf        # Task 4 Industrial Brief & Guidelines
│
├── Task 1/                           # Project 1: Advanced EDA & Feature Engineering
│   ├── messy_dataset.csv             # Raw dataset with missing values, noise, and outliers
│   ├── clean_dataset.csv             # Cleaned, imputed, and feature-engineered dataset
│   ├── generate_all.py               # Complete automation script for data generation & modeling
│   ├── project1_advanced_eda_ml.ipynb # Fully documented interactive Jupyter Notebook
│   └── model_evaluation_metrics.png  # Confusion matrix and ROC-AUC curve visualization
│
├── Task 2/                           # Project 2: Supervised Learning (Fraud Detection)
│   ├── creditcard.csv                # European cardholders fraud dataset (284,807 transactions)
│   └── fraud_detection_pipeline.ipynb # End-to-end SMOTE, scaling, modeling, and threshold tuning notebook
│
├── Task 3/                           # Project 3: Unsupervised Learning (Customer Segmentation)
│   ├── Mall_Customers.csv            # Retail customer dataset (Age, Income, Spending Score)
│   └── Customer_Segmentation_Task3.ipynb # Dimensionality reduction (PCA), K-Means & persona profiling
│
└── Task 4/                           # Project 4: NLP & Sentiment Analysis
    ├── IMDB Dataset.csv              # 50,000 benchmark movie reviews (Positive / Negative)
    ├── requirements.txt              # Task-specific Python dependencies
    ├── build_notebook.py             # Script generating the reproducible sentiment analysis notebook
    ├── sentiment_analysis.ipynb      # Main interactive NLP exploration & model comparison notebook
    ├── run_pipeline.py               # Modular command-line training and evaluation CLI
    ├── src/                          # Modular production source package
    │   ├── __init__.py
    │   ├── preprocessor.py           # Text cleaning, HTML stripping, lemmatization & tokenization
    │   ├── feature_extraction.py     # TF-IDF mathematical vectorization wrapper
    │   ├── model.py                  # Model training, evaluation, and serialization logic
    │   └── utils.py                  # Plotting routines (ROC, PR curves, WordClouds, top n-grams)
    └── outputs/                      # Generated evaluation artifacts & serialized models
        ├── models/                   # tfidf_vectorizer.joblib & best_sentiment_model.joblib
        └── plots/                    # High-res confusion matrices, wordclouds, top words
```

---

## 🔬 In-Depth Project Breakdowns

### 🏷️ Project 1: Advanced EDA & Feature Engineering
* **Goal**: Transform noisy, chaotic financial data into high-quality training fuel for machine learning algorithms through strict statistical logic.
* **Methodology**:
  1. **Data Cleaning & Imputation**: Addressed MCAR/MAR missing values across continuous features using **K-Nearest Neighbors (KNN) Imputation** and median backfilling; standard categorical mode imputation for discrete columns.
  2. **Outlier Neutralization**: Detected and capped multivariate anomalies using the **Interquartile Range (IQR)** method (`[Q1 - 1.5*IQR, Q3 + 1.5*IQR]`).
  3. **Feature Engineering**: Engineered 4 high-signal domain features:
     - `debt_to_income_ratio` = $\text{Total Debt} / \text{Annual Income}$
     - `loan_to_income_ratio` = $\text{Loan Amount} / \text{Annual Income}$
     - `credit_utilization_ratio` = $\text{Credit Card Balance} / \text{Total Debt}$
     - `financial_stress_index` = Combined weighted risk metric
  4. **Modeling**: Trained a `RandomForestClassifier` demonstrating superior discrimination on default prediction with ROC-AUC evaluation.

---

### 🛡️ Project 2: Supervised Learning — Credit Card Fraud Detection
* **Goal**: Build and optimize a classification pipeline capable of pinpointing fraudulent transactions in an extreme class-imbalance environment (**0.17% fraud rate** / 492 frauds out of 284,807 transactions).
* **Methodology**:
  1. **Data Preprocessing**: Handled skewed time and monetary attributes using `RobustScaler` (resistant to extreme financial outliers).
  2. **Leak-Free Imbalance Handling**: Applied **SMOTE (Synthetic Minority Over-sampling Technique)** strictly on training folds via `imblearn` pipelines to avoid data snooping.
  3. **Model Exploration**: Evaluated **Logistic Regression**, **Random Forest Classifier**, and **XGBoost Classifier**.
  4. **Strict Evaluation Metrics**: Discarded raw accuracy in favor of:
     - **Precision-Recall (PR) Curves & Average Precision (AP)**
     - **Receiver Operating Characteristic (ROC-AUC)**
     - **False Positive vs. False Negative Cost Tradeoff Analysis** and decision threshold tuning.

---

### 🛍️ Project 3: Unsupervised Learning — Customer Segmentation
* **Goal**: Uncover latent mathematical customer segments from unlabelled retail transaction data and translate mathematical clusters into actionable marketing personas.
* **Methodology**:
  1. **Dimensionality Reduction**: Implemented **Principal Component Analysis (PCA)** to capture maximal variance while mapping high-dimensional spaces into interpretable 2D/3D visualizations.
  2. **Mathematical Cluster Optimization**:
     - **Elbow Method (Inertia / WCSS)** to detect the optimal inflection point.
     - **Silhouette Score Analysis** to validate intra-cluster cohesion and inter-cluster separation.
  3. **K-Means Clustering**: Partitioned customer data based on Euclidean distance metrics.
  4. **Business Persona Translation**:
     - *Frugal Savers*: High income, low spending.
     - *Affluent Spenders / VIPs*: High income, high spending.
     - *Careful / Conservative Consumers*: Moderate income, moderate spending.
     - *Impulsive / Young Spenders*: Low income, high spending.

---

### 💬 Project 4: NLP & Sentiment Analysis
* **Goal**: Engineer a Natural Language Processing system to clean, vectorize, and categorize unstructured human reviews (IMDB 50k Dataset) into **Positive** or **Negative** sentiment.
* **Methodology**:
  1. **Text Preprocessing**: Stripped HTML markup and URLs; normalized contractions; preserved sentiment-critical negations (`not`, `never`, `no`) while stripping standard stopwords; applied **WordNet Lemmatization**.
  2. **Mathematical Vectorization**: Implemented **TF-IDF (Term Frequency - Inverse Document Frequency)** with unigram and bigram feature extraction ($n\text{-gram range}=(1, 2)$).
  3. **Classifier Benchmarking**:
     - **Multinomial Naive Bayes (`MultinomialNB`)**: ~86.5% Accuracy / F1.
     - **Linear Support Vector Machine (`LinearSVC`)**: **~90.0% Accuracy / F1, ROC-AUC > 0.95**.
     - **Logistic Regression**: ~89.5% Accuracy / F1.
  4. **Artifact Export & Modular Code**: Modularized into `src/` modules with standalone CLI training (`run_pipeline.py`) and joblib model serialization.

---

## ⚡ Quickstart & Setup Guide

### 1. Prerequisites & Environment Setup
Clone this repository and create a Python virtual environment:
```bash
git clone <your-repo-url>
cd "Data Science"

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
Install all required libraries across all tasks:
```bash
pip install numpy pandas scikit-learn matplotlib seaborn imbalanced-learn xgboost nltk wordcloud joblib jupyter
```

Download NLTK corpora (for NLP tasks):
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt')"
```

### 3. Running the Projects

#### Task 1:
```bash
cd "Task 1"
python generate_all.py
# Or launch the notebook:
jupyter notebook project1_advanced_eda_ml.ipynb
```

#### Task 2:
```bash
cd "Task 2"
jupyter notebook fraud_detection_pipeline.ipynb
```

#### Task 3:
```bash
cd "Task 3"
jupyter notebook Customer_Segmentation_Task3.ipynb
```

#### Task 4:
```bash
cd "Task 4"
# Run automated pipeline CLI (sample or full):
python run_pipeline.py --sample 5000
# Or launch interactive notebook:
jupyter notebook sentiment_analysis.ipynb
```

---

## 👥 Internship & Author Details
* **Program**: Industrial Training Kit — Batch 2026
* **Organization**: DecodeLabs ([decodelabs.tech](http://www.decodelabs.tech))
* **Track**: Data Science & Machine Learning
