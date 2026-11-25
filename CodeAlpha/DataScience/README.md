# 📊 CodeAlpha Data Science Internship — Project Portfolio

Welcome to my portfolio for the **Data Science Internship at CodeAlpha** (Module 1). This repository contains the complete implementation, exploratory analysis, predictive modeling, and business evaluation of the four assigned tasks. Each project has been structured as a production-grade data science workflow—ranging from exploratory analysis and visual reporting to feature engineering, hyperparameter tuning, model serialization, and policy/strategic recommendations.

---

## 📂 Repository Structure

Below is the directory layout of the workspace, showing datasets, codebases, saved models, and key visualization output directories.

```text
Data Science/
│
├── Data Science Tasks & Instructions — CodeAlpha M1.pdf   # Official Internship Guidelines
│
├── Task1/                                                 # TASK 1: Iris Flower Classification
│   ├── Iris.csv                                           # Dataset
│   ├── Task1.ipynb                                        # Analysis & Modeling Pipeline
│   ├── auc_roc_curve.png                                  # One-vs-Rest AUC-ROC Plot
│   └── confusion_matrix.png                               # Multiclass Confusion Matrix Heatmap
│
├── Task2/                                                 # TASK 2: Unemployment Analysis in India
│   ├── Unemployment_in_India.csv                          # Dataset 1 (Region, Area, Date, LPR)
│   ├── Unemployment_Rate_upto_11_2020.csv                 # Dataset 2 (COVID period specific)
│   ├── Task2.ipynb                                        # Cleaning, Visualization & Policy Notebook
│   ├── fig1_national_trend.png                            # National Unemployment Trend
│   ├── fig2_state_analysis.png                            # State-wise Average Unemployment
│   ├── fig3_urban_vs_rural.png                            # Urban vs Rural Contrast
│   ├── fig4_seasonal_heatmap.png                          # Seasonal Heatmap of Unemployment
│   ├── fig5_distribution_comparison.png                   # Distribution plots of key variables
│   ├── fig6_correlation.png                               # Correlation Heatmap
│   └── fig7_top10_peak_covid.png                          # Worst Hit States during Peak Covid
│
├── Task3/                                                 # TASK 3: Car Price Prediction
│   ├── cardata.csv                                        # Car Features Dataset
│   ├── Task3.ipynb                                        # Regression Comparison & Tuning Pipeline
│   ├── car_price_model.pkl                                # Serialized Inference Pipeline
│   ├── eda_overview.png                                   # EDA Distributions & Scatter plots
│   ├── correlation_heatmap.png                            # Feature Correlations Heatmap
│   └── model_evaluation.png                               # Actual vs Predicted & Residuals
│
└── Task4/                                                 # TASK 4: Sales Prediction
    ├── Advertising.csv                                    # Marketing Spend vs Sales Dataset
    ├── Task4.ipynb                                        # Modeling & Impact Analysis Pipeline
    └── outputs/                                           # Saved Visualizations
        ├── 01_correlation_heatmap.png
        ├── 02_spend_vs_sales.png
        ├── 03_sales_distribution.png
        ├── 04_actual_vs_predicted.png
        ├── 05_residuals.png
        └── 06_feature_impact.png
```

---

## 🛠️ Installation & Setup

To run these projects locally, follow the steps below:

### 1. Prerequisites
Ensure you have Python (version 3.9 to 3.12 is recommended) installed.

### 2. Clone the Repository
```bash
git clone https://github.com/YourUsername/CodeAlpha_ProjectName.git
cd CodeAlpha_ProjectName
```

