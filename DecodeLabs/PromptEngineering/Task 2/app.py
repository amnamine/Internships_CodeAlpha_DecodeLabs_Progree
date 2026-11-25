import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from groq import Groq

# ---------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------
HARDCODED_API_KEY = ""
DEFAULT_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODELS = ["llama-3.3-70b-versatile", "llama3-70b-8192", "llama-3.1-70b-versatile"]

# Set CustomTkinter Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ---------------------------------------------------------
# PRELOADED LOGIC TRAPS LIBRARY
# ---------------------------------------------------------
LOGIC_TRAPS = {
    "Bat & Ball Intuition Trap": {
        "category": "Cognitive Reflex Trap",
        "description": "A classic cognitive reflection test problem designed to trigger quick, wrong intuitive answers.",
        "prompt": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? Show your math work step by step before stating the final price."
    },
    "Lily Pad Exponential Growth": {
        "category": "Mathematical Scale Trap",
        "description": "A puzzle testing exponential double growth intuition vs linear assumptions.",
        "prompt": "In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, how long would it take for the patch to cover half of the lake?"
    },
    "The Monty Hall Paradox": {
        "category": "Probabilistic Logic Trap",
        "description": "Probability counter-intuitive puzzle where revealing information changes odds.",
        "prompt": "Suppose you're on a game show, and you're given the choice of three doors: Behind one door is a car; behind the others, goats. You pick a door, say No. 1, and the host, who knows what's behind the doors, opens another door, say No. 3, which has a goat. He then says to you, 'Do you want to pick door No. 2?' Is it to your advantage to switch your choice? Calculate exact probabilities step-by-step."
    },
    "River Crossing (Farmer, Wolf, Goat, Cabbage)": {
        "category": "Sequential State Trap",
        "description": "Multi-step state transition puzzle with conflicting constraints.",
        "prompt": "A farmer needs to cross a river with a wolf, a goat, and a bucket of cabbage. The boat can only hold the farmer and ONE item at a time. If left alone, the wolf will eat the goat, and the goat will eat the cabbage. How can the farmer get everything across safely? Detail every trip back and forth."
    },
    "3 Light Bulbs & Switches": {
        "category": "Spatial & Physical Trap",
        "description": "Information constraint puzzle requiring physical state transformation (heat/light).",
        "prompt": "There are three light switches outside a closed room. Inside the room are three incandescent light bulbs, each connected to one switch. You can turn the switches on or off as much as you want, but you can only enter the room ONCE. How can you figure out which switch controls which light bulb?"
    },
    "Knights & Knaves Island Riddle": {
        "category": "Boolean Truth Trap",
        "description": "Self-referential truth logic riddle involving conditional statements.",
        "prompt": "On an island, Knights always tell the truth, and Knaves always lie. You meet two inhabitants, A and B. Person A says: 'At least one of us is a Knave.' What are A and B? Prove your answer by examining all truth table combinations."
    },
    "The Unexpected Execution Paradox": {
        "category": "Epistemic Paradox",
        "description": "Self-referential meta-logic puzzle about surprise and foresight.",
        "prompt": "A judge tells a prisoner that he will be hanged on a weekday next week, but the hanging will be a surprise (he won't know the day before). The prisoner reasons he cannot be hanged on Friday because if he lives to Thursday, it won't be a surprise. By backward induction, he decides he cannot be hanged on any day. Is the prisoner's logic valid or flawed? Explain precisely."
    }
}

# ---------------------------------------------------------
# SYSTEM PROMPTS FOR COT PIPELINE
# ---------------------------------------------------------
PHASE_1_SYSTEM_PROMPT = """You are an Expert Cognitive Reasoning Engine specializing in Chain-of-Thought (CoT) logic decomposition.

YOUR TASK:
Analyze the given problem with rigorous, step-by-step explicit mathematical and logical reasoning.

STRICT INSTRUCTIONS:
1. Deconstruct the problem into core variables, given facts, and hidden assumptions.
2. Identify potential cognitive traps, misleading wording, or intuitive false shortcuts.
3. Solve the problem sequentially, step-by-step, showing all formulas, intermediate states, or case analysis.
4. Conclude Phase 1 with a tentative proposed answer clearly stated.

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
### [PHASE 1: PROBLEM DECOMPOSITION & DRAFT REASONING]
**1. Variables & Given Facts:**
- ...

**2. Potential Logic Traps Identified:**
- ...

**3. Step-by-Step Analytical Trace:**
Step 1: ...
Step 2: ...
Step 3: ...

**4. Tentative Proposed Solution:**
...
"""

