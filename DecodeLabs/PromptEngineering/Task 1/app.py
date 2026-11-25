import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import urllib.request
import urllib.error
import threading
import time
import re

# Hardcoded Groq API Key as requested
GROQ_API_KEY = ""
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_MODEL = "llama-3.3-70b-versatile"
MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

# Preset unstructured data examples
SAMPLE_DATASETS = {
    "Medical Consultation Note": {
        "text": """PATIENT CLINICAL SUMMARY
Date: 12/05/2025
Patient Name: Johnathan Vance, DOB: 04/18/1982
Vitals: BP 138/88, HR 82 bpm, Temp 98.6F, SpO2 97%
Chief Complaint: Patient reports experiencing persistent low back pain radiating down the left leg for 3 weeks, scale 6/10.
Assessment & Plan: Lumbar radiculopathy suspected. Prescribed Ibuprofen 600mg TID p.r.n. and ordered Lumbar MRI. Follow-up scheduled in 2 weeks.""",
        "schema": '{\n  "patient_name": "string",\n  "dob": "YYYY-MM-DD",\n  "consultation_date": "YYYY-MM-DD",\n  "vitals": {\n    "bp": "string",\n    "hr_bpm": "number",\n    "spo2": "string"\n  },\n  "diagnosis": "string",\n  "medication": "string",\n  "follow_up_weeks": "number"\n}',
        "few_shots": [
            {
                "input": "PATIENT CLINICAL SUMMARY\nDate: 01/10/2025\nPatient Name: Sarah Connor, DOB: 09/12/1975\nVitals: BP 120/80, HR 70 bpm, Temp 98.2F, SpO2 99%\nChief Complaint: Mild tension headache.\nAssessment & Plan: Tension headache. Advised rest and Paracetamol 500mg as needed.",
                "output": '{\n  "patient_name": "Sarah Connor",\n  "dob": "1975-09-12",\n  "consultation_date": "2025-01-10",\n  "vitals": {\n    "bp": "120/80",\n    "hr_bpm": 70,\n    "spo2": "99%"\n  },\n  "diagnosis": "Tension headache",\n  "medication": "Paracetamol 500mg",\n  "follow_up_weeks": 0\n}'
            }
        ]
    },
    "E-Commerce Order Email": {
        "text": """From: support@techmart.com
Subject: Confirmation for Order #TM-994821
Date: Aug 8, 2026

Hi Alex,
Thanks for ordering! Here is your purchase summary:
Item 1: UltraWide Monitor 34" - Qty: 1 - Price: $499.99
Item 2: Mechanical Wireless Keyboard - Qty: 2 - Price: $89.50 each
Shipping Fee: $15.00
Tax: $54.32
Total Amount Billed: $748.31
Shipping Address: 742 Evergreen Terrace, Springfield, OR 97477
Estimated Delivery: Aug 12, 2026.""",
        "schema": '{\n  "order_id": "string",\n  "customer_name": "string",\n  "items": [\n    {\n      "product_name": "string",\n      "quantity": "number",\n      "unit_price": "number"\n    }\n  ],\n  "shipping_fee": "number",\n  "tax": "number",\n  "total_amount": "number",\n  "shipping_city": "string"\n}',
        "few_shots": [
            {
                "input": "From: billing@books.com\nOrder #BK-102\nHi Maria,\nYou bought: 1x Python Handbook for $30.00, Shipping: $5.00. Total: $35.00 to Seattle, WA.",
                "output": '{\n  "order_id": "BK-102",\n  "customer_name": "Maria",\n  "items": [\n    {\n      "product_name": "Python Handbook",\n      "quantity": 1,\n      "unit_price": 30.00\n    }\n  ],\n  "shipping_fee": 5.00,\n  "tax": 0.00,\n  "total_amount": 35.00,\n  "shipping_city": "Seattle"\n}'
            }
        ]
    },
    "Customer Support Feedback": {
        "text": """Ticket ID: TCK-40291 | Created: 2026-08-01
User: dev_guru_99 (Priority: Premium)
Category: Billing / Refund Request
Message: I was charged twice for subscription renewal on July 29th ($29.99 x 2). Requesting immediate refund of the duplicate $29.99 charge. Very frustrated with the delay in support response!
Sentiment: Negative
Assigned Agent: TechOps Lead""",
        "schema": '{\n  "ticket_id": "string",\n  "username": "string",\n  "user_tier": "string",\n  "category": "string",\n  "issue_summary": "string",\n  "requested_refund_amount": "number",\n  "urgency_level": "High | Medium | Low",\n  "sentiment": "Positive | Neutral | Negative"\n}',
        "few_shots": [
            {
                "input": "Ticket ID: TCK-101 | User: alice_w | Category: Feature Request\nLove the new UI! Can you add dark mode to exported PDFs? Thanks!",
                "output": '{\n  "ticket_id": "TCK-101",\n  "username": "alice_w",\n  "user_tier": "Standard",\n  "category": "Feature Request",\n  "issue_summary": "Add dark mode option for exported PDF documents",\n  "requested_refund_amount": 0.00,\n  "urgency_level": "Low",\n  "sentiment": "Positive"\n}'
            }
        ]
    }
}

class ModernApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Groq Llama 3.3 70B - Zero-Shot & Few-Shot Data Extractor")
        self.geometry("1300x860")
        self.minsize(1100, 750)
        
        # UI Color Palette (Dark Futuristic Modern Theme)
        self.colors = {
            "bg_dark": "#0b0f19",
            "bg_card": "#151c2c",
            "bg_card_alt": "#1a233a",
            "border": "#27354e",
            "primary": "#6366f1",
            "primary_hover": "#4f46e5",
            "accent_teal": "#06b6d4",
            "accent_emerald": "#10b981",
            "accent_amber": "#f59e0b",
            "text_main": "#f8fafc",
            "text_muted": "#94a3b8",
            "json_key": "#a78bfa",
            "json_str": "#34d399",
            "json_num": "#fbbf24",
            "json_bool": "#f472b6"
        }
        
        self.configure(bg=self.colors["bg_dark"])
        
        # Application Variables
        self.mode_var = tk.StringVar(value="Few-Shot")
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        self.temp_var = tk.DoubleVar(value=0.0)
        self.delimiter_var = tk.StringVar(value='"""')
        self.is_processing = False
        self.animation_step = 0
        
        self._init_styles()
        self._build_ui()
        self._load_sample("Medical Consultation Note")

    def _init_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Customizing TTK styles
        self.style.configure(".", background=self.colors["bg_dark"], foreground=self.colors["text_main"], font=("Segoe UI", 10))
        self.style.configure("TFrame", background=self.colors["bg_dark"])
        self.style.configure("Card.TFrame", background=self.colors["bg_card"], relief="flat")
        
        self.style.configure("TLabel", background=self.colors["bg_card"], foreground=self.colors["text_main"], font=("Segoe UI", 10))
        self.style.configure("Muted.TLabel", background=self.colors["bg_card"], foreground=self.colors["text_muted"], font=("Segoe UI", 9))
        self.style.configure("Title.TLabel", background=self.colors["bg_card"], foreground=self.colors["text_main"], font=("Segoe UI", 12, "bold"))
        
        self.style.configure("TCombobox", fieldbackground=self.colors["bg_card_alt"], background=self.colors["border"], foreground=self.colors["text_main"])
        self.style.map("TCombobox", fieldbackground=[('readonly', self.colors["bg_card_alt"])], selectbackground=[('readonly', self.colors["primary"])])

    def _create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors["bg_card"], height=70)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Banner bar with decorative left accent border
        accent_bar = tk.Frame(header_frame, bg=self.colors["primary"], width=6)
        accent_bar.pack(side="left", fill="y")
        
        content = tk.Frame(header_frame, bg=self.colors["bg_card"])
        content.pack(side="left", fill="both", expand=True, padx=20, pady=12)
        
        title_label = tk.Label(content, text="⚡ Zero-Shot & Few-Shot Data Extractor", font=("Segoe UI", 16, "bold"), fg=self.colors["text_main"], bg=self.colors["bg_card"])
        title_label.pack(anchor="w")
        
        subtitle = tk.Label(content, text="Powered by Groq LLM (Llama 3.3 70B Versatile) • Structured JSON Engine", font=("Segoe UI", 9), fg=self.colors["accent_teal"], bg=self.colors["bg_card"])
        subtitle.pack(anchor="w", pady=(2, 0))
        
        # Status Pill Indicator
        self.status_pill = tk.Label(header_frame, text="● READY", font=("Segoe UI", 9, "bold"), fg=self.colors["accent_emerald"], bg=self.colors["bg_card_alt"], padx=12, pady=6)
        self.status_pill.pack(side="right", padx=20)

    def _build_ui(self):
        main_container = tk.Frame(self, bg=self.colors["bg_dark"])
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._create_header(main_container)
        
        # Two-column layout
        paned = tk.PanedWindow(main_container, orient=tk.HORIZONTAL, bg=self.colors["bg_dark"], bd=0, sashwidth=6)
        paned.pack(fill="both", expand=True)
        
        left_panel = tk.Frame(paned, bg=self.colors["bg_dark"])
        right_panel = tk.Frame(paned, bg=self.colors["bg_dark"])
        
        paned.add(left_panel)
        paned.add(right_panel)
        
        # LEFT PANEL: Controls, Unstructured Text, Schema, Few-shot Examples
        self._build_left_panel(left_panel)
        
        # RIGHT PANEL: Prompt Construction Preview, Output JSON & Statistics
        self._build_right_panel(right_panel)

    def _build_left_panel(self, parent):
        # 1. Preset & Configuration Card
        cfg_card = tk.Frame(parent, bg=self.colors["bg_card"], highlightbackground=self.colors["border"], highlightthickness=1)
        cfg_card.pack(fill="x", pady=(0, 10), ipady=8, ipadx=10)
        
        lbl_cfg = tk.Label(cfg_card, text="⚙️ Extraction Configuration & Presets", font=("Segoe UI", 11, "bold"), fg=self.colors["text_main"], bg=self.colors["bg_card"])
        lbl_cfg.pack(anchor="w", padx=10, pady=(6, 8))
        
        # Row 1: Preset loader & Model selector
        r1 = tk.Frame(cfg_card, bg=self.colors["bg_card"])
        r1.pack(fill="x", padx=10, pady=2)
        
        tk.Label(r1, text="Sample Preset:", bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(side="left")
        self.cb_preset = ttk.Combobox(r1, values=list(SAMPLE_DATASETS.keys()), state="readonly", width=24)
        self.cb_preset.set("Medical Consultation Note")
        self.cb_preset.pack(side="left", padx=(6, 15))
        self.cb_preset.bind("<<ComboboxSelected>>", self._on_preset_change)
        
        tk.Label(r1, text="Model:", bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(side="left")
        self.cb_model = ttk.Combobox(r1, textvariable=self.model_var, values=MODELS, state="readonly", width=22)
        self.cb_model.pack(side="left", padx=6)
        
        # Row 2: Mode (Zero vs Few-Shot), Temp slider, Delimiter
        r2 = tk.Frame(cfg_card, bg=self.colors["bg_card"])
        r2.pack(fill="x", padx=10, pady=(8, 4))
        
        tk.Label(r2, text="Prompt Mode:", bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(side="left")
        
        rb_few = tk.Radiobutton(r2, text="Few-Shot (2-3 Examples)", variable=self.mode_var, value="Few-Shot", bg=self.colors["bg_card"], fg=self.colors["accent_teal"], selectcolor=self.colors["bg_card_alt"], activebackground=self.colors["bg_card"], command=self._update_prompt_preview)
        rb_few.pack(side="left", padx=4)
        
        rb_zero = tk.Radiobutton(r2, text="Zero-Shot", variable=self.mode_var, value="Zero-Shot", bg=self.colors["bg_card"], fg=self.colors["accent_amber"], selectcolor=self.colors["bg_card_alt"], activebackground=self.colors["bg_card"], command=self._update_prompt_preview)
        rb_zero.pack(side="left", padx=4)
        
        # Temp slider
        tk.Label(r2, text="Temp:", bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(side="left", padx=(15, 2))
        self.lbl_temp_val = tk.Label(r2, text="0.0", fg=self.colors["primary"], bg=self.colors["bg_card"], font=("Segoe UI", 9, "bold"))
        self.lbl_temp_val.pack(side="right", padx=(2, 0))
        
        slider_temp = tk.Scale(r2, from_=0.0, to=1.0, resolution=0.05, orient="horizontal", variable=self.temp_var, showvalue=False, bg=self.colors["bg_card"], highlightthickness=0, troughcolor=self.colors["bg_card_alt"], activebackground=self.colors["primary"], length=80, command=lambda v: self.lbl_temp_val.config(text=f"{float(v):.2f}"))
        slider_temp.pack(side="right")
        
        # Delimiter input
        tk.Label(r2, text="Delimiter:", bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(side="left", padx=(15, 2))
        entry_del = tk.Entry(r2, textvariable=self.delimiter_var, width=6, bg=self.colors["bg_card_alt"], fg=self.colors["text_main"], insertbackground="white", bd=1, relief="solid")
        entry_del.pack(side="left")
        entry_del.bind("<KeyRelease>", lambda e: self._update_prompt_preview())

        # Notebook for Raw Input, Target Schema, Few-shot Editor
        nb_left = ttk.Notebook(parent)
        nb_left.pack(fill="both", expand=True, pady=(0, 10))
        
        # Tab 1: Messy Raw Input
        f_raw = tk.Frame(nb_left, bg=self.colors["bg_card"])
        nb_left.add(f_raw, text=" 📝 Messy Input Text ")
        
        self.txt_raw = tk.Text(f_raw, bg=self.colors["bg_dark"], fg=self.colors["text_main"], font=("Consolas", 10), bd=0, padx=10, pady=10, insertbackground="white", selectbackground=self.colors["primary"])
        self.txt_raw.pack(fill="both", expand=True)
        self.txt_raw.bind("<KeyRelease>", lambda e: self._update_prompt_preview())

        # Tab 2: Target JSON Schema
        f_schema = tk.Frame(nb_left, bg=self.colors["bg_card"])
        nb_left.add(f_schema, text=" 📐 Target JSON Schema ")
        
        self.txt_schema = tk.Text(f_schema, bg=self.colors["bg_dark"], fg=self.colors["text_main"], font=("Consolas", 10), bd=0, padx=10, pady=10, insertbackground="white", selectbackground=self.colors["primary"])
        self.txt_schema.pack(fill="both", expand=True)
        self.txt_schema.bind("<KeyRelease>", lambda e: self._update_prompt_preview())

        # Tab 3: Few-Shot Examples Manager
        f_fewshots = tk.Frame(nb_left, bg=self.colors["bg_card"])
        nb_left.add(f_fewshots, text=" 🎯 Few-Shot Examples (In-Prompt) ")
        
        lbl_fs = tk.Label(f_fewshots, text="Sample Input / Output Pairs passed to LLM for Few-Shot Learning:", bg=self.colors["bg_card"], fg=self.colors["text_muted"], font=("Segoe UI", 9, "italic"))
        lbl_fs.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.txt_fewshots = tk.Text(f_fewshots, bg=self.colors["bg_dark"], fg=self.colors["text_main"], font=("Consolas", 9), bd=0, padx=10, pady=10, insertbackground="white")
        self.txt_fewshots.pack(fill="both", expand=True)
        self.txt_fewshots.bind("<KeyRelease>", lambda e: self._update_prompt_preview())

        # Run Button Bar
        btn_frame = tk.Frame(parent, bg=self.colors["bg_dark"])
        btn_frame.pack(fill="x")
        
        self.btn_extract = tk.Button(btn_frame, text="⚡ EXTRACT DATA TO JSON NOW", font=("Segoe UI", 11, "bold"), fg="white", bg=self.colors["primary"], activebackground=self.colors["primary_hover"], activeforeground="white", bd=0, pady=10, cursor="hand2", command=self.run_extraction)
        self.btn_extract.pack(fill="x")

    def _build_right_panel(self, parent):
        nb_right = ttk.Notebook(parent)
        nb_right.pack(fill="both", expand=True)
        
        # Tab 1: Extracted JSON Output
        f_out = tk.Frame(nb_right, bg=self.colors["bg_card"])
        nb_right.add(f_out, text=" ✨ Structured JSON Output ")
        
        # Top info toolbar for Output
        out_bar = tk.Frame(f_out, bg=self.colors["bg_card_alt"], height=35)
        out_bar.pack(fill="x")
        
        self.lbl_json_status = tk.Label(out_bar, text="STATUS: Idle", font=("Segoe UI", 9, "bold"), fg=self.colors["text_muted"], bg=self.colors["bg_card_alt"], padx=10)
        self.lbl_json_status.pack(side="left")
        
        self.lbl_metrics = tk.Label(out_bar, text="", font=("Segoe UI", 9), fg=self.colors["accent_teal"], bg=self.colors["bg_card_alt"])
        self.lbl_metrics.pack(side="left", padx=10)
        
        btn_copy = tk.Button(out_bar, text="📋 Copy JSON", font=("Segoe UI", 9), bg=self.colors["border"], fg=self.colors["text_main"], bd=0, padx=8, cursor="hand2", command=self._copy_output)
        btn_copy.pack(side="right", padx=5, pady=4)
        
        btn_save = tk.Button(out_bar, text="💾 Save", font=("Segoe UI", 9), bg=self.colors["border"], fg=self.colors["text_main"], bd=0, padx=8, cursor="hand2", command=self._save_output)
        btn_save.pack(side="right", padx=5, pady=4)
        
        # Text output area with syntax highlighting
        self.txt_output = tk.Text(f_out, bg="#080c14", fg=self.colors["text_main"], font=("Consolas", 10, "bold"), bd=0, padx=12, pady=12, insertbackground="white", selectbackground=self.colors["primary"])
        self.txt_output.pack(fill="both", expand=True)
        
        # Configure tags for JSON styling
        self.txt_output.tag_configure("key", foreground=self.colors["json_key"])
        self.txt_output.tag_configure("string", foreground=self.colors["json_str"])
        self.txt_output.tag_configure("number", foreground=self.colors["json_num"])
        self.txt_output.tag_configure("boolean", foreground=self.colors["json_bool"])
        self.txt_output.tag_configure("error", foreground=self.colors["accent_amber"])

        # Tab 2: Prompt Sent to LLM (Full Inspection)
        f_prompt_view = tk.Frame(nb_right, bg=self.colors["bg_card"])
        nb_right.add(f_prompt_view, text=" 👁️ Inspected LLM Prompt ")
        
        lbl_pv = tk.Label(f_prompt_view, text="Exact constructed prompt sent to Groq Llama 3.3 70B (Strict Delimiters & Rules):", bg=self.colors["bg_card"], fg=self.colors["text_muted"], font=("Segoe UI", 9, "italic"))
        lbl_pv.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.txt_prompt_inspect = tk.Text(f_prompt_view, bg=self.colors["bg_dark"], fg=self.colors["accent_teal"], font=("Consolas", 9), bd=0, padx=10, pady=10, insertbackground="white")
        self.txt_prompt_inspect.pack(fill="both", expand=True)

    def _on_preset_change(self, event=None):
        name = self.cb_preset.get()
        if name in SAMPLE_DATASETS:
            self._load_sample(name)

    def _load_sample(self, name):
        ds = SAMPLE_DATASETS[name]
        self.txt_raw.delete("1.0", tk.END)
        self.txt_raw.insert(tk.END, ds["text"])
        
        self.txt_schema.delete("1.0", tk.END)
        self.txt_schema.insert(tk.END, ds["schema"])
        
        # Load few-shots formatting
        fs_str = ""
        for i, example in enumerate(ds["few_shots"], 1):
            fs_str += f"--- EXAMPLE {i} ---\nINPUT:\n{example['input']}\n\nOUTPUT JSON:\n{example['output']}\n\n"
        
        self.txt_fewshots.delete("1.0", tk.END)
        self.txt_fewshots.insert(tk.END, fs_str.strip())
        
        self._update_prompt_preview()

    def _construct_prompt(self):
        raw_text = self.txt_raw.get("1.0", tk.END).strip()
        schema_text = self.txt_schema.get("1.0", tk.END).strip()
        fewshot_text = self.txt_fewshots.get("1.0", tk.END).strip()
        delim = self.delimiter_var.get().strip() or '"""'
        mode = self.mode_var.get()
        
        system_instruction = f"""You are a precise, deterministic data extraction AI engine.
Your sole mission is to extract structured information from unstructured raw input text according to the target JSON schema provided.

STRICT RULES:
1. Output ONLY a single valid JSON object adhering strictly to the requested schema.
2. DO NOT output any markdown headers, conversational text, introduction, or postscript (e.g. NEVER write "Here is your JSON!").
3. Do not invent facts not contained within the raw text. Use null or empty values if data is missing.
4. Ensure the output is syntactically valid JSON parseable by standard JSON parsers."""

        prompt = ""
        if mode == "Few-Shot" and fewshot_text:
            prompt += f"FEW-SHOT EXAMPLES FOR REFERENCE:\n{fewshot_text}\n\n=========================================\n\n"
        
        prompt += f"""TARGET JSON SCHEMA STRUCTURE:
{schema_text}

INSTRUCTIONS:
Extract all fields from the RAW UNSTRUCTURED TEXT below delimited by {delim} and map them into the requested JSON schema structure above.

RAW UNSTRUCTURED TEXT:
{delim}
{raw_text}
{delim}

JSON OUTPUT:"""
        return system_instruction, prompt

    def _update_prompt_preview(self):
        sys_inst, user_prompt = self._construct_prompt()
        full_inspect = f"=== SYSTEM INSTRUCTION ===\n{sys_inst}\n\n=== USER PROMPT ===\n{user_prompt}"
        
        self.txt_prompt_inspect.delete("1.0", tk.END)
        self.txt_prompt_inspect.insert(tk.END, full_inspect)

    def _animate_pulse(self):
        if not self.is_processing:
            return
        
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        char = dots[self.animation_step % len(dots)]
        self.animation_step += 1
        
        self.status_pill.config(text=f"{char} EXTRACTING VIA GROQ...", fg=self.colors["accent_amber"])
        self.after(100, self._animate_pulse)

    def run_extraction(self):
        if self.is_processing:
            return
        
        raw_text = self.txt_raw.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Empty Input", "Please enter or select some unstructured text to extract.")
            return

        self.is_processing = True
        self.btn_extract.config(state="disabled", text="⏳ EXTRACTING JSON...", bg=self.colors["border"])
        self.lbl_json_status.config(text="STATUS: Querying Groq LLM...", fg=self.colors["accent_amber"])
        self.txt_output.delete("1.0", tk.END)
        self._animate_pulse()
        
        sys_prompt, user_prompt = self._construct_prompt()
        model_name = self.model_var.get()
        temperature = float(self.temp_var.get())
        
        # Run API request in separate thread to keep UI responsive
        threading.Thread(target=self._call_groq_api, args=(sys_prompt, user_prompt, model_name, temperature), daemon=True).start()

    def _call_groq_api(self, sys_prompt, user_prompt, model_name, temperature):
        start_time = time.time()
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            req = urllib.request.Request(GROQ_API_URL, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                
                content = res_json['choices'][0]['message']['content'].strip()
                tokens_used = res_json.get('usage', {}).get('total_tokens', 'N/A')
                elapsed = time.time() - start_time
                
                self.after(0, self._handle_success, content, tokens_used, elapsed)
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8') if e.fp else str(e)
            self.after(0, self._handle_error, f"HTTP Error {e.code}: {err_msg}")
        except Exception as e:
            self.after(0, self._handle_error, f"Connection/Execution Error: {str(e)}")

    def _handle_success(self, raw_response, tokens, elapsed):
        self.is_processing = False
        self.status_pill.config(text="● READY", fg=self.colors["accent_emerald"])
        self.btn_extract.config(state="normal", text="⚡ EXTRACT DATA TO JSON NOW", bg=self.colors["primary"])
        
        # Clean markdown wrappers if model enclosed response in ```json ... ```
        cleaned = raw_response
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        # Parse and Pretty Print JSON
        try:
            parsed = json.loads(cleaned)
            formatted = json.dumps(parsed, indent=2)
            
            self.lbl_json_status.config(text="STATUS: ✅ Valid Structured JSON Output", fg=self.colors["accent_emerald"])
            self.lbl_metrics.config(text=f"⏱️ Latency: {elapsed:.2f}s  |  🪙 Tokens: {tokens}")
            
            self._render_colored_json(formatted)
        except json.JSONDecodeError as je:
            self.lbl_json_status.config(text="STATUS: ⚠️ Raw Output (JSON Parse Warning)", fg=self.colors["accent_amber"])
            self.lbl_metrics.config(text=f"⏱️ Latency: {elapsed:.2f}s  |  🪙 Tokens: {tokens}")
            self.txt_output.insert(tk.END, raw_response, "error")

    def _handle_error(self, error_message):
        self.is_processing = False
        self.status_pill.config(text="● API ERROR", fg="#ef4444")
        self.btn_extract.config(state="normal", text="⚡ EXTRACT DATA TO JSON NOW", bg=self.colors["primary"])
        self.lbl_json_status.config(text="STATUS: ❌ API Request Failed", fg="#ef4444")
        
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"ERROR DETAILS:\n{error_message}\n\nPlease check your internet connection or API Key.", "error")

    def _render_colored_json(self, json_str):
        self.txt_output.delete("1.0", tk.END)
        
        # Simple syntax highlighter for key-values
        lines = json_str.split("\n")
        for line in lines:
            # Check for key line: "key": value
            match_key = re.match(r'^(\s*)"([^"]+)":\s*(.*)$', line)
            if match_key:
                indent, key, val = match_key.groups()
                self.txt_output.insert(tk.END, indent)
                self.txt_output.insert(tk.END, f'"{key}"', "key")
                self.txt_output.insert(tk.END, ": ")
                
                # Highlight value
                if val.startswith('"'):
                    self.txt_output.insert(tk.END, val + "\n", "string")
                elif val in ["true", "false", "null"]:
                    self.txt_output.insert(tk.END, val + "\n", "boolean")
                elif re.match(r'^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?,?$', val):
                    self.txt_output.insert(tk.END, val + "\n", "number")
                else:
                    self.txt_output.insert(tk.END, val + "\n")
            else:
                self.txt_output.insert(tk.END, line + "\n")

    def _copy_output(self):
        content = self.txt_output.get("1.0", tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("Copied", "JSON output copied to clipboard!")

    def _save_output(self):
        content = self.txt_output.get("1.0", tk.END).strip()
        if not content:
            return
        
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"File saved successfully to:\n{filepath}")

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
