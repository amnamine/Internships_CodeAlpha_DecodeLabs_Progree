import os
import sys
import threading
import time
import requests
import io
import re
import pickle
import pandas as pd
import numpy as np

import customtkinter as ctk
from tkinter import filedialog, messagebox

# FAISS and Sentence Transformers Imports
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

from sklearn.feature_extraction.text import TfidfVectorizer
import groq

# Hardcoded Groq API Configuration
GROQ_API_KEY = ""
DEFAULT_MODEL = "llama-3.3-70b-versatile"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "rag_cache")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# System Prompt Template with Strict Negative Constraints and Citation Rules
DEFAULT_CLOSED_BOOK_SYSTEM_PROMPT = """You are a strict Context-Anchored Closed-Book Answering Agent.
Your sole mission is to answer user questions using EXCLUSIVELY the provided reference context documents.

STRICT OPERATIONAL RULES:
1. CLOSED-BOOK RULE: You MUST rely ONLY on the provided reference context text below. Do NOT use any prior world knowledge or external facts.
2. NEGATIVE CONSTRAINT RULE: If the user's question cannot be completely and directly answered using ONLY the provided reference context, your response MUST BE EXACTLY: "Information Not Found" (with no extra explanation or outside guessing).
3. EXACT PARAGRAPH CITATION RULE: For every claim, fact, or answer derived from the context, you MUST append the exact paragraph citation (e.g., [Paragraph 1], [Paragraph 2], [Source: CSV Row 3]) immediately following the sentence or statement.
4. ABSOLUTE FACTUALITY: Do not infer, assume, or extrapolate beyond what is explicitly stated in the context.

REFERENCE CONTEXT:
---
{context_text}
---
"""

# Pre-packaged Sample Knowledge Base CSV Datasets
SAMPLE_DATASETS = {
    "Quantum & Physics Knowledge Base (CSV)": """id,category,paragraph_text,source
1,Quantum Physics,"Quantum computing leverages quantum mechanics phenomena such as superposition and entanglement. In superposition, quantum bits or qubits can exist in states representing 0, 1, or both simultaneously.",Physics_Journal_2025.csv
2,Quantum Physics,"Quantum entanglement allows qubits that are physically separated to be instantaneously connected, such that the state of one qubit dictates the state of another regardless of distance.",Physics_Journal_2025.csv
3,Cryogenics,"Superconducting quantum processors require dilution refrigerators operating at ultracold temperatures near 15 millikelvin (-273.135 degrees Celsius) to preserve fragile quantum coherence.",Physics_Journal_2025.csv
4,Astrophysics,"Neutron stars are the collapsed cores of massive supergiant stars, possessing extreme densities where a single teaspoon of neutron star material would weigh approximately 6 billion tons on Earth.",Physics_Journal_2025.csv
5,Particle Physics,"The Higgs boson was discovered at CERN's Large Hadron Collider in 2012, confirming the mechanism that imparts mass to fundamental elementary particles.",Physics_Journal_2025.csv""",

    "AI & Supercomputing Knowledge Base (CSV)": """id,category,paragraph_text,source
1,Neural Networks,"Transformer architecture relies heavily on self-attention mechanisms to dynamically weigh the relevance of different words in a sequence regardless of positional distance.",AI_Research_2026.csv
2,Hardware,"Graphics Processing Units (GPUs) and Tensor Processing Units (TPUs) utilize high-bandwidth memory (HBM3e) and parallel matrix multiplication units to accelerate deep learning training.",AI_Research_2026.csv
3,RAG Systems,"Retrieval-Augmented Generation (RAG) mitigates LLM hallucinations by retrieving relevant ground-truth document chunks from a vector store like FAISS and injecting them directly into the context prompt.",AI_Research_2026.csv
4,Optimization,"FlashAttention optimizes the self-attention memory bottleneck by tiling matrix operations and avoiding intermediate attention matrix writes to high-latency GPU global memory.",AI_Research_2026.csv
5,Model Scaling,"Mixture of Experts (MoE) architectures activate only a sparse subset of expert network parameters for each input token, enabling trillion-parameter capacity with reduced computational FLOPS.",AI_Research_2026.csv""",

    "Global Economics & Energy Knowledge Base (CSV)": """id,category,paragraph_text,source
1,Renewable Energy,"Perovskite solar cells have achieved laboratory power conversion efficiencies exceeding 33 percent when stacked in tandem configurations with traditional silicon wafers.",Global_Energy_2026.csv
2,Macroeconomics,"Central bank interest rate decisions directly influence commercial lending rates, inflation targets, and currency valuation through open market monetary operations.",Global_Energy_2026.csv
3,Nuclear Fusion,"Magnetic confinement fusion reactors, such as tokamaks, utilize powerful superconducting magnets to trap hydrogen plasma at temperatures exceeding 100 million degrees Celsius.",Global_Energy_2026.csv
4,Semiconductors,"Extreme Ultraviolet (EUV) lithography machines produced by ASML utilize 13.5 nanometer wavelength light to etch microscopic circuit patterns onto silicon wafers.",Global_Energy_2026.csv"""
}

