"""
FAQ Chatbot
-----------
Task 2 implementation:
  1. Collect FAQs (question/answer pairs) about a topic/product.
  2. Preprocess text (tokenize, lowercase, clean punctuation, remove stopwords,
     lemmatize) using NLTK.
  3. Match the user's question to the most similar FAQ using TF-IDF + cosine
     similarity (scikit-learn).
  4. Display the best matching answer as a chatbot response.
  5. Optional: simple chat UI built with Tkinter.

Run with:  python AI_Task2.py
Requires:  pip install nltk scikit-learn

NOTE on the previous "BadZipFile: File is not a zip file" error:
  That happens when a previous NLTK data download got interrupted (firewall,
  antivirus, OneDrive sync, etc.) and left a corrupted .zip on disk. This
  version (a) no longer depends on the fragile 'punkt'/'punkt_tab' tokenizer
  at all -- tokenizing is done with a simple, dependency-free regex instead
  -- and (b) automatically detects and deletes any corrupted leftover NLTK
  files for stopwords/wordnet and re-downloads them cleanly. If a download
  still fails (e.g. no internet), the app falls back to a small built-in
  stopword list and skips lemmatization instead of crashing.

  If you still get errors after running this version, the fastest manual fix
  is: delete your nltk_data folder completely, then rerun the script.
  It is usually at one of:
      C:\\Users\\<you>\\AppData\\Roaming\\nltk_data
      C:\\Users\\<you>\\nltk_data
  (run `import nltk; print(nltk.data.path)` in Python to see the exact
  folders NLTK is using on your machine).
"""

import os
import re
import shutil
import string
import tkinter as tk
from tkinter import ttk

import nltk
from nltk.corpus import stopwords as _stopwords_corpus
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# 1. Robust NLTK setup: detect + auto-repair corrupted data, with a safe
#    fallback if downloads aren't possible at all (no internet, blocked, etc.)
#
#    Important: we test each resource by actually USING it (calling
#    stopwords.words(...) / lemmatizer.lemmatize(...)), not just by calling
#    nltk.data.find() on its own -- find() can report a resource as
#    "not found" even when it is perfectly fine, which caused false
#    failures. Using the resource for real is what actually triggers (and
#    therefore actually detects) a corrupted/incomplete zip.
# ---------------------------------------------------------------------------
_FALLBACK_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "of",
    "for", "is", "are", "was", "were", "be", "been", "being", "i", "you",
    "he", "she", "it", "we", "they", "do", "does", "did", "have", "has",
    "had", "with", "this", "that", "these", "those", "my", "your", "his",
    "her", "its", "our", "their", "what", "which", "who", "whom", "as",
    "by", "from", "about", "into", "than", "so", "such", "not", "no",
    "can", "could", "will", "would", "should", "just", "there", "here",
    "am", "me", "us", "them",
}

_lemmatizer = WordNetLemmatizer()


def _resource_works(test_fn) -> bool:
    try:
        test_fn()
        return True
    except Exception:
        return False


def _wipe_resource(resource_path: str) -> None:
    """Delete any existing copy (extracted folder and/or .zip) of an NLTK
    resource so a fresh download isn't blocked by corrupted leftovers."""
    for base in list(nltk.data.path):
        for candidate in (
            os.path.join(base, resource_path),
            os.path.join(base, resource_path + ".zip"),
        ):
            if os.path.isdir(candidate):
                shutil.rmtree(candidate, ignore_errors=True)
            elif os.path.isfile(candidate):
                try:
                    os.remove(candidate)
                except OSError:
                    pass


def ensure_resource(pkg_name: str, resource_path: str, test_fn) -> bool:
    """Make sure an NLTK resource is genuinely usable. If the first real-use
    test fails (missing OR corrupted, e.g. BadZipFile), wipe any broken
    leftovers and re-download once. Returns True if it ends up usable."""
    if _resource_works(test_fn):
        return True

    _wipe_resource(resource_path)
    try:
        nltk.download(pkg_name, quiet=True)
    except Exception as exc:
        print(f"[warning] Download failed for '{pkg_name}': {exc}")

    ok = _resource_works(test_fn)
    if not ok:
        print(f"[warning] NLTK resource '{pkg_name}' still unusable after retry; "
              f"falling back to a built-in alternative.")
    return ok


_have_stopwords = ensure_resource(
    "stopwords", "corpora/stopwords",
    lambda: _stopwords_corpus.words("english"),
)
_have_wordnet = ensure_resource(
    "wordnet", "corpora/wordnet",
    lambda: _lemmatizer.lemmatize("testing"),
)
# omw-1.4 backs some wordnet lookups in newer NLTK versions; same usability test
ensure_resource("omw-1.4", "corpora/omw-1.4", lambda: _lemmatizer.lemmatize("testing"))

if _have_stopwords:
    STOP_WORDS = set(_stopwords_corpus.words("english"))
else:
    STOP_WORDS = _FALLBACK_STOPWORDS

if _have_wordnet:
    def lemmatize(word: str) -> str:
        return _lemmatizer.lemmatize(word)
else:
    def lemmatize(word: str) -> str:
        return word  # no-op fallback if wordnet isn't available


