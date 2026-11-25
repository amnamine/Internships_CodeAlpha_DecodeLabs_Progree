# CodeAlpha Machine Learning Internship - Month 1

Welcome to the official repository for the **CodeAlpha Machine Learning Internship (Month 1)**. This repository houses complete implementations, datasets, evaluation metrics, and visualization plots for all four machine learning and deep learning tasks.

---

## 📋 Table of Contents
- [📌 Overview & Challenge](#-overview--challenge)
- [📁 Repository Structure](#-repository-structure)
- [🛠️ Requirements & Installation](#%EF%B8%8F-requirements--installation)
- [🚀 Tasks Detailed Breakdown](#-tasks-detailed-breakdown)
  - [Task 1: Credit Scoring Model](#task-1-credit-scoring-model)
  - [Task 2: Emotion Recognition from Speech](#task-2-emotion-recognition-from-speech)
  - [Task 3: Handwritten Character Recognition](#task-3-handwritten-character-recognition)
  - [Task 4: Disease Prediction from Medical Data](#task-4-disease-prediction-from-medical-data)
- [🏆 Key Learnings](#-key-learnings)

---

## 📌 Overview & Challenge

This month-long challenge focuses on applying fundamental to advanced machine learning and deep learning algorithms to solve real-world problems. The curriculum covers:
1. **Classification & Risk Modeling:** Building credit scorecards using two different datasets and comparing classic ML algorithms against boosting models.
2. **Speech Signal Processing:** Leveraging Recurrent Neural Networks (BiLSTMs) and MFCC feature extraction for human emotion classification from audio recordings.
3. **Computer Vision & Image Classification:** Building deep Convolutional Neural Networks (CNNs) for high-accuracy handwritten digit recognition.
4. **Healthcare Analytics & Predictive Modeling:** Cleaning medical data (imputing biologically invalid zeros) and comparing classifiers (including XGBoost and SVM) to predict diabetes outcome.

---

## 📁 Repository Structure

```directory
.
├── README.md
├── Task1/
│   ├── Task1.ipynb                   # Credit scoring on custom creditscoring.csv dataset
│   ├── TaskOne.ipynb                 # Credit scoring on Kaggle's "Give Me Some Credit" dataset
│   ├── creditscoring.csv             # Custom dataset (12k samples)
│   ├── cs-training.csv               # Kaggle training dataset
│   ├── cs-test.csv                   # Kaggle test dataset
│   ├── confusion_matrices.png        # CM plot for Task1.ipynb models
│   ├── credit_scoring_results.png    # Results comparison plot for TaskOne.ipynb models
│   ├── feature_importance.png        # Random Forest feature importance plot
│   ├── model_comparison.png          # Metric comparison bar plot for Task1.ipynb
│   └── roc_curves.png                # ROC curves plot for Task1.ipynb
├── Task2/
│   └── Task2.ipynb                   # Speech emotion classification (TESS dataset, Bidirectional LSTM)
├── Task3/
│   ├── Task3codealpha.ipynb          # Handwritten digit recognition (MNIST dataset, CNN)
│   ├── accuracy_loss_curves.png      # Training history curves
│   ├── confusion_matrix.png          # Test set confusion matrix heatmap
│   └── random_predictions.png        # Sample test predictions with confidence levels
└── Task4/
    ├── Task4.ipynb                   # Disease prediction (Pima Indians Diabetes dataset)
    ├── diabetes.csv                  # Diabetes dataset
    ├── confusion_matrices.png        # CM subplots for all models
    ├── model_comparison.png          # Accuracy & AUC comparison bar chart
    └── roc_curve_comparison.png      # ROC curve comparisons
```

---

## 🛠️ Requirements & Installation

To run the Jupyter Notebooks locally, install the necessary dependencies:

```bash
pip install numpy pandas matplotlib seaborn scikit-learn tensorflow xgboost librosa
```

*Note: For GPU acceleration in Task 2 and Task 3, a CUDA-enabled GPU and appropriate TensorFlow GPU libraries are highly recommended.*

---

## 🚀 Tasks Detailed Breakdown

### Task 1: Credit Scoring Model

This folder contains **two separate implementations** targeting credit scoring and risk modeling:

#### Implementation A: Custom Credit Scoring ([Task1.ipynb](file:///d:/AMINE2/COURS%20FAC/travaux/CODELABSINTERSHIP/ML/Task1/Task1.ipynb))
* **Objective:** Predict creditworthiness (1 = Creditworthy, 0 = Not Creditworthy) based on past financial features.
* **Dataset (`creditscoring.csv`):** 12,000 samples, containing Age, Gender, Education, Income, Debt, Credit Score, Loan Amount, Loan Term, Payment History, and Employment Status.
* **Feature Engineering:** Added `Debt_to_Income` and `Loan_to_Income` ratios, followed by one-hot encoding of categorical features.
* **Performance Summary:**
  | Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
  | :--- | :---: | :---: | :---: | :---: | :---: |
  | **Logistic Regression** | 70.25% | 70.25% | 100.00% | 82.53% | 0.5177 |
  | **Decision Tree** | 69.17% | 70.28% | 97.21% | 81.58% | 0.4917 |
  | **Random Forest** | 70.25% | 70.25% | 100.00% | 82.53% | 0.5065 |

#### Implementation B: Kaggle "Give Me Some Credit" ([TaskOne.ipynb](file:///d:/AMINE2/COURS%20FAC/travaux/CODELABSINTERSHIP/ML/Task1/TaskOne.ipynb))
* **Objective:** Predict the probability that somebody will experience financial distress in the next two years.
* **Dataset (`cs-training.csv` & `cs-test.csv`):** Standard Kaggle dataset containing historical financial behavior.
* **Feature Engineering:** Added `TotalLatePayments`, `IncomePerDependent`, and age group bins. Imputed missing values using median imputation.
* **Performance Summary:**
  | Model | Accuracy | ROC-AUC |
  | :--- | :---: | :---: |
  | **Logistic Regression** | 77.25% | 0.8024 |
  | **Decision Tree** | 79.77% | 0.8539 |
  | **Random Forest** | 82.83% | 0.8647 |
  | **Gradient Boosting** | **93.72%** | **0.8698** |

---

### Task 2: Emotion Recognition from Speech

* **Objective:** Classify human speech recordings into 7 distinct emotions (`angry`, `disgust`, `fear`, `happy`, `neutral`, `pleasant_surprise`, `sad`).
* **Dataset:** Toronto Emotional Speech Set (TESS) containing 2,800 audio samples (400 per emotion class).
* **Audio Preprocessing & Feature Extraction:**
  - Audio signals loaded using `librosa`.
  - Extracted 40 Mel-Frequency Cepstral Coefficients (MFCCs) along with their first-order delta ($\Delta$) and second-order delta ($\Delta\Delta$) coefficients, yielding 120 features per time-frame.
  - Sequences padded or truncated to a fixed length of 130 frames.
* **Model Architecture (Bidirectional LSTM):**
  - Designed a deep recurrent network inside TensorFlow Keras:
    - **BiLSTM Layer 1:** 256 units + Batch Normalization + Dropout (0.3)
    - **BiLSTM Layer 2:** 128 units + Batch Normalization + Dropout (0.3)
    - **BiLSTM Layer 3:** 64 units + Batch Normalization + Dropout (0.3)
    - **Dense Head 1:** 256 units (ReLU) + Batch Normalization + Dropout (0.4)
    - **Dense Head 2:** 128 units (ReLU) + Dropout (0.3)
    - **Dense Output:** 7 units (Softmax)
  - Trained using TensorFlow's `MirroredStrategy` across multiple GPUs.
* **Performance Summary:**
  - **Test Accuracy:** Outstanding classification performance achieving **>98% accuracy** on the test split.

---

### Task 3: Handwritten Character Recognition

* **Objective:** Identify handwritten digits (0 through 9) using computer vision.
* **Dataset:** MNIST Dataset (60,000 training images, 10,000 testing images of size 28x28 grayscale).
* **Model Architecture (Deep CNN):**
  - **Conv Layer 1 & 2:** 32 filters (3x3), ReLU + Batch Normalization + MaxPool + Dropout (0.25)
  - **Conv Layer 3 & 4:** 64 filters (3x3), ReLU + Batch Normalization + MaxPool + Dropout (0.25)
  - **Conv Layer 5:** 128 filters (3x3), ReLU + Batch Normalization + MaxPool + Dropout (0.25)
  - **Dense Layer:** 256 units (ReLU) + Batch Normalization + Dropout (0.5)
  - **Dense Output:** 10 units (Softmax)
* **Performance Summary:**
  - **Test Accuracy:** **99.65%**
  - **Test Loss:** **0.0119**
  - Saved outputs: `confusion_matrix.png`, `accuracy_loss_curves.png`, and `random_predictions.png` showcasing predictions on random test images with their confidence percentages.

---

### Task 4: Disease Prediction from Medical Data

* **Objective:** Predict whether a patient has diabetes based on diagnostic measurements.
* **Dataset (`diabetes.csv`):** Pima Indian Diabetes dataset containing Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, and Age.
* **Data Cleaning & Imputation:**
  - Replaced biologically invalid zero values in Glucose, BloodPressure, SkinThickness, Insulin, and BMI with the conditional median computed by patient Outcome to prevent model bias.
  - Applied standard scaling to prepare features for distance-based and linear estimators.
* **Models Evaluated:** Logistic Regression, SVM (RBF Kernel), Random Forest, XGBoost.
* **Performance Summary:**
  | Model | Accuracy | Precision (diabetic) | Recall (diabetic) | F1-Score (diabetic) | ROC-AUC |
  | :--- | :---: | :---: | :---: | :---: | :---: |
  | **Logistic Regression** | 70.78% | 0.60 | 0.50 | 0.55 | 0.8130 |
  | **SVM** | 74.03% | 0.65 | 0.56 | 0.60 | 0.7964 |
  | **Random Forest** | 74.03% | 0.65 | 0.56 | 0.60 | 0.8161 |
  | **XGBoost** | **75.97%** | **0.67** | **0.61** | **0.64** | 0.8081 |

---

## 🏆 Key Learnings

* **Audio Signal Processing:** Extracting, concatenating, and processing MFCCs and delta coefficients into structured sequence data for BiLSTM architectures.
* **Medical Data Cleaning:** Imputing invalid zeros via conditional median grouping to maintain data distributions.
* **Regularization & Training Stability:** Leveraging Batch Normalization, Dropout, and Keras Callbacks (`EarlyStopping`, `ReduceLROnPlateau`) to prevent overfitting.
* **Multi-GPU Parallelism:** Distributing deep learning workloads using TensorFlow's `MirroredStrategy` for high-throughput model training.
* **Classifier Comparisons:** Visualizing model behavior via ROC-AUC and model comparison bar charts to choose appropriate models for tabular vs. unstructured data.

---
*Internship completed under mentoring by CodeAlpha.*