# Domain-specific sample question suggestions
DOMAIN_SUGGESTIONS = {
    "Quantum & Physics Knowledge Base (CSV)": [
        "How do superconducting quantum processors stay cold?",
        "What is quantum entanglement and superposition?",
        "What is the mass weight of a teaspoon of neutron star material?"
    ],
    "AI & Supercomputing Knowledge Base (CSV)": [
        "How does Retrieval-Augmented Generation (RAG) mitigate LLM hallucinations?",
        "What hardware optimization does FlashAttention use to avoid memory bottlenecks?",
        "How do Mixture of Experts (MoE) architectures handle token processing?"
    ],
    "Global Economics & Energy Knowledge Base (CSV)": [
        "What power conversion efficiency have perovskite solar cells achieved?",
        "What temperature do magnetic confinement tokamak fusion reactors reach?",
        "What light wavelength does ASML EUV lithography use for silicon wafers?"
    ]
}

class EmbeddingEngine:
    """Handles vector embeddings with Instant Lazy Asynchronous loading."""
    def __init__(self, on_model_loaded_callback=None):
        self.st_model = None
        self.use_st = False
        self.vectorizer = None
        self.is_loading = False
        self.on_model_loaded_callback = on_model_loaded_callback

        # Start asynchronous loading in background thread so GUI pops up INSTANTLY (<0.1s)
        if ST_AVAILABLE:
            self.is_loading = True
            threading.Thread(target=self._async_load_model, daemon=True).start()

    def _async_load_model(self):
        try:
            start_t = time.time()
            self.st_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_st = True
            self.is_loading = False
            print(f"Background SentenceTransformer loaded in {time.time()-start_t:.2f}s")
            if self.on_model_loaded_callback:
                self.on_model_loaded_callback()
        except Exception as e:
            print(f"SentenceTransformer async load failed: {e}")
            self.use_st = False
            self.is_loading = False

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if self.use_st and self.st_model is not None:
            embeddings = self.st_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.astype('float32')
        else:
            if self.vectorizer is None or len(texts) > 1:
                self.vectorizer = TfidfVectorizer().fit(texts)
            matrix = self.vectorizer.transform(texts).toarray()
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return (matrix / norms).astype('float32')