# ---------------------------------------------------------------------------
# 2. FAQ dataset (topic: an online electronics store)
#    -> Replace/extend this list with FAQs for your own product/topic.
# ---------------------------------------------------------------------------
FAQS = [
    {"question": "What are your business hours?",
     "answer": "We are open Monday to Friday, 9 AM to 6 PM, and Saturday 10 AM to 4 PM."},
    {"question": "How can I track my order?",
     "answer": "You can track your order anytime using the tracking link emailed to you once it ships."},
    {"question": "What is your return and refund policy?",
     "answer": "Items can be returned within 30 days of purchase for a full refund, as long as they are unused and in original packaging."},
    {"question": "Do you offer international shipping?",
     "answer": "Yes, we ship to over 50 countries worldwide. International delivery usually takes 7-14 business days."},
    {"question": "How do I reset my account password?",
     "answer": "Go to the login page, click 'Forgot Password', and follow the instructions sent to your registered email."},
    {"question": "What payment methods do you accept?",
     "answer": "We accept credit/debit cards, PayPal, and bank transfers."},
    {"question": "How long does standard delivery take?",
     "answer": "Standard domestic delivery takes 3-5 business days; express delivery takes 1-2 business days."},
    {"question": "Can I cancel my order after placing it?",
     "answer": "Orders can be cancelled within 1 hour of purchase from your account's 'My Orders' page."},
    {"question": "Do your products come with a warranty?",
     "answer": "All electronics come with a 1-year manufacturer warranty covering defects."},
    {"question": "How can I contact customer support?",
     "answer": "You can reach our support team via live chat on the website, or email support@example.com."},
]


# ---------------------------------------------------------------------------
# 3. Preprocessing: lowercase, strip punctuation, tokenize (regex, no NLTK
#    'punkt' dependency needed), remove stopwords, lemmatize.
# ---------------------------------------------------------------------------
def preprocess(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = re.findall(r"\b[a-z0-9]+\b", text)
    tokens = [lemmatize(tok) for tok in tokens if tok not in STOP_WORDS]
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# 4. Build the TF-IDF index once at startup over all FAQ questions.
# ---------------------------------------------------------------------------
_cleaned_questions = [preprocess(faq["question"]) for faq in FAQS]
_vectorizer = TfidfVectorizer()
_faq_vectors = _vectorizer.fit_transform(_cleaned_questions)

CONFIDENCE_THRESHOLD = 0.2  # below this similarity score we admit we don't know


def get_best_answer(user_text: str):
    """Return (answer, similarity_score) for the FAQ closest to user_text."""
    cleaned = preprocess(user_text)
    if not cleaned.strip():
        return "Could you type an actual question?", 0.0

    user_vec = _vectorizer.transform([cleaned])
    similarities = cosine_similarity(user_vec, _faq_vectors)[0]
    best_idx = similarities.argmax()
    best_score = similarities[best_idx]

    if best_score < CONFIDENCE_THRESHOLD:
        return ("Sorry, I'm not sure about that. Could you rephrase your "
                "question, or ask about orders, shipping, returns, "
                "payments, or support?"), best_score

    return FAQS[best_idx]["answer"], best_score


# ---------------------------------------------------------------------------
# 5. Tkinter chat UI
# ---------------------------------------------------------------------------
class ChatBotApp:
    BG = "#f0f2f5"
    USER_BUBBLE = "#0b84ff"
    BOT_BUBBLE = "#e4e6eb"
    USER_TEXT = "white"
    BOT_TEXT = "black"

    def __init__(self, root):
        self.root = root
        root.title("FAQ Chatbot")
        root.geometry("480x600")
        root.configure(bg=self.BG)
        root.minsize(360, 420)

        # ---- Header -------------------------------------------------
        header = tk.Frame(root, bg="#0b84ff", height=56)
        header.pack(fill="x", side="top")
        tk.Label(
            header, text="🤖 FAQ Assistant", bg="#0b84ff", fg="white",
            font=("Segoe UI", 14, "bold"), pady=12
        ).pack()

        # ---- Scrollable chat area ------------------------------------
        chat_container = tk.Frame(root, bg=self.BG)
        chat_container.pack(fill="both", expand=True, padx=8, pady=8)

        self.canvas = tk.Canvas(chat_container, bg=self.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.canvas.yview)
        self.messages_frame = tk.Frame(self.canvas, bg=self.BG)

        self.messages_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw", width=440)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- Input area ----------------------------------------------
        input_frame = tk.Frame(root, bg=self.BG)
        input_frame.pack(fill="x", padx=8, pady=(0, 10))

        self.entry = ttk.Entry(input_frame, font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=6)
        self.entry.bind("<Return>", lambda e: self.send_message())
        self.entry.focus_set()

        send_btn = tk.Button(
            input_frame, text="Send", command=self.send_message,
            bg="#0b84ff", fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=14, pady=6, cursor="hand2",
        )
        send_btn.pack(side="right")

        # ---- Greeting ---------------------------------------------------
        self.add_message(
            "Hi! I can answer FAQs about orders, shipping, returns, "
            "payments, warranty, and support. Ask me anything!",
            sender="bot",
        )

    # -------------------------------------------------------------
    def add_message(self, text, sender="bot"):
        row = tk.Frame(self.messages_frame, bg=self.BG)
        row.pack(fill="x", pady=4, anchor="e" if sender == "user" else "w")

        bubble_bg = self.USER_BUBBLE if sender == "user" else self.BOT_BUBBLE
        bubble_fg = self.USER_TEXT if sender == "user" else self.BOT_TEXT

        bubble = tk.Label(
            row, text=text, bg=bubble_bg, fg=bubble_fg,
            font=("Segoe UI", 10), wraplength=320, justify="left",
            padx=10, pady=8,
        )
        bubble.pack(side="right" if sender == "user" else "left",
                    padx=10, anchor="e" if sender == "user" else "w")

        self.root.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # -------------------------------------------------------------
    def send_message(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.entry.delete(0, tk.END)
        self.add_message(user_text, sender="user")

        answer, score = get_best_answer(user_text)
        self.add_message(answer, sender="bot")


def main():
    root = tk.Tk()
    ChatBotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()