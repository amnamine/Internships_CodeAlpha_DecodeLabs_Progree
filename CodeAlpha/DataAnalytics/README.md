# CodeAlpha Data Analytics Internship Portfolio

Welcome to the **Data Analytics Internship Portfolio** repository, completed as part of the CodeAlpha Data Analytics Internship program. This repository contains four comprehensive projects covering the entire lifecycle of data analysis: from robust web scraping and automated extraction to explorative data analysis (EDA), interactive dashboard visualization, and advanced NLP sentiment/emotion classification.

---

## 📂 Project Structure

Below is the file structure of the repository, including direct links to primary components and scripts:

```text
DataAnalytics/
├── Data Analytics Tasks & Instructions — CodeAlpha M1.pdf   # Official Internship Guidelines
├── Task 1/                                                 # Task 1: Web Scraping Pipeline
│   ├── main.py                                             # CLI Scraper entry point
│   ├── analyzer.py                                         # Text report & chart generator
│   ├── requirements.txt                                    # Scraper dependencies
│   ├── scraper/                                            # Core crawler classes
│   │   ├── client.py                                       # Resilient HTTP Client
│   │   ├── parser.py                                       # HTML Content Parser
│   │   └── pipeline.py                                     # Scraper Orchestration
│   ├── data/                                               # Scraped raw data output
│   └── exports/                                            # Analytical outputs & charts
│
├── Task 2/                                                 # Task 2: Exploratory Data Analysis (EDA)
│   ├── Mall_Customers.csv                                  # Mall Customers demographic dataset
│   └── eda_mall_customers.ipynb                            # Complete EDA Jupyter Notebook
│
├── Task 3/                                                 # Task 3: Interactive Visualization Dashboard
│   ├── dashboard.py                                        # Streamlit & Plotly Dashboard Application
│   ├── Mall_Customers.csv                                  # Mall Customers dataset (duplicated for Task 3)
│   ├── visualize_mall_customers.ipynb                      # Visualization analysis Notebook
│   └── build_notebook.py                                   # Helper script for Jupyter export
│
└── Task 4/                                                 # Task 4: Sentiment & Emotion Analysis
    ├── sentiment_analysis.py                               # NLP preprocessor & modeling pipeline
    ├── sentiment_analysis.ipynb                            # Sentiment analysis Notebook
    ├── train.csv                                           # Training tweets dataset
    ├── test.csv                                            # Test tweets dataset
    ├── model_evaluation.txt                                # Performance metrics report
    └── plots/                                              # Visualizations for sentiment/emotion
```

---

## 🛠️ Project Summaries & Implementation Details