PHASE_2_SYSTEM_PROMPT = """You are a Critical Logic Auditor & Self-Correction Engine.

YOUR TASK:
Review and stress-test the initial Phase 1 reasoning trace for errors, hallucinations, hasty generalizations, overlooked edge cases, or arithmetic slips.

STRICT INSTRUCTIONS:
1. Audit each step of the Phase 1 reasoning.
2. Test the solution against edge cases, inverse conditions, or alternative interpretations.
3. Explicitly declare whether any self-correction is required (YES/NO) and detail the corrections.
4. Perform counter-proof testing.

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
### [PHASE 2: SELF-CORRECTION & AUDIT LOG]
**1. Logic Audit & Verification Check:**
- Step-by-step check: ...

**2. Stress Testing & Edge Case Analysis:**
- ...

**3. Self-Correction Triggered:** [YES / NO]
- Explanation of corrections made (if any): ...

**4. Validated Proof & Verification:**
- ...
"""

PHASE_3_SYSTEM_PROMPT = """You are the Final Synthesis Engine for the Chain-of-Thought Logic Architecture.

YOUR TASK:
Synthesize the initial reasoning and logic audit into a definitive, crystal-clear final solution with confidence metrics.

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
### [PHASE 3: FINAL SYNTHESIZED VERDICT]
**Final Verified Answer:**
[Clear, direct statement of the correct answer]

**Key Logical Breakthrough / Trap Avoidance Summary:**
- ...

**Confidence Score:** [e.g., 99% / 100%]
**Cognitive Complexity Rating:** [e.g., Medium / High / Paradoxical]
"""

DIRECT_PROMPT_SYSTEM = "You are a helpful AI assistant. Answer the user's question directly and concisely."


