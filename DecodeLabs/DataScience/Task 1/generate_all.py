import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import KNNImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve
)
from sklearn.preprocessing import StandardScaler
import nbformat as nbf
import os

# Set random seed for reproducibility
np.random.seed(42)
n_samples = 1200

print("1. Generating synthetic messy dataset...")

# Generate baseline features
age = np.random.normal(38, 12, n_samples)
annual_income = np.random.exponential(55000, n_samples) + 20000
loan_amount = np.random.gamma(4, 3500, n_samples)
credit_score = np.random.normal(670, 75, n_samples)
total_debt = annual_income * np.random.uniform(0.1, 0.8, n_samples)
credit_card_balance = annual_income * np.random.uniform(0.02, 0.35, n_samples)
employment_years = np.random.exponential(5, n_samples)

home_ownership_choices = ['RENT', 'OWN', 'MORTGAGE', 'OTHER']
home_ownership = np.random.choice(home_ownership_choices, size=n_samples, p=[0.4, 0.15, 0.4, 0.05])

loan_intent_choices = ['PERSONAL', 'EDUCATION', 'MEDICAL', 'VENTURE', 'HOMEIMPROVEMENT']
loan_intent = np.random.choice(loan_intent_choices, size=n_samples, p=[0.3, 0.25, 0.2, 0.15, 0.1])

# Generate target (loan default risk: 0 = No Default, 1 = Default)
# Synthetic relationship based on financial stress, low credit score, high loan/income ratio
financial_stress_raw = (total_debt / (annual_income + 1)) * 1.5 + (loan_amount / (annual_income + 1)) * 2.0 - (credit_score / 850.0) * 1.2
prob = 1 / (1 + np.exp(-(financial_stress_raw - np.median(financial_stress_raw)) * 4.0))
target = (np.random.uniform(0, 1, n_samples) < prob).astype(int)

df_raw = pd.DataFrame({
    'customer_id': [f'CUST_{1000 + i}' for i in range(n_samples)],
    'age': age,
    'annual_income': annual_income,
    'loan_amount': loan_amount,
    'credit_score': credit_score,
    'total_debt': total_debt,
    'credit_card_balance': credit_card_balance,
    'employment_years': employment_years,
    'home_ownership': home_ownership,
    'loan_intent': loan_intent,
    'default_status': target
})

# Inject Messy Data Issues
# 1. Missing Values (MCAR / MAR)
for col in ['age', 'annual_income', 'loan_amount', 'credit_score', 'total_debt', 'employment_years']:
    mask = np.random.rand(n_samples) < np.random.uniform(0.08, 0.15)
    df_raw.loc[mask, col] = np.nan

mask_cat = np.random.rand(n_samples) < 0.07
df_raw.loc[mask_cat, 'home_ownership'] = np.nan

# Introduce messy string variations
df_raw.loc[df_raw['home_ownership'] == 'RENT', 'home_ownership'] = np.random.choice(['RENT', ' rent ', 'Rent'], size=sum(df_raw['home_ownership'] == 'RENT'))

# 2. Outliers (Extreme unrealistic noise)
outlier_indices_income = np.random.choice(n_samples, size=15, replace=False)
df_raw.loc[outlier_indices_income, 'annual_income'] = np.random.uniform(500000, 2500000, size=15)

outlier_indices_age = np.random.choice(n_samples, size=10, replace=False)
df_raw.loc[outlier_indices_age, 'age'] = np.random.choice([-5, 145, 160], size=10)

outlier_indices_credit = np.random.choice(n_samples, size=10, replace=False)
df_raw.loc[outlier_indices_credit, 'credit_score'] = np.random.choice([-50, 9999], size=10)

# Save messy dataset
df_raw.to_csv('messy_dataset.csv', index=False)
print(f"Messy dataset saved with shape: {df_raw.shape}")
print("Missing values in raw data:")
print(df_raw.isnull().sum())

# --- Step 2: Cleaning & Preprocessing ---
print("\n2. Cleaning data (Imputation & Outlier Handling)...")
df_clean = df_raw.copy()

# Fix string whitespace and casing for categorical variables
df_clean['home_ownership'] = df_clean['home_ownership'].astype(str).str.strip().str.upper()
df_clean['home_ownership'] = df_clean['home_ownership'].replace({'NAN': np.nan})

# Outlier Neutralization using IQR (Interquartile Range Method)
num_cols = ['age', 'annual_income', 'loan_amount', 'credit_score', 'total_debt', 'credit_card_balance', 'employment_years']

