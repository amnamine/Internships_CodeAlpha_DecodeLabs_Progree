import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Setup matplotlib style for premium look
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16
})

# Color palette definition (sleek, curated)
PALETTE = {
    'positive': '#2ec4b6',
    'neutral': '#ffbf00',
    'negative': '#e71d36',
    'joy': '#ff9f1c',
    'sadness': '#4361ee',
    'anger': '#d90429',
    'fear': '#7209b7',
    'surprise': '#4cc9f0',
    'neutral_emotion': '#8d99ae'
}

def download_nltk_resources():
    """Ensure all required NLTK resources are available locally."""
    print("Downloading NLTK resources...")
    for resource in ['stopwords', 'punkt', 'punkt_tab', 'wordnet', 'vader_lexicon']:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            print(f"Error downloading {resource}: {e}")

def clean_text(text):
    """Clean tweet text by removing URLs, HTML tags, and non-alphabetic characters."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE) # Remove URLs
    text = re.sub(r"<.*?>", "", text) # Remove HTML tags
    text = re.sub(r"[^a-zA-Z\s]", "", text) # Remove special characters & numbers
    text = re.sub(r"\s+", " ", text).strip() # Remove extra whitespace
    return text

# Predefined emotion lexicon mapping
EMOTION_LEXICON = {
    'joy': {'happy', 'joy', 'love', 'wonderful', 'amazing', 'great', 'awesome', 'glad', 'excited', 'smile', 'laugh', 'good', 'cool', 'nice', 'pleasant', 'delight', 'cheerful', 'fun', 'happy', 'party', 'enjoy'},
    'sadness': {'sad', 'depressed', 'cry', 'grief', 'sorrow', 'unhappy', 'lonely', 'miss', 'hurt', 'pain', 'tear', 'gloomy', 'disappointed', 'sorry', 'disappointment', 'bad', 'crying', 'hate', 'broke'},
    'anger': {'angry', 'rage', 'hate', 'furious', 'mad', 'annoyed', 'pissed', 'irritated', 'disgust', 'hate', 'frustrated', 'bullying', 'bully', 'mean', 'offensive', 'hate', 'stupid', 'sucks', 'hell'},
    'fear': {'scared', 'fear', 'afraid', 'terrified', 'worry', 'anxious', 'dread', 'frightened', 'panic', 'nervous', 'horror', 'scary', 'worrying'},
    'surprise': {'surprise', 'shock', 'wonder', 'amazed', 'unexpected', 'sudden', 'unbelievable', 'wow', 'gasp', 'omg', 'incredible'}
}

def detect_emotion(text, lemmatizer, stop_words):
    """Detect dominant emotion in a text using simple keyword/lexicon mapping."""
    tokens = word_tokenize(text.lower())
    words = [lemmatizer.lemmatize(word) for word in tokens if word.isalpha() and word not in stop_words]
    
    emotion_counts = {emotion: 0 for emotion in EMOTION_LEXICON}
    for word in words:
        for emotion, keyword_set in EMOTION_LEXICON.items():
            if word in keyword_set:
                emotion_counts[emotion] += 1
                
    max_emotion = max(emotion_counts, key=emotion_counts.get)
    if emotion_counts[max_emotion] == 0:
        return 'neutral/others'
    return max_emotion

def main():
    download_nltk_resources()
    
    # Paths
    train_path = "train.csv"
    test_path = "test.csv"
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading datasets...")
    train_df = pd.read_csv(train_path, encoding='latin1')
    test_df = pd.read_csv(test_path, encoding='latin1')
    
    print(f"Train dataset size: {train_df.shape}")
    print(f"Test dataset size: {test_df.shape}")
    
    # Drop rows where text is missing
    train_df = train_df.dropna(subset=['text'])
    test_df = test_df.dropna(subset=['text'])
    
    # Clean text columns
    print("Cleaning text data...")
    train_df['cleaned_text'] = train_df['text'].apply(clean_text)
    test_df['cleaned_text'] = test_df['text'].apply(clean_text)
    
    # ------------------ 1. Sentiment Distribution Plot ------------------
    plt.figure(figsize=(10, 5))
    train_dist = train_df['sentiment'].value_counts(normalize=True)
    test_dist = test_df['sentiment'].value_counts(normalize=True)
    
    dist_df = pd.DataFrame({
        'Train': train_dist,
        'Test': test_dist
    }).reset_index().rename(columns={'index': 'Sentiment'})
    
    dist_melt = pd.melt(dist_df, id_vars='sentiment', value_vars=['Train', 'Test'], 
                        var_name='Dataset', value_name='Proportion')
    
    sns.barplot(data=dist_melt, x='sentiment', y='Proportion', hue='Dataset', 
                palette={'Train': '#1d3557', 'Test': '#457b9d'})
    plt.title("Sentiment Label Distribution (Train vs Test)")
    plt.ylabel("Proportion")
    plt.xlabel("Sentiment Class")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sentiment_distribution.png'), dpi=300)
    plt.close()
    
    # ------------------ 2. Supervised ML Model (TF-IDF + Logistic Regression) ------------------
    print("Training Supervised ML Model...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(train_df['cleaned_text'])
    y_train = train_df['sentiment']
    
    X_test = vectorizer.transform(test_df['cleaned_text'])
    y_test = test_df['sentiment']
    
    model = LogisticRegression(max_iter=1000, C=1.0)
    model.fit(X_train, y_train)
    y_pred_ml = model.predict(X_test)
    
    print("\n=== Supervised ML Model (Logistic Regression) Classification Report ===")
    ml_report = classification_report(y_test, y_pred_ml)
    print(ml_report)
    
    # Save ML metrics to file
    with open("model_evaluation.txt", "w", encoding="utf-8") as f:
        f.write("=== Supervised ML Model (Logistic Regression) ===\n")
        f.write(f"Accuracy: {accuracy_score(y_test, y_pred_ml):.4f}\n")
        f.write(ml_report)
        f.write("\n")
        
    # ------------------ 3. Lexicon-based Model (VADER) ------------------
    print("Running VADER Sentiment Analysis...")
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    
    def get_vader_sentiment(text):
        score = sia.polarity_scores(text)['compound']
        if score >= 0.05:
            return 'positive'
        elif score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
            
    # Calculate VADER sentiment and scores on test set
    test_df['vader_sentiment'] = test_df['text'].apply(get_vader_sentiment)
    test_df['vader_compound'] = test_df['text'].apply(lambda x: sia.polarity_scores(x)['compound'])
    
    print("\n=== Lexicon-based Model (VADER) Classification Report ===")
    vader_report = classification_report(y_test, test_df['vader_sentiment'])
    print(vader_report)
    
    with open("model_evaluation.txt", "a", encoding="utf-8") as f:
        f.write("=== Lexicon-based Model (VADER) ===\n")
        f.write(f"Accuracy: {accuracy_score(y_test, test_df['vader_sentiment']):.4f}\n")
        f.write(vader_report)
        f.write("\n")
        
    # ------------------ Plotting Confusion Matrices ------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    classes = ['negative', 'neutral', 'positive']
    
    cm_ml = confusion_matrix(y_test, y_pred_ml, labels=classes)
    sns.heatmap(cm_ml, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, ax=axes[0])
    axes[0].set_title("Supervised Logistic Regression CM")
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("True")
    
    cm_vader = confusion_matrix(y_test, test_df['vader_sentiment'], labels=classes)
    sns.heatmap(cm_vader, annot=True, fmt='d', cmap='Purples', xticklabels=classes, yticklabels=classes, ax=axes[1])
    axes[1].set_title("Lexicon-based VADER CM")
    axes[1].set_xlabel("Predicted")
    axes[1].set_ylabel("True")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ml_vs_vader_confusion.png'), dpi=300)
    plt.close()
    
    # ------------------ 4. Emotion Detection ------------------
    print("Detecting Emotions...")
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    test_df['emotion'] = test_df['cleaned_text'].apply(lambda x: detect_emotion(x, lemmatizer, stop_words))
    
    plt.figure(figsize=(10, 5))
    emotion_counts = test_df['emotion'].value_counts().reset_index()
    emotion_counts.columns = ['Emotion', 'Count']
    
    color_map = {
        'joy': PALETTE['joy'],
        'sadness': PALETTE['sadness'],
        'anger': PALETTE['anger'],
        'fear': PALETTE['fear'],
        'surprise': PALETTE['surprise'],
        'neutral/others': PALETTE['neutral_emotion']
    }
    
    sns.barplot(data=emotion_counts, x='Emotion', y='Count', palette=color_map)
    plt.title("Distribution of Detected Emotions (Test Set)")
    plt.xlabel("Emotion")
    plt.ylabel("Number of Tweets")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'emotion_distribution.png'), dpi=300)
    plt.close()
    
    # ------------------ 5. Demographic Trend Analysis ------------------
    print("Analyzing Demographic Trends...")
    
    # Sentiment by Age
    plt.figure(figsize=(12, 6))
    age_sentiment = test_df.groupby(['Age of User', 'sentiment']).size().unstack(fill_value=0)
    age_sentiment_pct = age_sentiment.div(age_sentiment.sum(axis=1), axis=0) * 100
    
    age_sentiment_pct.plot(kind='bar', stacked=True, color=[PALETTE['negative'], PALETTE['neutral'], PALETTE['positive']], ax=plt.gca())
    plt.title("Sentiment Percentage by User Age Group")
    plt.ylabel("Percentage (%)")
    plt.xlabel("Age Group")
    plt.xticks(rotation=0)
    plt.legend(title="Sentiment", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sentiment_by_age.png'), dpi=300)
    plt.close()
    
    # Sentiment by Time of Tweet
    plt.figure(figsize=(10, 5))
    time_sentiment = test_df.groupby(['Time of Tweet', 'sentiment']).size().unstack(fill_value=0)
    time_sentiment_pct = time_sentiment.div(time_sentiment.sum(axis=1), axis=0) * 100
    
    time_sentiment_pct.plot(kind='bar', stacked=True, color=[PALETTE['negative'], PALETTE['neutral'], PALETTE['positive']], ax=plt.gca())
    plt.title("Sentiment Percentage by Time of Tweet")
    plt.ylabel("Percentage (%)")
    plt.xlabel("Time of Tweet")
    plt.xticks(rotation=0)
    plt.legend(title="Sentiment", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sentiment_by_time.png'), dpi=300)
    plt.close()
    
    # Sentiment by Country (Top 10)
    plt.figure(figsize=(12, 6))
    top_countries = test_df['Country'].value_counts().head(10).index
    country_df = test_df[test_df['Country'].isin(top_countries)]
    
    # Group by country and calculate the average VADER compound score
    country_sentiment = country_df.groupby('Country')['vader_compound'].mean().sort_values(ascending=False).reset_index()
    
    sns.barplot(data=country_sentiment, x='vader_compound', y='Country', palette='coolwarm')
    plt.title("Average Sentiment Score (VADER Compound) by Country (Top 10)")
    plt.xlabel("Average Compound Score (-1 to +1)")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sentiment_by_country.png'), dpi=300)
    plt.close()
    
    print("\nAll tasks completed. Reports saved to 'model_evaluation.txt', and plots saved to the 'plots/' directory.")

if __name__ == "__main__":
    main()
