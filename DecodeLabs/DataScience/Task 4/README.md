# Project 4: NLP & Sentiment Analysis (IMDB Dataset)
**Decode Labs Internship — Data Science Task 4**

An end-to-end Natural Language Processing (NLP) and Machine Learning system to read, clean, mathematically represent, and categorize unstructured human movie reviews into **Positive** or **Negative** sentiment.

---

## 📁 Project Architecture

```
Task 4/
├── IMDB Dataset.csv              # 50,000 labeled movie reviews
├── requirements.txt              # Project dependencies
├── build_notebook.py             # Script generating sentiment_analysis.ipynb
├── sentiment_analysis.ipynb      # Main interactive, visually rich Jupyter Notebook
├── run_pipeline.py               # Standalone automated training & evaluation script
├── src/                          # Modular source codebase
│   ├── __init__.py
│   ├── preprocessor.py           # Strict text cleaning, tokenization, lemmatization
│   ├── feature_extraction.py     # TF-IDF mathematical vectorization module
│   ├── model.py                  # Naive Bayes, Linear SVM, Logistic Regression
│   └── utils.py                  # High-quality Matplotlib & Seaborn visualization tools
└── outputs/                      # Generated evaluation artifacts & saved models
    ├── models/
    │   ├── tfidf_vectorizer.joblib
    │   └── best_sentiment_model.joblib
    └── plots/
        ├── sentiment_distribution.png
        ├── wordclouds.png
        ├── confusion_matrices.png
        ├── roc_curves.png
        └── top_predictive_words.png
```

---

## 🛠️ Key Pipeline Components

1. **Strict Text Pre-Processing**:
   - Strips HTML markup (`<br />`) and web URLs.
   - Cleans punctuation and non-alphanumeric noise.
   - Preserves sentiment-critical negation words (`not`, `never`, `didn't`, `no`) while removing standard stopwords.
   - WordNet Lemmatization (transforms `movies` -> `movie`, `loving` -> `love`).

2. **TF-IDF Feature Extraction**:
   - Computes Term Frequency-Inverse Document Frequency matrices.
   - Extracts unigrams and bigrams (e.g., `"great movie"`, `"not good"`, `"waste time"`).

3. **Machine Learning Classifiers**:
   - **Multinomial Naive Bayes (`MultinomialNB`)**
   - **Linear Support Vector Machine (`LinearSVC`)**
   - **Logistic Regression**

4. **Model Performance Summary**:
   - **Linear SVM / Logistic Regression**: ~89.5% - 90.0% Accuracy & F1-Score (ROC-AUC > 0.95).
   - **Multinomial Naive Bayes**: ~86.5% Accuracy & F1-Score.

---

## 🚀 Quickstart & Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline Script
```bash
# Run on full 50,000 reviews dataset:
python run_pipeline.py

# Or run on a fast sample (e.g. 5,000 reviews):
python run_pipeline.py --sample 5000
```

### 3. Open the Jupyter Notebook
Launch Jupyter Notebook or VS Code to interactively step through the cells:
```bash
jupyter notebook sentiment_analysis.ipynb
```

---

## 💡 Real-Time Sentiment Prediction Example

```python
from src.preprocessor import TextPreprocessor
from src.feature_extraction import TextVectorizer
from src.model import SentimentModelTrainer

preprocessor = TextPreprocessor(preserve_negations=True)
vectorizer = TextVectorizer.load("outputs/models/tfidf_vectorizer.joblib")
model = SentimentModelTrainer.load_model("outputs/models/best_sentiment_model.joblib")

sample = "An absolute triumph of cinema! Incredible acting and poignant script."
cleaned = preprocessor.preprocess_text(sample)
vec = vectorizer.transform([cleaned])
prediction = model.predict(vec)[0]

print("Predicted Sentiment:", "POSITIVE" if prediction == 1 else "NEGATIVE")
```