# Pre-cap physically impossible domain values before IQR
df_clean.loc[df_clean['age'] < 18, 'age'] = np.nan
df_clean.loc[df_clean['age'] > 100, 'age'] = np.nan
df_clean.loc[(df_clean['credit_score'] < 300) | (df_clean['credit_score'] > 850), 'credit_score'] = np.nan

# Statistical Imputation: KNN Imputation for Numerical Features
print("Applying KNN Imputer for numerical columns...")
imputer = KNNImputer(n_neighbors=5)
df_clean[num_cols] = imputer.fit_transform(df_clean[num_cols])

# Impute categorical column mode
df_clean['home_ownership'] = df_clean['home_ownership'].fillna(df_clean['home_ownership'].mode()[0])
df_clean['loan_intent'] = df_clean['loan_intent'].fillna(df_clean['loan_intent'].mode()[0])

# Apply IQR Capping on skewed numeric columns to neutralize remaining extreme outliers
print("Neutralizing outliers via IQR Capping...")
for col in num_cols:
    Q1 = df_clean[col].quantile(0.25)
    Q3 = df_clean[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Cap values outside lower and upper bounds
    df_clean[col] = np.clip(df_clean[col], lower_bound, upper_bound)

# --- Step 3: Feature Engineering ---
print("\n3. Engineering predictive features...")

# Feature 1: Debt-to-Income (DTI) Ratio
df_clean['debt_to_income_ratio'] = df_clean['total_debt'] / (df_clean['annual_income'] + 1)

# Feature 2: Loan-to-Income (LTI) Ratio
df_clean['loan_to_income_ratio'] = df_clean['loan_amount'] / (df_clean['annual_income'] + 1)

# Feature 3: Credit Card Utilization Rate relative to income
df_clean['credit_utilization_ratio'] = df_clean['credit_card_balance'] / (df_clean['annual_income'] + 1)

# Feature 4: Financial Stress Composite Index
df_clean['financial_stress_index'] = (
    (df_clean['debt_to_income_ratio'] * 0.4) + 
    (df_clean['loan_to_income_ratio'] * 0.4) - 
    ((df_clean['credit_score'] / 850.0) * 0.2)
)

print("Engineered 4 new features: 'debt_to_income_ratio', 'loan_to_income_ratio', 'credit_utilization_ratio', 'financial_stress_index'")

# Save Cleaned CSV
df_clean.to_csv('clean_dataset.csv', index=False)
print("Mathematically clean dataset saved as 'clean_dataset.csv'!")

# --- Step 4: Model Building & Evaluation ---
print("\n4. Training Machine Learning Classification Model...")

# Features & Target preparation
X = df_clean.drop(columns=['customer_id', 'default_status'])
y = df_clean['default_status']

# One-Hot Encoding for categorical features
X = pd.get_dummies(X, columns=['home_ownership', 'loan_intent'], drop_first=True)

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest Classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
clf.fit(X_train_scaled, y_train)

# Predictions & Probabilities
y_pred = clf.predict(X_test_scaled)
y_proba = clf.predict_proba(X_test_scaled)[:, 1]

# Metrics
acc = accuracy_score(y_test, y_pred)
clf_report = classification_report(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_proba)

print("="*60)
print(f"MODEL ACCURACY SCORE: {acc:.4f}")
print("="*60)
print("\nCLASSIFICATION REPORT:")
print(clf_report)
print("="*60)
print("\nCONFUSION MATRIX:")
print(cm)
print("="*60)
print(f"\nROC AUC SCORE: {roc_auc:.4f}")
print("="*60)

# Plot & Save Confusion Matrix & ROC Curve
plt.figure(figsize=(12, 5))

# Subplot 1: Confusion Matrix
plt.subplot(1, 2, 1)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Non-Default (0)', 'Default (1)'],
            yticklabels=['Non-Default (0)', 'Default (1)'])
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.xlabel('Predicted Label', fontsize=12)
plt.ylabel('True Label', fontsize=12)

# Subplot 2: ROC Curve
plt.subplot(1, 2, 2)
fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC Curve (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=14, fontweight='bold')
plt.legend(loc="lower right", fontsize=11)

plt.tight_layout()
plt.savefig('model_evaluation_metrics.png', dpi=300)
plt.close()
print("Saved evaluation plot as 'model_evaluation_metrics.png'.")

# --- Step 5: Generate Clean .ipynb Notebook ---
print("\n5. Creating project1_advanced_eda_ml.ipynb clean notebook...")

nb = nbf.v4.new_notebook()

cells = []

