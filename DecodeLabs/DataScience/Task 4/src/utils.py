import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc
from wordcloud import WordCloud


# Set clean modern visualization style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})


def plot_sentiment_distribution(df, target_col='sentiment', save_path=None):
    """Plots clean bar distribution and pie chart of sentiments."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    counts = df[target_col].value_counts()
    colors = ['#2b5c8f', '#d95f02']

    # Bar chart
    sns.barplot(x=counts.index, y=counts.values, ax=axes[0], palette=colors)
    axes[0].set_title("Sentiment Class Distribution", fontsize=14, fontweight='bold', pad=12)
    axes[0].set_xlabel("Sentiment", fontsize=12)
    axes[0].set_ylabel("Number of Reviews", fontsize=12)
    for p in axes[0].patches:
        axes[0].annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha='center', va='center', xytext=(0, 6), textcoords='offset points', fontweight='bold')

    # Donut / Pie chart
    axes[1].pie(counts.values, labels=counts.index, autopct='%1.1f%%', colors=colors, 
                startangle=140, explode=(0.04, 0.04), wedgeprops=dict(width=0.6, edgecolor='w'))
    axes[1].set_title("Sentiment Ratio", fontsize=14, fontweight='bold', pad=12)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig


def plot_wordclouds(positive_texts, negative_texts, save_path=None):
    """Plots side-by-side Word Clouds for Positive and Negative reviews."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    wc_pos = WordCloud(width=800, height=400, background_color='white',
                       colormap='Greens_r', max_words=150).generate(positive_texts)
    wc_neg = WordCloud(width=800, height=400, background_color='white',
                       colormap='Reds_r', max_words=150).generate(negative_texts)

    axes[0].imshow(wc_pos, interpolation='bilinear')
    axes[0].axis('off')
    axes[0].set_title("Most Frequent Words in Positive Reviews", fontsize=15, fontweight='bold', pad=10)

    axes[1].imshow(wc_neg, interpolation='bilinear')
    axes[1].axis('off')
    axes[1].set_title("Most Frequent Words in Negative Reviews", fontsize=15, fontweight='bold', pad=10)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig


def plot_confusion_matrices(results, save_path=None):
    """Plots Heatmaps of Confusion Matrices for all evaluated models."""
    n_models = len(results)
    fig, axes = plt.subplots(1, n_models, figsize=(5.5 * n_models, 4.5))
    if n_models == 1:
        axes = [axes]

    for idx, (name, metrics) in enumerate(results.items()):
        cm = metrics['confusion_matrix']
        sns.heatmap(cm, annot=True, fmt=',d', cmap='Blues', cbar=False, ax=axes[idx],
                    xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'],
                    annot_kws={"size": 13, "weight": "bold"})
        axes[idx].set_title(f"{name}\nAcc: {metrics['Accuracy']:.3f} | F1: {metrics['F1-Score']:.3f}",
                            fontsize=12, fontweight='bold', pad=10)
        axes[idx].set_xlabel("Predicted Label", fontsize=11)
        axes[idx].set_ylabel("True Label", fontsize=11)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig


def plot_roc_curves(results, y_test, save_path=None):
    """Plots ROC Curves for all evaluated models in a single comparative chart."""
    fig, ax = plt.subplots(figsize=(8, 6))

    for name, metrics in results.items():
        y_prob = metrics['y_prob']
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = metrics['ROC-AUC']
        ax.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {roc_auc:.4f})")

    ax.plot([0, 1], [0, 1], color='gray', lw=1.5, linestyle='--', label='Random Chance (AUC = 0.5000)')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    ax.set_ylabel('True Positive Rate (Sensitivity)', fontsize=12)
    ax.set_title('Receiver Operating Characteristic (ROC) Curves', fontsize=14, fontweight='bold', pad=12)
    ax.legend(loc="lower right", frameon=True, fontsize=10)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig


def plot_top_features(model, vectorizer, top_n=20, save_path=None):
    """Visualizes top positive and negative predictive words/n-grams from Linear Model coefficients."""
    if not hasattr(model, "coef_"):
        return None

    feature_names = np.array(vectorizer.get_feature_names_out())
    coef = model.coef_[0]

    top_pos_idx = np.argsort(coef)[-top_n:]
    top_neg_idx = np.argsort(coef)[:top_n]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Top Positive Features
    sns.barplot(x=coef[top_pos_idx], y=feature_names[top_pos_idx], ax=axes[0], palette="Greens_d")
    axes[0].set_title(f"Top {top_n} Words Indicating POSITIVE Sentiment", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Model Coefficient (Weight)")

    # Top Negative Features
    sns.barplot(x=coef[top_neg_idx], y=feature_names[top_neg_idx], ax=axes[1], palette="Reds_d")
    axes[1].set_title(f"Top {top_n} Words Indicating NEGATIVE Sentiment", fontsize=13, fontweight='bold')
    axes[1].set_xlabel("Model Coefficient (Weight)")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig
