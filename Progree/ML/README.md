# 🚀 PROGREE Machine Learning Internship Repository

Welcome to the **PROGREE Machine Learning Internship** project repository! This repository hosts end-to-end implementations of foundational to advanced Machine Learning and Deep Learning pipelines, ranging from regularized predictive regression and convolutional vision networks to cost-sensitive clinical classification on imbalanced medical diagnostic datasets.

---

## 📂 Repository Structure & Project Overview

```text
├── 📄 Machine Learning Tasks & Instructions.pdf   # Official Internship Tasks & Guidelines
│
├── 📁 Task 2/                                    # Predictive Linear Regression Model Pipeline
│   ├── 📓 Predictive_Linear_Regression_Pipeline.ipynb
│   └── 📊 housing.csv                            # California Housing Dataset
│
├── 📁 Task 3/                                    # Multi-Class Image Classification (CNN)
│   ├── 📓 cifar10.ipynb                          # CIFAR-10 Deep Learning Pipeline
│   └── 📦 cifar10_cnn.h5                         # Trained Keras Model Artifact
│
├── 📁 Task 4/                                    # Clinical Disease Predictor on Imbalanced Data
│   ├── 📓 task4_clinical_disease_predictor_pipeline.ipynb
│   ├── 🐍 generate_nb.py                         # Programmatic Pipeline Generator Script
│   └── 📊 data.csv                               # Breast Cancer Wisconsin (Diagnostic) Dataset
│
└── 📄 README.md                                  # Repository Documentation & Project Summary
```

---

## 📑 Tasks Breakdown & Technical Highlights

### 📌 [Task 1: Professional LinkedIn Announcement](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/ML/Machine%20Learning%20Tasks%20%26%20Instructions.pdf)
* **Objective**: Official announcement of internship onboarding and professional networking.
* **Focus**: Sharing internship acceptance, goals, and connecting with the community using `#machinelearning #ml #datascience #progree`.

---

### 📌 [Task 2: Predictive Linear Regression Model Pipeline](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/ML/Task%202/Predictive_Linear_Regression_Pipeline.ipynb)
* **Objective**: Build a robust, regularized supervised regression model to predict continuous numerical values (`median_house_value`).
* **Dataset**: California Housing Dataset ([housing.csv](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/ML/Task%202/housing.csv)).
* **Key Components & Highlights**:
  * **Exploratory Data Analysis (EDA)**: Correlation heatmaps, geographic coordinate mapping vs. housing value, skewness and distribution analysis.
  * **Data Preprocessing & Pipeline**:
    * Imputation of missing values via `SimpleImputer(strategy='mean')`.
    * Continuous feature standardization with `StandardScaler`.
    * Categorical feature transformation via `OneHotEncoder(handle_unknown='ignore')`.
    * End-to-end integration with Scikit-Learn `ColumnTransformer` & `Pipeline` ensuring **zero data leakage**.
  * **Model Training & Regularization**:
    * Baseline Ordinary Least Squares (`LinearRegression`).
    * $L_2$ Regularization (`RidgeCV`) with cross-validated optimal $\alpha$ search.
    * $L_1$ Regularization (`LassoCV`) for automated feature selection and sparsity profiling.
  * **Evaluation & Diagnostics**:
    * Performance logging: $R^2$, $\text{RMSE}$, and $\text{MAE}$ across train/test splits.
    * Diagnostic visualizations: Actual vs. Predicted plots, Residual Distributions, Residuals vs. Fitted Values, and Feature Coefficient Impact charts.

---

### 📌 [Task 3: Multi-Class Image Classification Convolutional Neural Network (CNN)](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/ML/Task%203/cifar10.ipynb)
* **Objective**: Construct and train a deep learning vision pipeline categorizing raw pixel image arrays across 10 object classes.
* **Dataset**: **CIFAR-10** (60,000 $32\times32\times3$ RGB images across 10 classes: *Airplane, Automobile, Bird, Cat, Deer, Dog, Frog, Horse, Ship, Truck*).
* **Key Components & Highlights**:
  * **Data Pipeline**: Min-max normalization (`[0, 1]` scale float conversion) and stratified train/validation/test partitioning.
  * **Deep Architecture (TensorFlow / Keras)**:
    * Custom multi-stage 2D Convolutional feature extractors (`Conv2D` with ReLU activation, kernel size $3\times3$).
    * Spatial dimension reduction using `MaxPooling2D(pool_size=(2, 2))`.
    * Feature flattening and high-level representation via Dense layers with Softmax multi-class output.
  * **Optimization & Training**:
    * Loss: Sparse Categorical Crossentropy.
    * Optimizer: Adam.
    * 40-epoch training schedule monitoring loss and accuracy convergence.
  * **Evaluation & Diagnostics**:
    * Multi-class Confusion Matrix with Seaborn heatmap rendering.
    * Class-wise Precision, Recall, and F1-Score breakdown via Scikit-Learn `classification_report`.
    * Visual inference verification on sample test images displaying True vs. Predicted labels.
    * Serialized model artifact saved as `cifar10_cnn.h5`.