# Title & Overview
cells.append(nbf.v4.new_markdown_cell("""# Project 1: Advanced EDA & Feature Engineering
### End-to-End Machine Learning Pipeline: Data Generation, Statistical Imputation, Outlier Handling, Feature Engineering & Classification

**Author / Internship Project 1**  
**Goal:** Transform raw, chaotic financial/loan data into a mathematically clean dataset ready for machine learning algorithms, engineer predictive domain features, and evaluate a high-performing classification model.

---
## Pipeline Overview
1. **Raw & Messy Synthetic Data Generation**: Inject realistic missing values (MCAR/MAR), outliers, and inconsistent formatting.
2. **Advanced EDA & Data Cleaning**:
   - Statistical Imputation via **KNN Imputer** & Median.
   - Outlier Neutralization using the **Interquartile Range (IQR)** method.
3. **Feature Engineering**: Construct 4 new predictive financial risk metrics (`debt_to_income_ratio`, `loan_to_income_ratio`, `credit_utilization_ratio`, `financial_stress_index`).
4. **Clean Dataset Export**: Export `clean_dataset.csv`.
5. **Classification Model Training & Evaluation**: Train `RandomForestClassifier` and compute Accuracy, Classification Report, Confusion Matrix, and ROC-AUC curve.
"""))