### 1. [Task 1: Web Scraping & Data Analysis Pipeline](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%201)
A production-grade web scraping and automated data analytics pipeline targeting [Books to Scrape](http://books.toscrape.com/). It crawls catalog indices, traverses pagination, parses individual product detail pages, cleans the resulting dataset, and performs statistical analysis.
- **Key Features**:
  - **Resiliency & Politeness**: Utilizes a custom client with automatic retries via `urllib3.util.Retry` to recover from temporary server errors (e.g., 500, 502, 503, 504), implements rate-limiting delays to respect target server bandwidth, and rotates User-Agent headers.
  - **Comprehensive Parser**: Leverages `BeautifulSoup` to parse complex HTML patterns to extract details like Title, UPC, Price, Category, Availability, and Star Rating.
  - **Data Cleaning & Analysis**: Automated pipeline cleans currency symbols, string formats, and missing values, producing an analytical text report and publication-quality Seaborn charts.
- **Key Files**:
  - Entry point: [main.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%201/main.py)
  - Parser: [parser.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%201/scraper/parser.py)
  - Resilient Client: [client.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%201/scraper/client.py)
  - Analyzer: [analyzer.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%201/analyzer.py)

---

### 2. [Task 2: Exploratory Data Analysis (EDA)](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%202)
A detailed exploratory analysis of the **Mall Customers** demographic dataset (`Mall_Customers.csv`). The objective is to understand the variables, spot trends, identify customer demographics, and establish statistical foundations for customer segmentation.
- **Key Features**:
  - **Descriptive Statistics**: Detailed profiles of customer metrics (Age, Annual Income, Spending Score).
  - **Distribution Analysis**: Density plots, box plots, and histograms comparing demographics (such as Age and Income distributions) sliced by Gender.
  - **Correlation Analysis**: Explores relationships between variables through correlation matrices, scatter plots, and pair plots.
  - **K-Means Clustering Foundations**: Investigates optimal cluster numbers using the Elbow Method and Silhouette Analysis.
- **Key Files**:
  - EDA Notebook: [eda_mall_customers.ipynb](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%202/eda_mall_customers.ipynb)
  - Source Data: [Mall_Customers.csv](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%202/Mall_Customers.csv)

---

### 3. [Task 3: Interactive Data Visualization Dashboard](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%203)
A premium, interactive customer segmentation dashboard built with **Streamlit** and **Plotly**. It visualizes customer categories, applies real-time unsupervised K-Means clustering, and enables marketers to drill down into customer segments.
- **Key Features**:
  - **Interactive Filtering**: Dynamic sidebar allowing users to filter dashboards by Gender, Age range, and Annual Income range.
  - **Real-Time K-Means Clustering**: Automatically categorizes customers into 5 distinct groups:
    - *Target Group*: High Income, High Spending
    - *Savers*: High Income, Low Spending
    - *Average*: Medium Income, Medium Spending
    - *Careless*: Low Income, High Spending
    - *Sensible*: Low Income, Low Spending
  - **Rich Visualization Cards**: Displays key metrics (e.g., total customers, average spending score) alongside Plotly charts, 3D scatter plots, distribution graphs, and correlation heatmaps.
- **Key Files**:
  - Streamlit App: [dashboard.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%203/dashboard.py)
  - Analytics Notebook: [visualize_mall_customers.ipynb](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%203/visualize_mall_customers.ipynb)

---

### 4. [Task 4: Sentiment & Emotion Analysis](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%204)
A dual-approach NLP model classifying tweet sentiments (positive, neutral, negative) and mapping dominant emotional states (joy, sadness, anger, fear, surprise) using tweet corpus datasets.
- **Key Features**:
  - **Text Preprocessing**: Robust cleaning pipeline removing URLs, HTML tags, special symbols, and applying NLTK word tokenization and lemmatization.
  - **Emotion Lexicon Classifier**: A rule-based keyword mapping algorithm detecting secondary sentiment layers (e.g., joy, anger, fear) from an emotional lexicon.
  - **Supervised Sentiment Model**: Trains a TF-IDF vectorizer + Logistic Regression classifier.
  - **Hybrid Comparison**: Compares the custom supervised ML model to the lexicon-based VADER algorithm.
- **Model Evaluation Highlights** (stored in [model_evaluation.txt](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%204/model_evaluation.txt)):
  - **Logistic Regression Model**: **70.6% Accuracy**
  - **Lexicon-based (VADER) Model**: **64.8% Accuracy**
- **Key Files**:
  - Pipeline Script: [sentiment_analysis.py](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%204/sentiment_analysis.py)
  - Training Data: [train.csv](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%204/train.csv)
  - Evaluation Report: [model_evaluation.txt](file:///d:/AMINE2/COURS%20FAC/travaux/CodeAlpha_INTERNSHIP/DataAnalytics/Task%204/model_evaluation.txt)

---

## 🚀 Installation & Getting Started

### Prerequisites
- Python 3.10+
- Pip package manager

### Environment Setup
1. Clone this repository to your local machine.
2. Open your terminal at the root of the project.
3. Install dependencies for each task as needed. 

### Running Individual Tasks

#### Task 1: Web Scraper
```bash
cd "Task 1"
pip install -r requirements.txt

# Run with a 30-book limit to test correctness quickly
python main.py --limit-books 30

# Run a full scrape (all 1000 books)
python main.py
```

#### Task 2: Jupyter Notebook EDA
```bash
cd "Task 2"
pip install jupyter pandas numpy matplotlib seaborn scipy
jupyter notebook eda_mall_customers.ipynb
```

#### Task 3: Interactive Dashboard
```bash
cd "Task 3"
pip install streamlit pandas plotly scikit-learn
streamlit run dashboard.py
```

#### Task 4: Sentiment & Emotion Analysis
```bash
cd "Task 4"
pip install pandas numpy matplotlib seaborn nltk scikit-learn
python sentiment_analysis.py
```

---

## 🛠️ Technologies Used
- **Data Engineering & Crawling**: `BeautifulSoup4`, `urllib3`, `requests`
- **Exploratory Analytics & ML**: `pandas`, `numpy`, `scikit-learn` (`KMeans`, `LogisticRegression`, `TfidfVectorizer`)
- **NLP / Text Mining**: `nltk` (tokenization, wordnet lemmatization, VADER lexicon), regular expressions (`re`)
- **Visualizations**: `matplotlib`, `seaborn`, `plotly`
- **Dashboard Interfaces**: `streamlit`