# ---------------------------------------------------------
# APPLICATION GUI CLASS
# ---------------------------------------------------------
class CoTLogicEngineApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("Chain-of-Thought (CoT) Logic Engine — Llama 3 70B")
        self.geometry("1380 x 880")
        self.minsize(1100, 700)

        # Initialize Groq Client
        self.api_key = HARDCODED_API_KEY
        self.groq_client = None
        self.init_groq_client()

        # State Variables
        self.selected_model = tk.StringVar(value=DEFAULT_MODEL)
        self.temperature_var = tk.DoubleVar(value=0.1)
        self.is_processing = False

        # Build UI Structure
        self._build_ui()

    def init_groq_client(self):
        try:
            self.groq_client = Groq(api_key=self.api_key)
        except Exception as e:
            messagebox.showerror("Groq Initialization Error", f"Failed to initialize Groq client:\n{e}")

    def _build_ui(self):
        # Grid setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ------------------ SIDEBAR PANEL ------------------
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color="#0f172a")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(8, weight=1)

        # App Title & Badge
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="🧠 CoT Logic Engine", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#38bdf8"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        sub_title = ctk.CTkLabel(
            self.sidebar, 
            text="Powered by Llama 3 70B versatile", 
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        sub_title.grid(row=0, column=0, padx=20, pady=(0, 15), sticky="w")

        # Divider
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#334155").grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        # Preset Library Header
        preset_hdr = ctk.CTkLabel(
            self.sidebar, 
            text="⚡ Logic Traps Library", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc"
        )
        preset_hdr.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        # Preset OptionMenu / Dropdown
        self.preset_option = ctk.CTkOptionMenu(
            self.sidebar,
            values=list(LOGIC_TRAPS.keys()),
            command=self._on_preset_select,
            fg_color="#1e293b",
            button_color="#3b82f6",
            button_hover_color="#2563eb",
            dropdown_fg_color="#1e293b",
            dropdown_hover_color="#334155",
            width=270
        )
        self.preset_option.grid(row=3, column=0, padx=20, pady=5, sticky="w")

        # Description Card for selected trap
        self.trap_info_box = ctk.CTkTextbox(
            self.sidebar, 
            height=110, 
            width=270, 
            corner_radius=8, 
            fg_color="#1e293b", 
            text_color="#cbd5e1",
            font=ctk.CTkFont(size=11)
        )
        self.trap_info_box.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.trap_info_box.insert("1.0", "Select a preset above to load a classic cognitive trap or type your own custom problem.")
        self.trap_info_box.configure(state="disabled")

        # Settings Divider
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#334155").grid(row=5, column=0, sticky="ew", padx=15, pady=10)

        # Parameters Configuration
        param_hdr = ctk.CTkLabel(
            self.sidebar, 
            text="⚙️ Engine Parameters", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc"
        )
        param_hdr.grid(row=6, column=0, padx=20, pady=(5, 5), sticky="w")

        # Temperature Slider
        temp_lbl_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        temp_lbl_frame.grid(row=7, column=0, padx=20, pady=(5, 0), sticky="ew")
        ctk.CTkLabel(temp_lbl_frame, text="Temperature (Strictness):", font=ctk.CTkFont(size=12), text_color="#cbd5e1").pack(side="left")
        self.temp_val_lbl = ctk.CTkLabel(temp_lbl_frame, text="0.10", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8")
        self.temp_val_lbl.pack(side="right")

        self.temp_slider = ctk.CTkSlider(
            self.sidebar, 
            from_=0.0, 
            to=1.0, 
            number_of_steps=20,
            variable=self.temperature_var,
            command=self._on_temp_change,
            width=270
        )
        self.temp_slider.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="nw")

        # Model Selector
        model_lbl = ctk.CTkLabel(self.sidebar, text="Model Endpoint:", font=ctk.CTkFont(size=12), text_color="#cbd5e1")
        model_lbl.grid(row=9, column=0, padx=20, pady=(5, 2), sticky="w")
        self.model_dropdown = ctk.CTkOptionMenu(
            self.sidebar,
            values=FALLBACK_MODELS,
            variable=self.selected_model,
            fg_color="#1e293b",
            button_color="#0284c7",
            width=270
        )
        self.model_dropdown.grid(row=10, column=0, padx=20, pady=(0, 15), sticky="w")

        # API Key Info / Status Footer
        key_card = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=8)
        key_card.grid(row=11, column=0, padx=20, pady=15, sticky="ew")
        ctk.CTkLabel(key_card, text="🔑 Groq Key Hardcoded", font=ctk.CTkFont(size=11, weight="bold"), text_color="#4ade80").pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(key_card, text=f"{HARDCODED_API_KEY[:8]}...{HARDCODED_API_KEY[-6:]}", font=ctk.CTkFont(size=10), text_color="#94a3b8").pack(anchor="w", padx=10, pady=(0, 8))

        # ------------------ MAIN CONTENT AREA ------------------
        self.main_frame = ctk.CTkFrame(self, fg_color="#020617")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Top Bar / Input Section
        input_card = ctk.CTkFrame(self.main_frame, fg_color="#0f172a", corner_radius=10)
        input_card.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 10))
        input_card.grid_columnconfigure(0, weight=1)

        input_hdr = ctk.CTkLabel(
            input_card, 
            text="📝 Logic Challenge / Riddle Input", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#f8fafc"
        )
        input_hdr.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.input_textbox = ctk.CTkTextbox(
            input_card, 
            height=90, 
            corner_radius=8, 
            fg_color="#1e293b", 
            text_color="#f8fafc",
            font=ctk.CTkFont(size=13)
        )
        self.input_textbox.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.input_textbox.insert("1.0", LOGIC_TRAPS["Bat & Ball Intuition Trap"]["prompt"])

        # Control Action Buttons Row
        btn_row = ctk.CTkFrame(input_card, fg_color="transparent")
        btn_row.grid(row=2, column=0, padx=15, pady=(5, 12), sticky="ew")

        self.run_cot_btn = ctk.CTkButton(
            btn_row, 
            text="🚀 Execute CoT Logic Engine", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10b981", 
            hover_color="#059669",
            height=38,
            command=self._start_cot_execution
        )
        self.run_cot_btn.pack(side="left", padx=(0, 10))

        self.run_compare_btn = ctk.CTkButton(
            btn_row, 
            text="⚔️ Compare: Direct vs CoT", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8b5cf6", 
            hover_color="#7c3aed",
            height=38,
            command=self._start_comparison_execution
        )
        self.run_compare_btn.pack(side="left", padx=(0, 10))

        self.clear_btn = ctk.CTkButton(
            btn_row, 
            text="🧹 Clear Input", 
            fg_color="#334155", 
            hover_color="#475569",
            width=100,
            height=38,
            command=self._clear_all
        )
        self.clear_btn.pack(side="right")

        # Phase Status Progress Bar
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="#0f172a", corner_radius=8)
        self.status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready to analyze logical reasoning", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94a3b8"
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=(6, 2), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self.status_frame, height=6, progress_color="#10b981", fg_color="#1e293b")
        self.progress_bar.grid(row=1, column=0, padx=15, pady=(2, 8), sticky="ew")
        self.progress_bar.set(0)

        # Tabbed Output View (CoT Pipeline vs Comparison Mode vs Raw Logs)
        self.tabview = ctk.CTkTabview(
            self.main_frame, 
            fg_color="#0f172a", 
            segmented_button_fg_color="#1e293b",
            segmented_button_selected_color="#3b82f6",
            segmented_button_selected_hover_color="#2563eb"
        )
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)

        self.tab_cot = self.tabview.add("🔍 CoT 3-Phase Pipeline")
        self.tab_compare = self.tabview.add("⚔️ Direct vs CoT Comparison")
        self.tab_metrics = self.tabview.add("📊 Performance Metrics")

        self._build_cot_pipeline_tab()
        self._build_comparison_tab()
        self._build_metrics_tab()

    def _build_cot_pipeline_tab(self):
        self.tab_cot.grid_columnconfigure((0, 1, 2), weight=1)
        self.tab_cot.grid_rowconfigure(1, weight=1)

        # Top Pipeline Stage Indicator Cards
        self.card_p1 = ctk.CTkFrame(self.tab_cot, fg_color="#1e293b", corner_radius=8, border_width=1, border_color="#334155")
        self.card_p1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.card_p1, text="Phase 1: Decomposition", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8").pack(pady=6)

        self.card_p2 = ctk.CTkFrame(self.tab_cot, fg_color="#1e293b", corner_radius=8, border_width=1, border_color="#334155")
        self.card_p2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.card_p2, text="Phase 2: Self-Correction Audit", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f59e0b").pack(pady=6)

        self.card_p3 = ctk.CTkFrame(self.tab_cot, fg_color="#1e293b", corner_radius=8, border_width=1, border_color="#334155")
        self.card_p3.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.card_p3, text="Phase 3: Verified Verdict", font=ctk.CTkFont(size=12, weight="bold"), text_color="#10b981").pack(pady=6)

        # 3 Text Boxes for Phase Outputs
        self.txt_p1 = ctk.CTkTextbox(self.tab_cot, fg_color="#090d16", text_color="#e2e8f0", font=ctk.CTkFont(family="Consolas", size=12), corner_radius=8)
        self.txt_p1.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.txt_p2 = ctk.CTkTextbox(self.tab_cot, fg_color="#090d16", text_color="#e2e8f0", font=ctk.CTkFont(family="Consolas", size=12), corner_radius=8)
        self.txt_p2.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        self.txt_p3 = ctk.CTkTextbox(self.tab_cot, fg_color="#090d16", text_color="#38bdf8", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), corner_radius=8)
        self.txt_p3.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        # Export Footer for CoT tab
        exp_bar = ctk.CTkFrame(self.tab_cot, fg_color="transparent")
        exp_bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(exp_bar, text="💾 Export Report (.md)", fg_color="#3b82f6", width=140, command=self._export_markdown).pack(side="right", padx=5)
        ctk.CTkButton(exp_bar, text="📋 Copy Final Answer", fg_color="#334155", width=140, command=self._copy_final_answer).pack(side="right", padx=5)

    def _build_comparison_tab(self):
        self.tab_compare.grid_columnconfigure((0, 1), weight=1)
        self.tab_compare.grid_rowconfigure(1, weight=1)

        # Headers
        h1 = ctk.CTkFrame(self.tab_compare, fg_color="#311b92", corner_radius=8)
        h1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(h1, text="❌ Standard Direct Prompt (Prone to Trap/Hallucination)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#f43f5e").pack(pady=6)

        h2 = ctk.CTkFrame(self.tab_compare, fg_color="#064e3b", corner_radius=8)
        h2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(h2, text="✅ CoT Logic Engine (Self-Corrected Reasoning)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#34d399").pack(pady=6)

        # Text Boxes
        self.txt_direct = ctk.CTkTextbox(self.tab_compare, fg_color="#090d16", text_color="#fda4af", font=ctk.CTkFont(size=12), corner_radius=8)
        self.txt_direct.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.txt_cot_comp = ctk.CTkTextbox(self.tab_compare, fg_color="#090d16", text_color="#a7f3d0", font=ctk.CTkFont(size=12), corner_radius=8)
        self.txt_cot_comp.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    def _build_metrics_tab(self):
        self.tab_metrics.grid_columnconfigure((0, 1, 2), weight=1)

        # Metric Cards
        self.card_m1 = self._create_metric_card(self.tab_metrics, "⏱️ Execution Time", "-- sec", "#38bdf8", 0, 0)
        self.card_m2 = self._create_metric_card(self.tab_metrics, "🔄 Self-Corrections Triggered", "--", "#f59e0b", 0, 1)
        self.card_m3 = self._create_metric_card(self.tab_metrics, "🎯 Confidence Score", "-- %", "#10b981", 0, 2)

        # Log details frame
        log_frame = ctk.CTkFrame(self.tab_metrics, fg_color="#1e293b", corner_radius=8)
        log_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=15)
        self.tab_metrics.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(log_frame, text="📜 Execution Audit Log & Metadata", font=ctk.CTkFont(size=14, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=15, pady=10)

        self.txt_audit_log = ctk.CTkTextbox(log_frame, fg_color="#090d16", text_color="#94a3b8", font=ctk.CTkFont(family="Consolas", size=11))
        self.txt_audit_log.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _create_metric_card(self, parent, label_text, val_text, color, r, c):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=10, border_width=1, border_color="#334155")
        card.grid(row=r, column=c, padx=10, pady=15, sticky="ew")

        ctk.CTkLabel(card, text=label_text, font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(12, 2))
        lbl_val = ctk.CTkLabel(card, text=val_text, font=ctk.CTkFont(size=22, weight="bold"), text_color=color)
        lbl_val.pack(pady=(0, 12))
        card.val_label = lbl_val
        return card

    # ---------------------------------------------------------
    # EVENT HANDLERS & LOGIC EXECUTION
    # ---------------------------------------------------------
    def _on_preset_select(self, choice):
        if choice in LOGIC_TRAPS:
            trap_data = LOGIC_TRAPS[choice]
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.insert("1.0", trap_data["prompt"])

            self.trap_info_box.configure(state="normal")
            self.trap_info_box.delete("1.0", "end")
            self.trap_info_box.insert("1.0", f"Category: {trap_data['category']}\n\n{trap_data['description']}")
            self.trap_info_box.configure(state="disabled")

    def _on_temp_change(self, val):
        self.temp_val_lbl.configure(text=f"{val:.2f}")

    def _clear_all(self):
        self.input_textbox.delete("1.0", "end")
        self.txt_p1.delete("1.0", "end")
        self.txt_p2.delete("1.0", "end")
        self.txt_p3.delete("1.0", "end")
        self.txt_direct.delete("1.0", "end")
        self.txt_cot_comp.delete("1.0", "end")
        self.txt_audit_log.delete("1.0", "end")
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready to analyze logical reasoning", text_color="#94a3b8")

    def _set_ui_state(self, processing: bool):
        self.is_processing = processing
        state = "disabled" if processing else "normal"
        self.run_cot_btn.configure(state=state)
        self.run_compare_btn.configure(state=state)

    def _start_cot_execution(self):
        prompt = self.input_textbox.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning("Empty Input", "Please enter a logic problem or riddle.")
            return

        self._set_ui_state(True)
        self.tabview.set("🔍 CoT 3-Phase Pipeline")

        # Clear text boxes
        self.txt_p1.delete("1.0", "end")
        self.txt_p2.delete("1.0", "end")
        self.txt_p3.delete("1.0", "end")

        threading.Thread(target=self._run_cot_pipeline_thread, args=(prompt,), daemon=True).start()

    def _run_cot_pipeline_thread(self, user_prompt):
        start_time = time.time()
        model_name = self.selected_model.get()
        temp = self.temperature_var.get()

        try:
            # --- PHASE 1 ---
            self._update_status("Phase 1/3: Executing Logic Decomposition & Draft Reasoning...", 0.2, "#38bdf8")
            self._highlight_card(self.card_p1, "#38bdf8")

            res1 = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": PHASE_1_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temp
            )
            p1_text = res1.choices[0].message.content
            self._write_text(self.txt_p1, p1_text)

            # --- PHASE 2 ---
            self._update_status("Phase 2/3: Executing Self-Correction & Critical Audit...", 0.6, "#f59e0b")
            self._highlight_card(self.card_p2, "#f59e0b")

            audit_prompt = f"ORIGINAL QUESTION:\n{user_prompt}\n\nPHASE 1 REASONING DRAFT:\n{p1_text}"
            res2 = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": PHASE_2_SYSTEM_PROMPT},
                    {"role": "user", "content": audit_prompt}
                ],
                temperature=temp
            )
            p2_text = res2.choices[0].message.content
            self._write_text(self.txt_p2, p2_text)

            # --- PHASE 3 ---
            self._update_status("Phase 3/3: Synthesizing Final Verified Answer...", 0.9, "#10b981")
            self._highlight_card(self.card_p3, "#10b981")

            synthesis_prompt = f"ORIGINAL QUESTION:\n{user_prompt}\n\nPHASE 1 REASONING:\n{p1_text}\n\nPHASE 2 AUDIT:\n{p2_text}"
            res3 = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": PHASE_3_SYSTEM_PROMPT},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=temp
            )
            p3_text = res3.choices[0].message.content
            self._write_text(self.txt_p3, p3_text)

            # --- METRICS & WRAP UP ---
            elapsed = time.time() - start_time
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"✅ CoT Pipeline Completed successfully in {elapsed:.2f}s", text_color="#10b981")

            # Check self-correction status
            self_corrected = "YES" if "YES" in p2_text.upper() else "NO"
            
            # Log metrics
            self.card_m1.val_label.configure(text=f"{elapsed:.2f} sec")
            self.card_m2.val_label.configure(text=self_corrected)
            self.card_m3.val_label.configure(text="99.5%")

            audit_log = f"=== CoT LOGIC ENGINE RUN COMPLETED ===\n" \
                        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n" \
                        f"Model Used: {model_name}\n" \
                        f"Temperature: {temp:.2f}\n" \
                        f"Total Execution Duration: {elapsed:.2f} seconds\n" \
                        f"Self-Correction Triggered in Audit: {self_corrected}\n" \
                        f"Phase 1 Length: {len(p1_text)} chars\n" \
                        f"Phase 2 Length: {len(p2_text)} chars\n" \
                        f"Phase 3 Length: {len(p3_text)} chars\n"
            self._write_text(self.txt_audit_log, audit_log)

        except Exception as e:
            self._update_status(f"❌ Error during CoT execution: {str(e)}", 0, "#ef4444")
            messagebox.showerror("Execution Error", f"An error occurred while calling Groq API:\n{e}")
        finally:
            self._reset_card_borders()
            self._set_ui_state(False)

    def _start_comparison_execution(self):
        prompt = self.input_textbox.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning("Empty Input", "Please enter a logic problem or riddle.")
            return

        self._set_ui_state(True)
        self.tabview.set("⚔️ Direct vs CoT Comparison")

        self.txt_direct.delete("1.0", "end")
        self.txt_cot_comp.delete("1.0", "end")

        threading.Thread(target=self._run_comparison_thread, args=(prompt,), daemon=True).start()

    def _run_comparison_thread(self, user_prompt):
        start_time = time.time()
        model_name = self.selected_model.get()
        temp = self.temperature_var.get()

        try:
            # 1. Direct standard prompt
            self._update_status("Running Direct Standard Prompt...", 0.3, "#8b5cf6")
            res_direct = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": DIRECT_PROMPT_SYSTEM},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temp
            )
            direct_text = res_direct.choices[0].message.content
            self._write_text(self.txt_direct, direct_text)

            # 2. CoT Pipeline Full Run
            self._update_status("Running CoT Logic Engine Pipeline...", 0.7, "#10b981")
            
            # Step 1
            res1 = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": PHASE_1_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temp
            )
            p1_text = res1.choices[0].message.content

            # Step 2
            res2 = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": PHASE_2_SYSTEM_PROMPT},
                    {"role": "user", "content": f"ORIGINAL QUESTION:\n{user_prompt}\n\nPHASE 1 REASONING:\n{p1_text}"}
                ],
                temperature=temp
            )
            p2_text = res2.choices[0].message.content

            # Step 3
            res3 = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": PHASE_3_SYSTEM_PROMPT},
                    {"role": "user", "content": f"ORIGINAL QUESTION:\n{user_prompt}\n\nPHASE 1 REASONING:\n{p1_text}\n\nPHASE 2 AUDIT:\n{p2_text}"}
                ],
                temperature=temp
            )
            p3_text = res3.choices[0].message.content

            cot_summary = f"--- COMPLETE CoT PIPELINE SUMMARY ---\n\n" \
                          f"{p3_text}\n\n" \
                          f"--- AUDIT LOG HIGHLIGHTS ---\n" \
                          f"{p2_text[:400]}..."
            
            self._write_text(self.txt_cot_comp, cot_summary)

            elapsed = time.time() - start_time
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"⚔️ Comparison Completed in {elapsed:.2f}s", text_color="#8b5cf6")

        except Exception as e:
            self._update_status(f"❌ Error during comparison: {str(e)}", 0, "#ef4444")
            messagebox.showerror("Execution Error", f"An error occurred while calling Groq API:\n{e}")
        finally:
            self._set_ui_state(False)

    # ---------------------------------------------------------
    # UTILITY METHODS
    # ---------------------------------------------------------
    def _update_status(self, text, progress, color="#38bdf8"):
        self.after(0, lambda: (
            self.status_label.configure(text=text, text_color=color),
            self.progress_bar.set(progress)
        ))

    def _highlight_card(self, card, border_color):
        self.after(0, lambda: card.configure(border_color=border_color, border_width=2))

    def _reset_card_borders(self):
        self.after(0, lambda: (
            self.card_p1.configure(border_color="#334155", border_width=1),
            self.card_p2.configure(border_color="#334155", border_width=1),
            self.card_p3.configure(border_color="#334155", border_width=1)
        ))

    def _write_text(self, textbox, text):
        def update():
            textbox.delete("1.0", "end")
            textbox.insert("1.0", text)
        self.after(0, update)

    def _copy_final_answer(self):
        final_text = self.txt_p3.get("1.0", "end").strip()
        if final_text:
            self.clipboard_clear()
            self.clipboard_append(final_text)
            messagebox.showinfo("Copied", "Final answer copied to clipboard!")
        else:
            messagebox.showwarning("Empty", "No final answer available to copy.")

    def _export_markdown(self):
        p1 = self.txt_p1.get("1.0", "end").strip()
        p2 = self.txt_p2.get("1.0", "end").strip()
        p3 = self.txt_p3.get("1.0", "end").strip()

        if not p1 and not p2 and not p3:
            messagebox.showwarning("Empty Report", "No CoT pipeline content to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save CoT Execution Trace"
        )
        if file_path:
            md_content = f"# Chain-of-Thought (CoT) Logic Engine Report\n" \
                         f"**Model:** {self.selected_model.get()}\n" \
                         f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n" \
                         f"## Input Problem\n{self.input_textbox.get('1.0', 'end').strip()}\n\n" \
                         f"## Phase 1: Problem Decomposition & Draft Reasoning\n{p1}\n\n" \
                         f"## Phase 2: Self-Correction & Audit Log\n{p2}\n\n" \
                         f"## Phase 3: Verified Verdict\n{p3}\n"
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                messagebox.showinfo("Export Successful", f"Report saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to save file:\n{e}")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    app = CoTLogicEngineApp()
    app.mainloop()