# Cell 1: Imports
cells.append(nbf.v4.new_code_cell("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import KNNImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve
)
from sklearn.preprocessing import StandardScaler

# Set aesthetic styling
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Arial'
print("All libraries successfully imported.")"""))

# Section 1 Markdown
cells.append(nbf.v4.new_markdown_cell("""---
## Step 1: Synthetic Messy Data Generation & Initial EDA
We simulate a real-world customer credit dataset with missing values, skewed distributions, noisy strings, and extreme outliers."""))

# Cell 2: Data Generation
cells.append(nbf.v4.new_code_cell("""# Load messy dataset generated for analysis
df_raw = pd.read_csv('messy_dataset.csv')

print("--- Messy Dataset Overview ---")
print(f"Dataset Shape: {df_raw.shape}")
display(df_raw.head())

print("\\n--- Missing Value Count per Column ---")
print(df_raw.isnull().sum())

print("\\n--- Summary Statistics (Notice Extreme Outliers in age, income, credit_score) ---")
display(df_raw.describe())"""))

# Section 2 Markdown
cells.append(nbf.v4.new_markdown_cell("""---
## Step 2: Advanced Cleaning & Preprocessing
- **Categorical Cleaning**: Strip whitespace, standardize casing.
- **Outlier Neutralization (IQR & Domain Capping)**: Handle impossible values (e.g. negative ages or >100) and cap values outside $[Q1 - 1.5 \\times IQR, Q3 + 1.5 \\times IQR]$.
- **Statistical Imputation**: Use **KNN Imputer** (K-Nearest Neighbors) to impute missing numeric values based on feature similarities."""))

# Cell 3: Data Cleaning Implementation
cells.append(nbf.v4.new_code_cell("""df_clean = df_raw.copy()

# 1. Clean String Whitespace & Casing
df_clean['home_ownership'] = df_clean['home_ownership'].astype(str).str.strip().str.upper()
df_clean['home_ownership'] = df_clean['home_ownership'].replace({'NAN': np.nan})

# 2. Pre-cap Domain Violations
df_clean.loc[df_clean['age'] < 18, 'age'] = np.nan
df_clean.loc[df_clean['age'] > 100, 'age'] = np.nan
df_clean.loc[(df_clean['credit_score'] < 300) | (df_clean['credit_score'] > 850), 'credit_score'] = np.nan

# 3. Statistical Imputation via KNN Imputer
num_cols = ['age', 'annual_income', 'loan_amount', 'credit_score', 'total_debt', 'credit_card_balance', 'employment_years']
imputer = KNNImputer(n_neighbors=5)
df_clean[num_cols] = imputer.fit_transform(df_clean[num_cols])

# Impute categorical mode
df_clean['home_ownership'] = df_clean['home_ownership'].fillna(df_clean['home_ownership'].mode()[0])
df_clean['loan_intent'] = df_clean['loan_intent'].fillna(df_clean['loan_intent'].mode()[0])

# 4. Neutralize Outliers using IQR (Interquartile Range) Method
for col in num_cols:
    Q1 = df_clean[col].quantile(0.25)
    Q3 = df_clean[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df_clean[col] = np.clip(df_clean[col], lower_bound, upper_bound)

print("Imputation and IQR Outlier Neutralization Complete.")
print("Missing values after cleaning:")
print(df_clean.isnull().sum())"""))

# Section 3 Markdown
cells.append(nbf.v4.new_markdown_cell("""---
## Step 3: Predictive Feature Engineering
We engineer 4 brand-new domain predictive features to boost model predictive capacity:
1. `debt_to_income_ratio`: Total debt divided by annual income.
2. `loan_to_income_ratio`: Loan amount requested relative to annual income.
3. `credit_utilization_ratio`: Credit card balance relative to annual income.
4. `financial_stress_index`: Weighted financial burden composite metric."""))

# Cell 4: Feature Engineering
cells.append(nbf.v4.new_code_cell("""# 1. Debt-to-Income (DTI)
df_clean['debt_to_income_ratio'] = df_clean['total_debt'] / (df_clean['annual_income'] + 1)

# 2. Loan-to-Income (LTI)
df_clean['loan_to_income_ratio'] = df_clean['loan_amount'] / (df_clean['annual_income'] + 1)

# 3. Credit Utilization Ratio
df_clean['credit_utilization_ratio'] = df_clean['credit_card_balance'] / (df_clean['annual_income'] + 1)

# 4. Composite Financial Stress Index
df_clean['financial_stress_index'] = (
    (df_clean['debt_to_income_ratio'] * 0.4) + 
    (df_clean['loan_to_income_ratio'] * 0.4) - 
    ((df_clean['credit_score'] / 850.0) * 0.2)
)

# Export cleaned dataset to CSV
df_clean.to_csv('clean_dataset.csv', index=False)
print("Engineered 4 new features successfully!")
display(df_clean[['debt_to_income_ratio', 'loan_to_income_ratio', 'credit_utilization_ratio', 'financial_stress_index']].head())"""))

# Section 4 Markdown
cells.append(nbf.v4.new_markdown_cell("""---
## Step 4: Machine Learning Classification Model Training & Evaluation
We build a **Random Forest Classifier** to predict loan default status (`0` = Low Risk, `1` = Default Risk)."""))

# Cell 5: Model Training & Metrics
cells.append(nbf.v4.new_code_cell("""# Define features X and target y
X = df_clean.drop(columns=['customer_id', 'default_status'])
y = df_clean['default_status']

# One-Hot Encoding
X = pd.get_dummies(X, columns=['home_ownership', 'loan_intent'], drop_first=True)

# Train-Test Split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Classification Model
clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
clf.fit(X_train_scaled, y_train)

# Predictions & Probabilities
y_pred = clf.predict(X_test_scaled)
y_proba = clf.predict_proba(X_test_scaled)[:, 1]

# Calculate Evaluation Metrics
acc = accuracy_score(y_test, y_pred)
clf_rep = classification_report(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_proba)

# Print Metrics Output
print("==================================================")
print(f" ACCURACY SCORE: {acc * 100:.2f}%")
print("==================================================")
print("\\nCLASSIFICATION REPORT:")
print(clf_rep)
print("==================================================")
print("\\nCONFUSION MATRIX:")
print(cm)
print("==================================================")
print(f"\\nROC AUC SCORE: {roc_auc:.4f}")
print("==================================================")"""))

# Cell 6: Visualizations
cells.append(nbf.v4.new_code_cell("""# Plot Confusion Matrix and ROC Curve
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot Confusion Matrix Heatmap
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=axes[0],
            xticklabels=['Non-Default (0)', 'Default (1)'],
            yticklabels=['Non-Default (0)', 'Default (1)'])
axes[0].set_title('Confusion Matrix Heatmap', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Predicted Class', fontsize=12)
axes[0].set_ylabel('Actual Class', fontsize=12)

# Plot ROC-AUC Curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
axes[1].plot(fpr, tpr, color='darkblue', lw=2.5, label=f'Random Forest (AUC = {roc_auc:.3f})')
axes[1].plot([0, 1], [0, 1], color='gray', lw=1.5, linestyle='--')
axes[1].set_xlim([0.0, 1.0])
axes[1].set_ylim([0.0, 1.05])
axes[1].set_xlabel('False Positive Rate', fontsize=12)
axes[1].set_ylabel('True Positive Rate', fontsize=12)
axes[1].set_title('Receiver Operating Characteristic (ROC) Curve', fontsize=14, fontweight='bold')
axes[1].legend(loc="lower right", fontsize=11)

plt.tight_layout()
plt.show()"""))

# Cell 7: Feature Importance
cells.append(nbf.v4.new_code_cell("""# Plot Feature Importances to inspect engineered features
importances = clf.feature_importances_
feature_names = X.columns

feat_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values('Importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feat_df, palette='viridis')
plt.title('Random Forest Feature Importance (Engineered Features Included)', fontsize=14, fontweight='bold')
plt.xlabel('Importance Score', fontsize=12)
plt.ylabel('Feature', fontsize=12)
plt.tight_layout()
plt.show()"""))

nb['cells'] = cells

with open('project1_advanced_eda_ml.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Clean Jupyter Notebook saved as 'project1_advanced_eda_ml.ipynb'.")