### 3. Install Dependencies
Install all the required standard scientific computation, machine learning, and visualization packages:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn joblib
```

### 4. Running the Notebooks
Launch Jupyter Notebook or JupyterLab to interact with and run the `.ipynb` files:
```bash
jupyter notebook
```

---

## 🔬 Detailed Task Implementation & Results

---

### 🌸 Task 1: Iris Flower Classification
* **Objective:** Build a machine learning model to classify Iris flowers into their correct species (`setosa`, `versicolor`, `virginica`) based on sepal and petal measurements (length & width).
* **Dataset:** [Iris.csv](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task1/Iris.csv) (150 samples, 4 features: `SepalLengthCm`, `SepalWidthCm`, `PetalLengthCm`, `PetalWidthCm`, and the target label `Species`).

#### Technical Workflow
1. **Data Preprocessing & Splitting:** Dropped unnecessary indices, encoded string labels (`LabelEncoder`), and split features using a stratified train/test split (80/20 ratio) to preserve class balance.
2. **Model Training:** Fit a **Random Forest Classifier** (`n_estimators=100`, `random_state=42`) on the training set.
3. **Model Evaluation:** Evaluated on the test set utilizing accuracy, a detailed classification report (precision, recall, f1-score), and a confusion matrix.

#### 📈 Results & Visualizations
* **Final Test Set Accuracy:** **90.00%**
* **Classification Report:**
  * `Iris-setosa`: **1.00** Precision | **1.00** Recall | **1.00** F1-Score
  * `Iris-versicolor`: **0.82** Precision | **0.90** Recall | **0.86** F1-Score
  * `Iris-virginica`: **0.89** Precision | **0.80** Recall | **0.84** F1-Score
* **Key Graphics Generated:**
  * **[confusion_matrix.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task1/confusion_matrix.png):** Visualizes the correct vs incorrect classifications across all three categories.
  * **[auc_roc_curve.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task1/auc_roc_curve.png):** Multi-class One-vs-Rest ROC curve showing near-perfect discrimination metrics (AUC of 1.000 for Setosa, 0.965 for Versicolor, and 0.965 for Virginica).

---

### 📈 Task 2: Unemployment Analysis in India (with COVID-19 Impact)
* **Objective:** Load, clean, merge, and visualize historical unemployment rate datasets from India to analyze seasonal trends, state-wise variances, urban-rural divides, and the direct impact of the COVID-19 lockdown.
* **Datasets:** [Unemployment_in_India.csv](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/Unemployment_in_India.csv) & [Unemployment_Rate_upto_11_2020.csv](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/Unemployment_Rate_upto_11_2020.csv).

#### Technical Workflow
1. **Data Integration:** Cleaned whitespaces, standardized date formats, handled missing rows, and merged files to create a cohesive longitudinal dataset of 1,007 rows representing 28 States and Union Territories.
2. **Impact Partitioning:** Created a binary categorical variable to split observations into **Pre-COVID** (before March 2020) vs. **COVID-19 Period** (March 2020 onwards).
3. **Exploratory Visualizations:** Produced 7 analytical charts using Seaborn and Matplotlib to highlight national trends, regional divides, and distributions.

#### 💡 Key Data Insights & Recommendations
* **COVID-19 Shift:** Pre-COVID national average unemployment was **9.48%**, which surged to **15.31%** during the COVID-19 window (an absolute increase of **+5.82%** / **+61.4%** relative increase).
* **The Urban Divide:** Average Urban unemployment was **13.17%** compared to **10.32%** in Rural regions, showing a clear **+2.84 pp** gap due to severe urban service sector disruptions.
* **Worst Affected Areas:** Puducherry saw a peak COVID unemployment spike to **76.7%**, while Tripura averaged the highest overall unemployment at **27.5%**.

#### 📋 Actionable Policy Recommendations
1. **Targeted Urban Economic Support:** Because urban regions saw sharper spikes and slower recovery during lockdown, policy interventions (e.g., job re-skilling, local MSME credit lines) must focus heavily on urban centers.
2. **Infrastructure Investment in High-Risk States:** Consistently high baseline unemployment in Tripura, Bihar, and Jharkhand calls for long-term industrialization and infrastructure stimulus.
3. **Extend Safety Nets to Peri-Urban Areas:** The MGNREGS rural job guarantee scheme provided a vital buffer. A similar urban employment guarantee scheme should be formulated.
4. **Counteract Seasonal Volatility:** The seasonal heatmap points to a persistent spike in unemployment around March–May. Pre-emptive public works projects or vocational training schedules could help smooth this seasonal spike.

#### 🎨 Generated Figures
* **[fig1_national_trend.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/fig1_national_trend.png):** Historical timeline of Indian unemployment showing the April 2020 peak.
* **[fig2_state_analysis.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/fig2_state_analysis.png):** Mean unemployment rate ranked across all 28 states/UTs.
* **[fig3_urban_vs_rural.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/fig3_urban_vs_rural.png):** Side-by-side violin/box plots highlighting the urban-rural divide.
* **[fig4_seasonal_heatmap.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/fig4_seasonal_heatmap.png):** Monthly trends illustrating seasonal peaks in early spring.
* **[fig5_distribution_comparison.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/fig5_distribution_comparison.png):** Comparison of key economic metric distributions.
* **[fig6_correlation.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/fig6_correlation.png):** Multi-variable economic correlation matrix.
* **[fig7_top10_peak_covid.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task2/fig7_top10_peak_covid.png):** States with the highest peak monthly rates during lockdown.

---

### 🚗 Task 3: Car Price Prediction with Machine Learning
* **Objective:** Create a machine learning regression pipeline to predict the selling price of used cars based on odometer mileage, brand goodwill, age, present showroom value, transmission, fuel type, and ownership history.
* **Dataset:** [cardata.csv](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task3/cardata.csv) (301 records, 9 features).

#### Technical Workflow
1. **Feature Engineering:**
   * `Car_Age`: Age of the car relative to the current year.
   * `Km_Per_Year`: Ratio of `Driven_kms` to `Car_Age` (helps quantify usage intensity).
   * `Price_Ratio`: Showroom value adjusted for car age.
2. **Preprocessing Pipeline (`ColumnTransformer`):**
   * Numeric values scaled using `StandardScaler`.
   * High-cardinality categorical values (`Car_Name`) encoded using `TargetEncoder` (representing brand/model market goodwill).
   * Low-cardinality categoricals (`Fuel_Type`, `Selling_type`, `Transmission`) encoded via `OneHotEncoder`.
3. **Model Selection (5-Fold Cross-Validation):** Evaluated four candidates: Linear Regression, Ridge, Random Forest, and Gradient Boosting.
4. **Final Model Evaluation:** Tested the best-performing model on a held-out validation set (20%).

#### 📈 Results & Visualizations
* **Best Cross-Validation Model:** **Linear Regression** (Mean CV $R^2 = 0.9572$).
* **Final Test Set Metrics:**
  * **$R^2$ Score:** **0.9643** (Explains 96.4% of the variance in selling price)
  * **Mean Absolute Error (MAE):** **0.618 lakhs** (~$740 USD equivalent)
  * **Root Mean Squared Error (RMSE):** **0.907 lakhs**
  * **Mean Absolute Percentage Error (MAPE):** **25.50%**
* **Key Outputs:**
  * **[car_price_model.pkl](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task3/car_price_model.pkl):** Fully serialized pipeline ready for inference deployments.
  * **[model_evaluation.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task3/model_evaluation.png):** Contains the "Actual vs. Predicted Price" scatter plot and "Residuals Distribution" histogram.

---

### 📺 Task 4: Sales Prediction using Python
* **Objective:** Analyze and predict future sales based on marketing budgets across multiple platforms (TV, Radio, Newspaper). Engineer categorical segments and model advertising returns using regression techniques.
* **Dataset:** [Advertising.csv](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task4/Advertising.csv) (200 marketing campaigns).

#### Technical Workflow
1. **Feature Engineering:**
   * `Total_Spend`: Sum of advertising dollars across TV, Radio, and Newspaper.
   * `Tv_Share`, `Radio_Share`, `Newspaper_Share`: Relative budget share per channel.
   * `Primary_Platform`: Engineered category marking the channel receiving the highest spend share for a campaign (one-hot encoded for modeling).
2. **Modeling:** Standardized features and compared Linear Regression vs. a **Random Forest Regressor** (300 estimators).
3. **Budget Scenario Simulation:** Built a "what-if" predictor function to forecast marginal sales returns on a +10% budget increase across specific channels.

#### 📈 Results & Evaluation
* **Model Comparison:**
  * *Linear Regression:* $R^2 = 0.9279$, $RMSE = 1.509$
  * *Random Forest:* $R^2 = 0.9598$, $RMSE = 1.126$ (Winner)
* **What-If Scenario Simulation (Example):**
  * Base sales prediction: **14.95** units.
  * **+10% TV Spend** -> Sales Change: **+0.296 units**
  * **+10% Radio Spend** -> Sales Change: **+0.150 units**
  * **+10% Newspaper Spend** -> Sales Change: **+0.135 units**

#### 📋 Actionable Business Insights
1. **High Model Explanatory Power:** The Random Forest Model explains **96.0%** of sales variance, providing a highly reliable simulator for marketing spend optimization.
2. **TV is the Anchor Channel:** TV spend remains the strongest positive driver of absolute sales and should serve as the baseline anchor of all multi-channel campaigns.
3. **Radio yields strong marginal efficiency:** Radio spend is highly effective as a secondary channel, showing high efficiency relative to its lower cost per unit.
4. **De-prioritize Newspaper Campaigns:** Newspaper advertising is the weakest predictor of Sales. Unless targeting specific niche print demographics, this budget should be reallocated to TV/Radio.
5. **Optimize for Diminishing Returns:** Sales scale with total spend, but show diminishing returns at higher budget caps. Marketing teams should test budget ceilings rather than scaling channels linearly.

#### 🎨 Outputs (Saved in `Task4/outputs/`)
* **[01_correlation_heatmap.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task4/outputs/01_correlation_heatmap.png):** Feature correlation map highlighting the strong connection between TV/Radio and Sales.
* **[02_spend_vs_sales.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task4/outputs/02_spend_vs_sales.png):** Linear regressions of individual channels vs. sales.
* **[04_actual_vs_predicted.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task4/outputs/04_actual_vs_predicted.png):** Actual vs. Predicted fit comparison for the Random Forest model.
* **[06_feature_impact.png](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/Data%20Science/Task4/outputs/06_feature_impact.png):** Side-by-side chart displaying Linear Regression coefficients vs. Random Forest feature importance.

---

## 👥 Author
Developed during the **CodeAlpha Data Science Internship** program.
* **Contact Email:** [services@codealpha.tech](mailto:services@codealpha.tech)
* **Official Website:** [www.codealpha.tech](http://www.codealpha.tech)
