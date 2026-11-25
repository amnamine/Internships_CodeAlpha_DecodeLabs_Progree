# CodeAlpha Artificial Intelligence Internship — Tasks

This repository contains my submission for the **CodeAlpha Artificial Intelligence Internship**. The internship requires completing **2 or 3 out of 4** listed AI tasks; this repo implements **three** of them:

| # | Task (per CodeAlpha brief) | File | Status |
|---|---|---|---|
| 1 | Language Translation Tool | `AI_Task1.py` | ✅ Done |
| 2 | Chatbot for FAQs | `AI_Task2.py` | ✅ Done |
| 3 | Music Generation with AI | — | ⬜ Not attempted |
| 4 | Object Detection and Tracking | `AI_Task3.py` | ✅ Done |

> **Note on file naming:** `AI_Task3.py` is the third script submitted in this repo, but it implements **Task 4 (Object Detection and Tracking)** from the original brief — Task 3 (Music Generation) was skipped in favor of it. The file's internal docstring is labeled "TASK 4" accordingly. Since 3 completed tasks already satisfies the internship's minimum requirement, this naming has no impact on eligibility.

---

## About the Internship

CodeAlpha is a software development company offering hands-on internships in emerging technologies. The AI track focuses on practical experience with model development, NLP, computer vision, and real-time data processing, with mentorship and project-based learning.

**Perks include:** an offer letter, a QR-verified completion certificate, a unique ID certificate, a letter of recommendation (performance-based), placement support, and resume-building assistance.

**Internship completion criteria:** a minimum of 2–3 completed tasks is required; submitting only one task is not eligible for certification.

---

## Repository Structure

```
.
├── AI_Task1.py   # Language Translation Tool (Tkinter GUI)
├── AI_Task2.py   # FAQ Chatbot (TF-IDF + cosine similarity)
├── AI_Task3.py   # Object Detection & Tracking (YOLO + ByteTrack)
└── README.md
```

---

## Task 1 — Language Translation Tool (`AI_Task1.py`)

A desktop GUI application built with **Tkinter** that translates text between languages.

**Features**
- Text input box with selectable source and target languages (18 languages + auto-detect)
- Translation powered by Google Translate via the `deep-translator` library
- One-click language swap button
- Copy-to-clipboard for the translated text
- Text-to-speech playback of the translation (via `pyttsx3`), run on a background thread so the UI doesn't freeze
- Clear/reset button and live status messages

**Requirements**
```bash
pip install deep-translator pyttsx3
```

**Run**
```bash
python AI_Task1.py
```

---

## Task 2 — Chatbot for FAQs (`AI_Task2.py`)

A rule-based FAQ chatbot with a chat-style **Tkinter** UI, built around classic NLP text matching rather than a generative model.

**How it works**
1. A set of FAQ question/answer pairs (sample topic: an online electronics store) is defined in code.
2. Each question is preprocessed: lowercased, stripped of punctuation, tokenized with a regex (no fragile `punkt` dependency), stopwords removed, and lemmatized using NLTK's `WordNetLemmatizer`.
3. A **TF-IDF vectorizer** (scikit-learn) builds a vector index over all FAQ questions at startup.
4. When the user asks something, their input goes through the same preprocessing pipeline, and **cosine similarity** is used to find the closest matching FAQ.
5. If the best match scores below a confidence threshold (0.2), the bot admits it doesn't know rather than returning a poor match.
6. The chosen answer is displayed in a bubble-style chat interface.

**Resilience note:** the script proactively detects and repairs corrupted/incomplete NLTK downloads (the common `BadZipFile` error) by re-downloading the affected resource, and falls back to a small built-in stopword list and skips lemmatization if NLTK data still can't be fetched (e.g. no internet) — so the chatbot keeps working in a degraded mode instead of crashing.

**Requirements**
```bash
pip install nltk scikit-learn
```

**Run**
```bash
python AI_Task2.py
```

**Customizing:** replace the `FAQS` list near the top of the file with your own product/topic questions and answers.

---

## Task 3 in this repo — Object Detection and Tracking (`AI_Task3.py`)

A command-line tool that performs detection and multi-object tracking on a **video file** (offline processing, not live webcam) using **OpenCV** and **Ultralytics YOLO**.

**Pipeline**
1. Loads a pretrained YOLO model (default: `yolo26n.pt`).
2. Opens the input video and reads its FPS, resolution, and frame count.
3. For every frame, runs `model.track(..., persist=True)`, which performs detection plus **ByteTrack** (a SORT-family tracker) so each object keeps a consistent ID across frames.
4. Draws a bounding box, class label, confidence score, and tracking ID on each detected object, plus a frame-progress overlay.
5. Writes the annotated frames to an output video file, with optional live preview (`--show`).
6. Prints progress every 30 frames and a final summary (frames processed, elapsed time, average FPS).

**Requirements**
```bash
pip install ultralytics opencv-python
```

**Run**
```bash
python AI_Task3.py --input input_video.mp4 --output output_video.mp4
```

**Options**

| Flag | Default | Description |
|---|---|---|
| `--input` | `video.mp4` | Path to the input video file |
| `--output` | `output_video.mp4` | Path to save the annotated output |
| `--model` | `yolo26n.pt` | YOLO model weights to use |
| `--conf` | `0.4` | Detection confidence threshold |
| `--tracker` | `bytetrack.yaml` | Tracker config (`bytetrack.yaml` or `botsort.yaml`) |
| `--show` | off | Display the video live while processing |

---

## General Setup

Clone the repo and install all dependencies used across the three tasks:

```bash
pip install deep-translator pyttsx3 nltk scikit-learn ultralytics opencv-python
```

Each script is standalone and can be run independently with `python <filename>.py`.

---

## Submission Checklist (per CodeAlpha instructions)

- [ ] Share internship status on LinkedIn, tagging @CodeAlpha
- [ ] Push source code to a GitHub repo named `CodeAlpha_ProjectName`
- [ ] Post a video walkthrough on LinkedIn with the GitHub repo link
- [ ] Submit the completed tasks via the official Submission Form

---

## Contact (CodeAlpha)

- Website: [www.codealpha.tech](https://www.codealpha.tech)
- Email: services@codealpha.tech, services.codealpha@gmail.com
- WhatsApp: +91 9336576683
