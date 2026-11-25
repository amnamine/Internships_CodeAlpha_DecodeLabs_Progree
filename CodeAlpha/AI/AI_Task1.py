"""
TASK 1: Language Translation Tool
----------------------------------
A desktop GUI application built with Tkinter that lets a user:
  - Enter text and select source & target languages
  - Send the text to a translation engine (Google Translate via deep-translator)
  - Display the translated text on screen
  - Copy the translation to the clipboard
  - Hear the translation read aloud (text-to-speech)

Required installs (run in your terminal):
    pip install deep-translator pyttsx3
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from deep_translator import GoogleTranslator
import pyttsx3

# ---------------------------------------------------------------------------
# Supported languages: display name -> language code
# ---------------------------------------------------------------------------
LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko",
    "Hindi": "hi",
    "Turkish": "tr",
    "Dutch": "nl",
    "Greek": "el",
    "Hebrew": "he",
    "Polish": "pl",
    "Swedish": "sv",
}

TARGET_LANGUAGES = [name for name in LANGUAGES if name != "Auto Detect"]


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Translation Tool")
        self.root.geometry("650x560")
        self.root.resizable(False, False)

        # Text-to-speech engine (initialized once, reused for each "Speak" click)
        self.tts_engine = pyttsx3.init()

        self.build_ui()

    # ------------------------------------------------------------------ UI
    def build_ui(self):
        title_label = tk.Label(
            self.root, text="Language Translation Tool",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=12)

        # ---- Input box -----------------------------------------------
        input_frame = tk.LabelFrame(self.root, text="Enter Text", font=("Segoe UI", 10, "bold"))
        input_frame.pack(padx=15, pady=5, fill="both")

        self.input_text = tk.Text(input_frame, height=6, wrap="word", font=("Segoe UI", 11))
        self.input_text.pack(padx=10, pady=10, fill="both")

        # ---- Language selectors ---------------------------------------
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(pady=10)

        tk.Label(lang_frame, text="From:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5)
        self.source_lang = ttk.Combobox(
            lang_frame, values=list(LANGUAGES.keys()), state="readonly", width=20
        )
        self.source_lang.current(0)  # default: Auto Detect
        self.source_lang.grid(row=0, column=1, padx=5)

        swap_btn = tk.Button(lang_frame, text="\u21c4", command=self.swap_languages,
                              font=("Segoe UI", 10, "bold"))
        swap_btn.grid(row=0, column=2, padx=10)

        tk.Label(lang_frame, text="To:", font=("Segoe UI", 10)).grid(row=0, column=3, padx=5)
        self.target_lang = ttk.Combobox(
            lang_frame, values=TARGET_LANGUAGES, state="readonly", width=20
        )
        self.target_lang.current(0)  # default: English
        self.target_lang.grid(row=0, column=4, padx=5)

        # ---- Translate button -------------------------------------------
        translate_btn = tk.Button(
            self.root, text="Translate", command=self.translate_text,
            bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"), width=15
        )
        translate_btn.pack(pady=8)

        # ---- Output box ---------------------------------------------------
        output_frame = tk.LabelFrame(self.root, text="Translated Text", font=("Segoe UI", 10, "bold"))
        output_frame.pack(padx=15, pady=5, fill="both")

        self.output_text = tk.Text(
            output_frame, height=6, wrap="word", font=("Segoe UI", 11),
            state="disabled", bg="#f5f5f5"
        )
        self.output_text.pack(padx=10, pady=10, fill="both")

        # ---- Bottom action buttons -----------------------------------------
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=12)

        copy_btn = tk.Button(btn_frame, text="Copy", command=self.copy_translation, width=12)
        copy_btn.grid(row=0, column=0, padx=10)

        speak_btn = tk.Button(btn_frame, text="Speak", command=self.speak_translation, width=12)
        speak_btn.grid(row=0, column=1, padx=10)

        clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_all, width=12)
        clear_btn.grid(row=0, column=2, padx=10)

        self.status_label = tk.Label(self.root, text="", font=("Segoe UI", 9), fg="gray")
        self.status_label.pack(pady=2)

    # -------------------------------------------------------------- actions
    def swap_languages(self):
        src = self.source_lang.get()
        tgt = self.target_lang.get()
        if src != "Auto Detect":
            self.source_lang.set(tgt)
            self.target_lang.set(src)
        else:
            messagebox.showinfo("Swap Unavailable", "Pick a specific source language first to swap.")

    def translate_text(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Input Needed", "Please enter some text to translate.")
            return

        src_code = LANGUAGES[self.source_lang.get()]
        tgt_code = LANGUAGES[self.target_lang.get()]

        self.status_label.config(text="Translating...")
        self.root.update_idletasks()

        try:
            translated = GoogleTranslator(source=src_code, target=tgt_code).translate(text)
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", translated)
            self.output_text.config(state="disabled")
            self.status_label.config(text="Done.")
        except Exception as e:
            self.status_label.config(text="")
            messagebox.showerror("Translation Error", f"Could not translate text:\n{e}")

    def copy_translation(self):
        translated = self.output_text.get("1.0", "end").strip()
        if translated:
            self.root.clipboard_clear()
            self.root.clipboard_append(translated)
            self.status_label.config(text="Copied to clipboard.")
        else:
            messagebox.showwarning("Nothing to Copy", "There is no translated text yet.")

    def speak_translation(self):
        translated = self.output_text.get("1.0", "end").strip()
        if translated:
            # Run in a background thread so the GUI doesn't freeze while speaking
            threading.Thread(target=self._speak, args=(translated,), daemon=True).start()
        else:
            messagebox.showwarning("Nothing to Speak", "There is no translated text yet.")

    def _speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def clear_all(self):
        self.input_text.delete("1.0", "end")
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")
        self.status_label.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()