class FAISSVectorStore:
    """FAISS Vector Database manager with instant disk saving and loading capabilities."""
    def __init__(self, embedder: EmbeddingEngine):
        self.embedder = embedder
        self.chunks = []
        self.index = None
        self.dimension = None

    def add_chunks(self, chunk_list: list[dict], cache_key: str = None):
        if not chunk_list:
            return
        
        texts = [c['paragraph'] for c in chunk_list]
        embeddings = self.embedder.embed_texts(texts)
        self.dimension = embeddings.shape[1]

        if FAISS_AVAILABLE:
            if self.index is None:
                self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(embeddings)
        
        start_idx = len(self.chunks)
        for i, c in enumerate(chunk_list):
            c['global_index'] = start_idx + i
            c['embedding'] = embeddings[i]
            self.chunks.append(c)

        if cache_key:
            self.save_to_disk(cache_key)

    def save_to_disk(self, cache_key: str):
        try:
            safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', cache_key)
            meta_path = os.path.join(CACHE_DIR, f"{safe_key}_meta.pkl")
            index_path = os.path.join(CACHE_DIR, f"{safe_key}_faiss.index")

            with open(meta_path, 'wb') as f:
                pickle.dump(self.chunks, f)

            if FAISS_AVAILABLE and self.index is not None:
                faiss.write_index(self.index, index_path)
        except Exception as e:
            print(f"Disk save failed: {e}")

    def load_from_disk(self, cache_key: str) -> bool:
        try:
            safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', cache_key)
            meta_path = os.path.join(CACHE_DIR, f"{safe_key}_meta.pkl")
            index_path = os.path.join(CACHE_DIR, f"{safe_key}_faiss.index")

            if not os.path.exists(meta_path):
                return False

            with open(meta_path, 'rb') as f:
                self.chunks = pickle.load(f)

            if FAISS_AVAILABLE and os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
                self.dimension = self.index.d
            else:
                doc_embs = np.array([c['embedding'] for c in self.chunks])
                self.dimension = doc_embs.shape[1]
                if FAISS_AVAILABLE:
                    self.index = faiss.IndexFlatIP(self.dimension)
                    self.index.add(doc_embs)
            return True
        except Exception as e:
            print(f"Disk load failed: {e}")
            return False

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        if not self.chunks:
            return []

        query_emb = self.embedder.embed_texts([query])

        if FAISS_AVAILABLE and self.index is not None:
            k = min(top_k, len(self.chunks))
            scores, indices = self.index.search(query_emb, k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.chunks):
                    chunk = self.chunks[idx].copy()
                    chunk['score'] = float(score)
                    results.append(chunk)
            return results
        else:
            doc_embs = np.array([c['embedding'] for c in self.chunks])
            scores = np.dot(doc_embs, query_emb.T).flatten()
            top_indices = np.argsort(scores)[::-1][:top_k]
            results = []
            for idx in top_indices:
                chunk = self.chunks[idx].copy()
                chunk['score'] = float(scores[idx])
                results.append(chunk)
            return results

    def clear(self):
        self.chunks.clear()
        self.index = None
        self.dimension = None