---

### 📌 [Task 4: High-Imbalance Clinical Disease Predictor Pipeline (Mini-Project)](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/ML/Task%204/task4_clinical_disease_predictor_pipeline.ipynb)
* **Objective**: Architect an end-to-end medical diagnosis classification system designed to detect early physiological abnormalities from skewed clinical data, prioritizing the reduction of life-threatening **False Negatives** (maximizing **Recall/Sensitivity**).
* **Dataset**: UCI Breast Cancer Wisconsin (Diagnostic) Dataset ([data.csv](file:///d:/AMINE2/COURS%20FAC/travaux/PROGREE_INTERNSHIP/ML/Task%204/data.csv)) — 569 instances, 30 fine-needle aspirate (FNA) morphological features.
* **Key Components & Highlights**:
  * **Clinical Framing & EDA**:
    * Target encoding (`Malignant` vs. `Benign`).
    * Nuclear morphology distribution analysis (mean, standard error, worst features).
    * Multicollinearity diagnostic matrix and removal of non-informative columns (`id`, `Unnamed: 32`).
  * **Imbalance Mitigation & Leakage Prevention**:
    * Synthetic Minority Over-sampling Technique (**SMOTE**).
    * Cost-Sensitive Class Weighting (`class_weight='balanced'` / `scale_pos_weight`).
    * Rigorous **Stratified 5-Fold Cross-Validation** using `imblearn.pipeline.Pipeline` ensuring oversampling occurs strictly within training folds.
  * **Multi-Model Benchmark & Hyperparameter Optimization**:
    * Multi-threaded CPU-optimized grid tuning (`GridSearchCV` with `n_jobs=-1`).
    * **Support Vector Classifier (SVM)** with RBF / Linear kernels & class weighting.
    * **Random Forest Classifier** with ensemble balancing and tree depth tuning.
    * **XGBoost Classifier** with gradient boosted decision trees and positive weight scaling.
  * **Clinical Metrics & Model Explainability**:
    * Comprehensive metrics: Recall (Sensitivity), Specificity, Precision, F1-score, ROC-AUC, and PR-AUC.
    * Comparative Confusion Matrices highlighting zero/minimal false-negative profiles.
    * Overlayed ROC and Precision-Recall Curves.
    * Global Feature Importance ranking identifying pivotal biomarkers (e.g., `worst concave points`, `worst perimeter`, `worst radius`).
    * 2D PCA Clinical Decision Boundary visualization.

---

## 🛠️ Tech Stack & Dependencies

The workflows across this repository leverage modern, industry-standard Python libraries:

| Category | Libraries / Tools |
| :--- | :--- |
| **Core & Scientific Computing** | `Python 3.10+`, `NumPy`, `Pandas` |
| **Machine Learning & Preprocessing** | `Scikit-Learn`, `Imbalanced-Learn (imblearn)`, `XGBoost` |
| **Deep Learning** | `TensorFlow`, `Keras` |
| **Visualization & Reporting** | `Matplotlib`, `Seaborn`, `nbformat` |
| **Interactive Development** | `Jupyter Notebooks`, `Google Colab / Kaggle Environments` |

---

## ⚡ Getting Started & Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd ML
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install numpy pandas scikit-learn imbalanced-learn xgboost tensorflow matplotlib seaborn jupyter nbformat
   ```

4. **Launch Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```
   Navigate to any of the task folders (`Task 2`, `Task 3`, or `Task 4`) to run and inspect the pipelines.

---

## 👥 Author & Acknowledgements
* **Intern / Author**: Amine
* **Program**: **PROGREE Machine Learning Internship**
