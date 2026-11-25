import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)
import joblib


class SentimentModelTrainer:
    """
    Trains and evaluates standard NLP sentiment classifiers:
    - Multinomial Naive Bayes (MultinomialNB)
    - Linear Support Vector Machine (LinearSVC)
    - Logistic Regression
    """

    def __init__(self):
        self.models = {
            "Multinomial Naive Bayes": MultinomialNB(alpha=0.5),
            "Linear SVM (LinearSVC)": LinearSVC(C=1.0, random_state=42, max_iter=3000),
            "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        }
        self.trained_models = {}
        self.results = {}

    def train_and_evaluate(self, X_train, y_train, X_test, y_test):
        """
        Fits each model and calculates evaluation metrics (Accuracy, Precision, Recall, F1, ROC-AUC).
        """
        for name, model in self.models.items():
            print(f"[*] Training {name}...")
            model.fit(X_train, y_train)
            self.trained_models[name] = model

            # Predictions
            y_pred = model.predict(X_test)
            
            # Predict Probabilities / Decision Scores for ROC-AUC
            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_test)[:, 1]
            elif hasattr(model, "decision_function"):
                y_prob = model.decision_function(X_test)
            else:
                y_prob = y_pred

            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, pos_label=1)
            rec = recall_score(y_test, y_pred, pos_label=1)
            f1 = f1_score(y_test, y_pred, pos_label=1)
            auc = roc_auc_score(y_test, y_prob)

            self.results[name] = {
                "Accuracy": acc,
                "Precision": prec,
                "Recall": rec,
                "F1-Score": f1,
                "ROC-AUC": auc,
                "y_pred": y_pred,
                "y_prob": y_prob,
                "confusion_matrix": confusion_matrix(y_test, y_pred),
                "classification_report": classification_report(y_test, y_pred, target_names=['Negative', 'Positive'], output_dict=False)
            }
            print(f"    -> {name} | Accuracy: {acc:.4f} | F1: {f1:.4f} | ROC-AUC: {auc:.4f}")

        return self.results

    def get_best_model(self, metric="F1-Score"):
        """Returns the name and instance of the best performing model."""
        best_name = max(self.results, key=lambda k: self.results[k][metric])
        return best_name, self.trained_models[best_name]

    def save_model(self, model_name: str, filepath: str):
        """Saves specified model to disk."""
        if model_name in self.trained_models:
            joblib.dump(self.trained_models[model_name], filepath)
        else:
            raise ValueError(f"Model {model_name} not found in trained models.")

    @staticmethod
    def load_model(filepath: str):
        """Loads a model from disk."""
        return joblib.load(filepath)
