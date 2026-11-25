import os
import sys
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from src.preprocessor import TextPreprocessor
from src.feature_extraction import TextVectorizer
from src.model import SentimentModelTrainer
from src.utils import (
    plot_sentiment_distribution,
    plot_wordclouds,
    plot_confusion_matrices,
    plot_roc_curves,
    plot_top_features
)


def run_pipeline(data_path="IMDB Dataset.csv", sample_size=None, output_dir="outputs"):
    """
    Executes the entire NLP sentiment analysis pipeline:
    1. Loads dataset
    2. Runs text preprocessing (Tokenization, Stopwords, Lemmatization)
    3. Transforms text to TF-IDF feature matrices
    4. Trains Naive Bayes, Linear SVM, Logistic Regression
    5. Saves plots, evaluation metrics, and best serialized model
    """
    os.makedirs(output_dir, exist_ok=True)
    plots_dir = os.path.join(output_dir, "plots")
    models_dir = os.path.join(output_dir, "models")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    print("=" * 70)
    print("      NLP & SENTIMENT ANALYSIS PIPELINE (IMDB DATASET)")
    print("=" * 70)

    # 1. Load Data
    print(f"\n[1/5] Loading data from '{data_path}'...")
    df = pd.read_csv(data_path)
    print(f"      Total records loaded: {len(df):,}")

    if sample_size and sample_size < len(df):
        print(f"      Sampling {sample_size:,} rows for rapid execution...")
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)

    # Map sentiment to binary integers (positive -> 1, negative -> 0)
    df['target'] = df['sentiment'].map({'positive': 1, 'negative': 0})

    # Plot Sentiment Distribution
    print("      Saving Sentiment Distribution plot...")
    plot_sentiment_distribution(df, save_path=os.path.join(plots_dir, "sentiment_distribution.png"))

    # 2. Text Preprocessing Pipeline
    print("\n[2/5] Running Text Preprocessing (Cleaning, Stop-Words, Lemmatization)...")
    preprocessor = TextPreprocessor(preserve_negations=True)
    df['cleaned_review'] = preprocessor.transform_series(df['review'])
    print(f"      Example original:\n        \"{df['review'].iloc[0][:120]}...\"")
    print(f"      Example cleaned:\n        \"{df['cleaned_review'].iloc[0][:120]}...\"")

    # Word Cloud generation
    print("      Generating Word Clouds (Positive vs Negative)...")
    pos_text = " ".join(df[df['target'] == 1]['cleaned_review'])
    neg_text = " ".join(df[df['target'] == 0]['cleaned_review'])
    plot_wordclouds(pos_text, neg_text, save_path=os.path.join(plots_dir, "wordclouds.png"))

    # 3. Train / Test Split and TF-IDF Feature Extraction
    print("\n[3/5] Vectorizing Text with TF-IDF (Unigrams + Bigrams)...")
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        df['cleaned_review'], df['target'], test_size=0.2, random_state=42, stratify=df['target']
    )

    vectorizer = TextVectorizer(max_features=15000, ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)

    print(f"      Training shape: {X_train.shape} | Test shape: {X_test.shape}")
    # Save vectorizer
    vectorizer.save(os.path.join(models_dir, "tfidf_vectorizer.joblib"))

    # 4. Model Training & Benchmarking
    print("\n[4/5] Training Classifiers (Naive Bayes, Linear SVM, Logistic Regression)...")
    trainer = SentimentModelTrainer()
    results = trainer.train_and_evaluate(X_train, y_train, X_test, y_test)

    # Save Plots
    print("      Generating Confusion Matrices and ROC Curves...")
    plot_confusion_matrices(results, save_path=os.path.join(plots_dir, "confusion_matrices.png"))
    plot_roc_curves(results, y_test, save_path=os.path.join(plots_dir, "roc_curves.png"))

    # Save Best Model
    best_name, best_model = trainer.get_best_model(metric="F1-Score")
    print(f"\n      >>> Best Performing Model: {best_name} (F1 = {results[best_name]['F1-Score']:.4f})")
    trainer.save_model(best_name, os.path.join(models_dir, "best_sentiment_model.joblib"))

    # Feature Importance Plot
    if "Linear SVM (LinearSVC)" in trainer.trained_models:
        plot_top_features(
            trainer.trained_models["Linear SVM (LinearSVC)"],
            vectorizer.vectorizer,
            top_n=20,
            save_path=os.path.join(plots_dir, "top_predictive_words.png")
        )

    # 5. Live Inference Demonstration
    print("\n[5/5] Demonstrating Inference on New Custom Reviews:")
    test_samples = [
        "This movie was an absolute masterpiece! Captivating storyline and stellar acting.",
        "A complete waste of time. Terrible script, boring characters, and horrible pacing.",
        "Surprisingly good! I did not expect to like it, but the twist at the end was brilliant.",
        "It was mediocre at best. Not the worst film, but certainly not worth the ticket price."
    ]

    for sample in test_samples:
        cleaned = preprocessor.preprocess_text(sample)
        vec = vectorizer.transform([cleaned])
        pred = best_model.predict(vec)[0]
        sentiment_str = "POSITIVE (+)" if pred == 1 else "NEGATIVE (-)"
        print(f"\n      Review: \"{sample}\"")
        print(f"      -> Predicted: {sentiment_str}")

    print("\n" + "=" * 70)
    print(f"Pipeline executed successfully! Artifacts saved to '{output_dir}/'")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Sentiment Analysis NLP Pipeline")
    parser.add_argument("--data", type=str, default="IMDB Dataset.csv", help="Path to IMDB dataset CSV")
    parser.add_argument("--sample", type=int, default=None, help="Optional sample size for fast testing")
    args = parser.parse_args()

    run_pipeline(data_path=args.data, sample_size=args.sample)