class RAGApplication(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App Window Setup - Opens INSTANTLY!
        self.title("Context-Anchored Answering (RAG Basics) - Llama 3 70B & FAISS")
        self.geometry("1300x860")
        self.minsize(1080, 720)

        # CustomTkinter Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Groq Client Initialization
        self.groq_client = groq.Groq(api_key=GROQ_API_KEY)
        self.model_name = DEFAULT_MODEL

        # RAG Engine Initialization with Lazy Model Callback
        self.embedder = EmbeddingEngine(on_model_loaded_callback=self._on_embedder_ready)
        self.vector_store = FAISSVectorStore(self.embedder)

        # Settings
        self.strict_mode = ctk.BooleanVar(value=True)
        self.top_k_var = ctk.IntVar(value=4)
        self.system_prompt_var = ctk.StringVar(value=DEFAULT_CLOSED_BOOK_SYSTEM_PROMPT)

        # Dynamic Suggestion Buttons list
        self.suggestion_buttons = []
        self.current_dataset_name = "Quantum & Physics Knowledge Base (CSV)"

        # Create GUI Layout immediately
        self._create_layout()

        # Load default dataset into FAISS index (from disk if available!)
        self._load_sample_dataset(self.current_dataset_name)

    def _on_embedder_ready(self):
        self.after(0, lambda: self.stat_embed_label.configure(
            text="Embedder: MiniLM-L6-v2 (Active)",
            text_color="#00E676"
        ))

    def _create_layout(self):
        # Grid Configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=290, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        # Sidebar Title
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="⚡ RAG Vector DB", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        subtitle_label = ctk.CTkLabel(
            self.sidebar, 
            text="Instant Disk Engine", 
            font=ctk.CTkFont(size=12, weight="normal"), 
            text_color="#8899A6"
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        # Dataset Loader Section
        ds_header = ctk.CTkLabel(self.sidebar, text="📚 Select Knowledge Base", font=ctk.CTkFont(size=14, weight="bold"))
        ds_header.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        self.dataset_optionmenu = ctk.CTkOptionMenu(
            self.sidebar, 
            values=list(SAMPLE_DATASETS.keys()),
            command=self._on_dataset_select
        )
        self.dataset_optionmenu.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Custom File / Web Loader Buttons
        self.upload_btn = ctk.CTkButton(
            self.sidebar, 
            text="📁 Upload Document (CSV/TXT)", 
            command=self._upload_custom_file,
            fg_color="#2A3C50", hover_color="#3B526D"
        )
        self.upload_btn.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.web_scrape_btn = ctk.CTkButton(
            self.sidebar, 
            text="🌐 Scrape Web Dataset CSV", 
            command=self._open_web_scrape_modal,
            fg_color="#2A3C50", hover_color="#3B526D"
        )
        self.web_scrape_btn.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        # FAISS Index Status Card
        self.status_card = ctk.CTkFrame(self.sidebar, fg_color="#1E2A38", corner_radius=10)
        self.status_card.grid(row=6, column=0, padx=20, pady=15, sticky="ew")

        self.status_title = ctk.CTkLabel(self.status_card, text="📊 Index Statistics", font=ctk.CTkFont(size=13, weight="bold"))
        self.status_title.pack(anchor="w", padx=12, pady=(10, 5))

        self.stat_chunks_label = ctk.CTkLabel(self.status_card, text="Indexed Chunks: 0", font=ctk.CTkFont(size=12), text_color="#A0AAB2")
        self.stat_chunks_label.pack(anchor="w", padx=12, pady=2)

        self.stat_vector_label = ctk.CTkLabel(self.status_card, text=f"FAISS Status: {'Active (Disk Fast)' if FAISS_AVAILABLE else 'TF-IDF Fallback'}", font=ctk.CTkFont(size=12), text_color="#00E676")
        self.stat_vector_label.pack(anchor="w", padx=12, pady=2)

        self.stat_embed_label = ctk.CTkLabel(
            self.status_card, 
            text="Embedder: Loading Async..." if self.embedder.is_loading else "Embedder: Ready", 
            font=ctk.CTkFont(size=11), 
            text_color="#FFAB00" if self.embedder.is_loading else "#00E676"
        )
        self.stat_embed_label.pack(anchor="w", padx=12, pady=(2, 10))

        # Model Info
        model_label = ctk.CTkLabel(self.sidebar, text=f"🤖 Model: Llama 3 70B Versatile\n🔑 Groq API: Active\n💾 Disk Cache: Instant", font=ctk.CTkFont(size=11), text_color="#6C7A89", justify="left")
        model_label.grid(row=9, column=0, padx=20, pady=20, sticky="sw")

        # Main Tab View Container
        self.tabview = ctk.CTkTabview(self, corner_radius=12)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.tab_chat = self.tabview.add("💬 RAG Question Answering")
        self.tab_context = self.tabview.add("🔍 Vector Context Inspector")
        self.tab_settings = self.tabview.add("⚙️ Closed-Book Prompt & Rules")

        self._build_chat_tab()
        self._build_context_tab()
        self._build_settings_tab()

    def _build_chat_tab(self):
        self.tab_chat.grid_columnconfigure(0, weight=1)
        self.tab_chat.grid_rowconfigure(3, weight=1)

        # Header Info Banner
        header_frame = ctk.CTkFrame(self.tab_chat, fg_color="#18222D", corner_radius=10)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        info_lbl = ctk.CTkLabel(
            header_frame, 
            text="🎯 Project 3: Context-Anchored Closed-Book Answering System",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00D2FF"
        )
        info_lbl.pack(anchor="w", padx=15, pady=(10, 2))

        desc_lbl = ctk.CTkLabel(
            header_frame,
            text="Restricts LLM to exclusively use FAISS vector chunks. If missing, responds 'Information Not Found'. Citations required.",
            font=ctk.CTkFont(size=12),
            text_color="#95A5A6"
        )
        desc_lbl.pack(anchor="w", padx=15, pady=(0, 10))

        # Query Presets & Domain Suggestions Toolbar
        preset_frame = ctk.CTkFrame(self.tab_chat, fg_color="#1F2937", corner_radius=10)
        preset_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        preset_top = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_top.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(preset_top, text="💡 Quick Tests:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 10))

        btn_valid = ctk.CTkButton(
            preset_top, text="✅ Valid In-Context Q", height=26,
            command=lambda: self._set_query("How do superconducting quantum processors stay cold?", auto_run=True),
            fg_color="#1E3A8A", hover_color="#2563EB"
        )
        btn_valid.pack(side="left", padx=5)

        btn_invalid = ctk.CTkButton(
            preset_top, text="❌ Out-of-Context Q (Hallucination Test)", height=26,
            command=lambda: self._set_query("What is the capital city of Australia and its population?", auto_run=True),
            fg_color="#831843", hover_color="#BE185D"
        )
        btn_invalid.pack(side="left", padx=5)

        # Domain Specific Suggestions Container
        self.suggestions_container = ctk.CTkFrame(preset_frame, fg_color="transparent")
        self.suggestions_container.pack(fill="x", padx=10, pady=(0, 8))

        self._update_domain_suggestions(self.current_dataset_name)

        # Output Display Area
        output_container = ctk.CTkFrame(self.tab_chat, fg_color="#111827", corner_radius=10)
        output_container.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        output_container.grid_columnconfigure(0, weight=1)
        output_container.grid_rowconfigure(1, weight=1)

        # Citation Verification Badge Header
        badge_frame = ctk.CTkFrame(output_container, fg_color="#1F2937", height=40, corner_radius=8)
        badge_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.badge_status = ctk.CTkLabel(
            badge_frame, 
            text="STATUS: READY", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#9CA3AF"
        )
        self.badge_status.pack(side="left", padx=15)

        self.citation_count_lbl = ctk.CTkLabel(
            badge_frame,
            text="Citations Detected: 0",
            font=ctk.CTkFont(size=12),
            text_color="#D1D5DB"
        )
        self.citation_count_lbl.pack(side="right", padx=15)

        # Response Text Box
        self.response_text = ctk.CTkTextbox(
            output_container, 
            font=ctk.CTkFont(family="Consolas", size=14),
            wrap="word",
            fg_color="#0F172A",
            text_color="#F3F4F6",
            border_color="#1E293B",
            border_width=1
        )
        self.response_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Input Query Controls
        input_frame = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        input_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.query_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Enter your question to test Context-Anchored Closed-Book RAG...",
            font=ctk.CTkFont(size=14),
            height=45
        )
        self.query_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.query_entry.bind("<Return>", lambda e: self._on_run_query())

        self.run_btn = ctk.CTkButton(
            input_frame, 
            text="🚀 Query RAG", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=140,
            command=self._on_run_query,
            fg_color="#2563EB", hover_color="#1D4ED8"
        )
        self.run_btn.grid(row=0, column=1, sticky="e")

    def _update_domain_suggestions(self, dataset_name: str):
        for btn in self.suggestion_buttons:
            btn.destroy()
        self.suggestion_buttons.clear()

        lbl = ctk.CTkLabel(self.suggestions_container, text="📌 3 Domain Suggestions:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8")
        lbl.pack(side="left", padx=(0, 10))
        self.suggestion_buttons.append(lbl)

        questions = DOMAIN_SUGGESTIONS.get(dataset_name, [
            "What main information is included in this document?",
            "Summarize key technical points with exact citations.",
            "List specific parameters or facts mentioned in the text."
        ])

        for q in questions:
            short_q = q[:35] + "..." if len(q) > 35 else q
            btn = ctk.CTkButton(
                self.suggestions_container,
                text=f"❓ {short_q}",
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color="#374151", hover_color="#4B5563",
                command=lambda question=q: self._set_query(question, auto_run=True)
            )
            btn.pack(side="left", padx=4)
            self.suggestion_buttons.append(btn)

    def _build_context_tab(self):
        self.tab_context.grid_columnconfigure(0, weight=1)
        self.tab_context.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.tab_context,
            text="🔎 Top Vector Chunks Injected into Llama 3 70B System Prompt",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#38BDF8"
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.context_textbox = ctk.CTkTextbox(
            self.tab_context,
            font=ctk.CTkFont(family="Consolas", size=13),
            wrap="word",
            fg_color="#0B0F19",
            text_color="#E2E8F0"
        )
        self.context_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def _build_settings_tab(self):
        self.tab_settings.grid_columnconfigure(0, weight=1)
        self.tab_settings.grid_rowconfigure(4, weight=1)

        toggle_frame = ctk.CTkFrame(self.tab_settings, fg_color="#1E293B", corner_radius=10)
        toggle_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.switch_strict = ctk.CTkSwitch(
            toggle_frame,
            text="Strict Closed-Book Mode (Force 'Information Not Found' when text missing)",
            variable=self.strict_mode,
            font=ctk.CTkFont(size=13, weight="bold"),
            progress_color="#2563EB"
        )
        self.switch_strict.pack(anchor="w", padx=15, pady=12)

        slider_frame = ctk.CTkFrame(self.tab_settings, fg_color="#1E293B", corner_radius=10)
        slider_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        topk_label_txt = ctk.CTkLabel(slider_frame, text=f"Top-K FAISS Chunks to Retrieve: {self.top_k_var.get()}", font=ctk.CTkFont(size=13, weight="bold"))
        topk_label_txt.pack(anchor="w", padx=15, pady=(10, 2))

        def update_topk_lbl(val):
            topk_label_txt.configure(text=f"Top-K FAISS Chunks to Retrieve: {int(val)}")

        slider_topk = ctk.CTkSlider(slider_frame, from_=1, to=10, number_of_steps=9, variable=self.top_k_var, command=update_topk_lbl)
        slider_topk.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(self.tab_settings, text="📜 Live System Prompt Template:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=3, column=0, padx=10, pady=(10, 5), sticky="w")

        self.prompt_text_edit = ctk.CTkTextbox(
            self.tab_settings,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0F172A",
            text_color="#94A3B8"
        )
        self.prompt_text_edit.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        self.prompt_text_edit.insert("1.0", DEFAULT_CLOSED_BOOK_SYSTEM_PROMPT)

    # Core Operations
    def _set_query(self, text: str, auto_run: bool = False):
        self.query_entry.delete(0, "end")
        self.query_entry.insert(0, text)
        if auto_run:
            self._on_run_query()

    def _on_dataset_select(self, choice: str):
        self.current_dataset_name = choice
        self._update_domain_suggestions(choice)
        self._load_sample_dataset(choice)

    def _load_sample_dataset(self, name: str):
        self.vector_store.clear()
        
        # Load instantly from disk cache!
        if self.vector_store.load_from_disk(name):
            self._update_index_stats(f"Loaded '{name}' (Instant Disk Cache)")
            return

        csv_str = SAMPLE_DATASETS.get(name, "")
        if not csv_str:
            return

        df = pd.read_csv(io.StringIO(csv_str))
        chunk_list = []
        for idx, row in df.iterrows():
            para_text = str(row['paragraph_text'])
            cid = f"[Paragraph {row['id']}]"
            src = str(row.get('source', 'Dataset.csv'))
            chunk_list.append({
                'id': row['id'],
                'paragraph': para_text,
                'citation_id': cid,
                'source': src
            })

        self.vector_store.add_chunks(chunk_list, cache_key=name)
        self._update_index_stats(f"Loaded and Cached '{name}'")

    def _upload_custom_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text & CSV Files", "*.csv *.txt"), ("CSV Files", "*.csv"), ("Text Files", "*.txt")])
        if not file_path:
            return

        try:
            filename = os.path.basename(file_path)
            chunk_list = []

            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                text_col = None
                for col in df.columns:
                    if 'text' in col.lower() or 'content' in col.lower() or 'paragraph' in col.lower() or 'desc' in col.lower():
                        text_col = col
                        break
                if not text_col:
                    text_col = df.columns[0]

                for idx, row in df.iterrows():
                    chunk_list.append({
                        'id': idx + 1,
                        'paragraph': str(row[text_col]),
                        'citation_id': f"[Source: {filename} Row {idx + 1}]",
                        'source': filename
                    })
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                for idx, p in enumerate(paragraphs):
                    chunk_list.append({
                        'id': idx + 1,
                        'paragraph': p,
                        'citation_id': f"[Paragraph {idx + 1}]",
                        'source': filename
                    })

            self.vector_store.clear()
            self.vector_store.add_chunks(chunk_list, cache_key=filename)
            self._update_index_stats(f"Loaded custom file '{filename}'")
            messagebox.showinfo("Success", f"Successfully indexed & cached {len(chunk_list)} chunks from '{filename}' into FAISS Vector DB!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def _open_web_scrape_modal(self):
        dialog = ctk.CTkInputDialog(text="Enter URL of a webpage or raw CSV file to scrape and index:", title="Web Dataset Scraper")
        url = dialog.get_input()
        if not url:
            return

        def scrape_worker():
            try:
                self.stat_chunks_label.configure(text="Scraping Web Dataset...")
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()

                chunk_list = []
                if url.endswith('.csv') or 'csv' in resp.headers.get('Content-Type', ''):
                    df = pd.read_csv(io.StringIO(resp.text))
                    for idx, row in df.iterrows():
                        text_val = " ".join([str(v) for v in row.values if pd.notna(v)])
                        chunk_list.append({
                            'id': idx + 1,
                            'paragraph': text_val,
                            'citation_id': f"[Web CSV Row {idx + 1}]",
                            'source': url
                        })
                else:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    paras = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 30]
                    for idx, p in enumerate(paras):
                        chunk_list.append({
                            'id': idx + 1,
                            'paragraph': p,
                            'citation_id': f"[Web Paragraph {idx + 1}]",
                            'source': url
                        })

                if not chunk_list:
                    raise ValueError("No valid text paragraphs or table rows found at URL.")

                cache_key = url.split('/')[-1] or "web_scraped_data"
                self.vector_store.clear()
                self.vector_store.add_chunks(chunk_list, cache_key=cache_key)
                self.after(0, lambda: self._update_index_stats(f"Scraped Web Dataset ({len(chunk_list)} chunks)"))
                self.after(0, lambda: messagebox.showinfo("Scrape Complete", f"Successfully indexed & cached {len(chunk_list)} chunks from web URL!"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Scrape Error", f"Failed to scrape web dataset: {e}"))
                self.after(0, lambda: self._update_index_stats("Scrape Failed"))

        threading.Thread(target=scrape_worker, daemon=True).start()

    def _update_index_stats(self, msg: str = ""):
        total = len(self.vector_store.chunks)
        self.stat_chunks_label.configure(text=f"Indexed Chunks: {total}")

    def _on_run_query(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a question.")
            return

        self.run_btn.configure(state="disabled", text="⚡ Processing...")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", "🔍 Searching FAISS Vector Index and prompting Llama 3 70B...\n")
        self.badge_status.configure(text="STATUS: QUERYING FAISS & GROQ", text_color="#FFAB00")

        threading.Thread(target=self._execute_rag_pipeline, args=(query,), daemon=True).start()

    def _execute_rag_pipeline(self, query: str):
        try:
            top_k = self.top_k_var.get()
            retrieved = self.vector_store.search(query, top_k=top_k)

            context_blocks = []
            for item in retrieved:
                cid = item.get('citation_id', f"[Paragraph {item['id']}]")
                context_blocks.append(f"{cid}: {item['paragraph']}")

            context_text = "\n\n".join(context_blocks) if context_blocks else "No relevant context found in database."

            self.after(0, lambda: self._update_context_inspector(query, retrieved, context_text))

            sys_template = self.prompt_text_edit.get("1.0", "end").strip()
            system_prompt = sys_template.format(context_text=context_text)

            start_time = time.time()
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,
                max_tokens=1024
            )
            elapsed = time.time() - start_time
            ans_content = response.choices[0].message.content.strip()

            self.after(0, lambda: self._render_response(ans_content, elapsed))

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self._render_error(err_msg))

    def _update_context_inspector(self, query: str, chunks: list[dict], context_text: str):
        self.context_textbox.delete("1.0", "end")
        header = f"QUERY: '{query}'\nRETRIEVED {len(chunks)} FAISS VECTOR CHUNKS:\n" + "="*70 + "\n\n"
        self.context_textbox.insert("1.0", header)

        for i, c in enumerate(chunks):
            chunk_info = f"--- Chunk {i+1} --- | Similarity Score: {c.get('score', 0.0):.4f} | Citation ID: {c.get('citation_id')}\n"
            chunk_info += f"Source: {c.get('source', 'N/A')}\n"
            chunk_info += f"Text: {c.get('paragraph')}\n\n"
            self.context_textbox.insert("end", chunk_info)

    def _render_response(self, content: str, elapsed: float):
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", content + f"\n\n\n[Latency: {elapsed:.2f}s | Model: {self.model_name}]")

        if "Information Not Found" in content:
            self.badge_status.configure(text="STATUS: ⛔ INFORMATION NOT FOUND (Strict Negative Constraint Triggered)", text_color="#EF4444")
            self.citation_count_lbl.configure(text="Citations: 0 (No Match)", text_color="#EF4444")
        else:
            citations = re.findall(r'\[Paragraph \d+\]|\[Source: [^\]]+\]|\[Web [^\]]+\]', content)
            count = len(citations)
            if count > 0:
                self.badge_status.configure(text="STATUS: ✅ CONTEXT-ANCHORED (Valid Paragraph Citations)", text_color="#10B981")
                self.citation_count_lbl.configure(text=f"Citations Detected: {count} {set(citations)}", text_color="#10B981")
            else:
                self.badge_status.configure(text="STATUS: ⚠️ UNANCHORED / MISSING CITATION", text_color="#F59E0B")
                self.citation_count_lbl.configure(text="Citations: None Detected", text_color="#F59E0B")

        self.run_btn.configure(state="normal", text="🚀 Query RAG")

    def _render_error(self, err: str):
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", f"❌ API / Pipeline Error: {err}")
        self.badge_status.configure(text="STATUS: ERROR", text_color="#EF4444")
        self.run_btn.configure(state="normal", text="🚀 Query RAG")

if __name__ == "__main__":
    app = RAGApplication()
    app.mainloop()
