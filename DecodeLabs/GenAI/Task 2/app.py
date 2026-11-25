import tkinter as tk
import customtkinter as ctk
from groq import Groq
import threading
import time

# Set window theme and color palette
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Hardcoded API key
API_KEY = ""
MODEL_NAME = "llama-3.3-70b-versatile"

class CopywritingAgentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Automated Copywriting & Tone Transformer (Autonomous Agent)")
        self.geometry("1100x750")
        self.minimum_size = (950, 650)
        
        # Initialize Groq client
        try:
            self.groq_client = Groq(api_key=API_KEY)
        except Exception as e:
            self.groq_client = None
            
        # UI State Variables
        self.product_name_var = tk.StringVar(value="NeuroSpark Smart Coffee")
        self.platform_var = tk.StringVar(value="LinkedIn")
        self.tone_var = tk.StringVar(value="Persuasive")
        self.temp_var = tk.DoubleVar(value=0.7)
        self.top_p_var = tk.DoubleVar(value=0.9)
        self.refinement_var = tk.BooleanVar(value=True)
        
        # Default prompt template
        self.prompt_template_str = (
            "You are an expert AI copywriter and marketing strategist.\n"
            "Create a highly engaging copy for the following product:\n"
            "Product Name: {product_name}\n"
            "Product Details/Description: {description}\n"
            "Target Platform: {platform}\n"
            "Tone of Voice: {tone}\n\n"
            "Make sure to adhere to platform-specific conventions (e.g. hashtags and hooks for Instagram, professional context for LinkedIn, subject lines for Email).\n"
            "Provide the final copywriting output clearly marked under a '### FINAL COPY' header."
        )
        
        # Draw UI
        self.create_layout()
        self.update_prompt_preview()
        
        # Bind inputs to update prompt preview automatically
        self.product_name_var.trace_add("write", lambda *args: self.update_prompt_preview())
        self.platform_var.trace_add("write", lambda *args: self.update_prompt_preview())
        self.tone_var.trace_add("write", lambda *args: self.update_prompt_preview())
        
    def create_layout(self):
        # Configure Grid Layout
        self.grid_columnconfigure(0, weight=2, minsize=400) # Input Panel
        self.grid_columnconfigure(1, weight=3, minsize=550) # Output Panel
        self.grid_rowconfigure(0, weight=1)
        
        # --- LEFT PANEL: INPUT & CONFIGURATION ---
        left_panel = ctk.CTkFrame(self, corner_radius=15, fg_color="#1a1c23")
        left_panel.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(3, weight=1) # Let the description box grow
        
        # Title Header
        title_label = ctk.CTkLabel(
            left_panel, 
            text="Copywriting Agent Settings", 
            font=ctk.CTkFont(family="Outfit", size=22, weight="bold"),
            text_color="#00D2C4"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # 1. Product Name Entry
        ctk.CTkLabel(left_panel, text="Product Name", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=0, padx=20, pady=(10, 2), sticky="w")
        self.name_entry = ctk.CTkEntry(
            left_panel, 
            textvariable=self.product_name_var, 
            placeholder_text="Enter product name...", 
            height=38,
            fg_color="#262930",
            border_color="#3b3e45"
        )
        self.name_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # 2. Product Description Text Box
        ctk.CTkLabel(left_panel, text="Product Key Features / Description", font=ctk.CTkFont(size=13, weight="bold")).grid(row=3, column=0, padx=20, pady=(5, 2), sticky="w")
        self.desc_text = ctk.CTkTextbox(
            left_panel, 
            height=120, 
            fg_color="#262930", 
            border_color="#3b3e45",
            border_width=1
        )
        self.desc_text.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.desc_text.insert("1.0", "A premium coffee blend infused with organic Nootropics, Lion's Mane, and L-Theanine. Designed to give clean, jitter-free energy and laser focus for developers and creatives. 100% organic, vegan, and delicious dark roast.")
        self.desc_text.bind("<KeyRelease>", lambda event: self.update_prompt_preview())
        
        # 3. Platform & Tone Selectors (Grid Layout)
        selectors_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        selectors_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        selectors_frame.grid_columnconfigure(0, weight=1)
        selectors_frame.grid_columnconfigure(1, weight=1)
        
        # Platform Selection
        ctk.CTkLabel(selectors_frame, text="Target Platform", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, padx=5, pady=(0, 2), sticky="w")
        self.platform_menu = ctk.CTkOptionMenu(
            selectors_frame, 
            variable=self.platform_var,
            values=["LinkedIn", "Instagram", "Email Newsletter", "Twitter / X", "Facebook Ads", "Blog Outline"],
            fg_color="#262930",
            button_color="#333742",
            dropdown_fg_color="#1a1c23"
        )
        self.platform_menu.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")
        
        # Tone Selection
        ctk.CTkLabel(selectors_frame, text="Tone of Voice", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, padx=5, pady=(0, 2), sticky="w")
        self.tone_menu = ctk.CTkOptionMenu(
            selectors_frame, 
            variable=self.tone_var,
            values=["Persuasive", "Professional", "Witty & Fun", "Bold & Creative", "Educational / Informative", "Empathetic & Warm"],
            fg_color="#262930",
            button_color="#333742",
            dropdown_fg_color="#1a1c23"
        )
        self.tone_menu.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="ew")
        
        # 4. System Parameters (Temperature & Top_P)
        params_frame = ctk.CTkFrame(left_panel, corner_radius=10, fg_color="#262930", border_color="#3b3e45", border_width=1)
        params_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        params_frame.grid_columnconfigure(0, weight=1)
        
        # Temperature Slider
        self.temp_label = ctk.CTkLabel(params_frame, text="Temperature: 0.70 (Creativity Control)", font=ctk.CTkFont(size=12, weight="bold"))
        self.temp_label.grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        self.temp_slider = ctk.CTkSlider(
            params_frame, 
            from_=0.0, 
            to=2.0, 
            number_of_steps=20, 
            variable=self.temp_var,
            command=self.on_temp_slide
        )
        self.temp_slider.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        # Top_P Slider
        self.top_p_label = ctk.CTkLabel(params_frame, text="Top P: 0.90 (Nucleus Sampling)", font=ctk.CTkFont(size=12, weight="bold"))
        self.top_p_label.grid(row=2, column=0, padx=15, pady=(10, 2), sticky="w")
        self.top_p_slider = ctk.CTkSlider(
            params_frame, 
            from_=0.0, 
            to=1.0, 
            number_of_steps=20, 
            variable=self.top_p_var,
            command=self.on_top_p_slide
        )
        self.top_p_slider.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        # 5. Agentic Loop Control
        agent_config_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        agent_config_frame.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        
        self.refinement_switch = ctk.CTkSwitch(
            agent_config_frame, 
            text="Autonomous Agent Multi-Stage Refinement", 
            variable=self.refinement_var,
            progress_color="#00D2C4",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.refinement_switch.pack(anchor="w", pady=5)
        
        # 6. Generate Button
        self.generate_btn = ctk.CTkButton(
            left_panel, 
            text="GENERATE MARKETING COPY", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#00D2C4",
            hover_color="#00b5a9",
            text_color="#0d0e12",
            height=45,
            corner_radius=8,
            command=self.start_generation_thread
        )
        self.generate_btn.grid(row=8, column=0, padx=20, pady=(15, 20), sticky="ew")
        
        
        # --- RIGHT PANEL: OUTPUT, TABS & LOGGING ---
        right_panel = ctk.CTkFrame(self, corner_radius=15, fg_color="#111318")
        right_panel.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Header banner
        header_bar = ctk.CTkFrame(right_panel, fg_color="#1a1c23", corner_radius=10, height=50)
        header_bar.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        header_bar.pack_propagate(False)
        
        header_title = ctk.CTkLabel(
            header_bar, 
            text="Agent workspace Status: Idle", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#A0A5B5"
        )
        header_title.pack(side="left", padx=15)
        self.status_label = header_title
        
        # Dynamic Tabview
        self.tab_control = ctk.CTkTabview(
            right_panel, 
            fg_color="#1a1c23", 
            segmented_button_fg_color="#262930",
            segmented_button_selected_color="#00D2C4",
            segmented_button_selected_hover_color="#00b5a9",
            segmented_button_unselected_color="#1a1c23",
            text_color="#ffffff"
        )
        self.tab_control.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="nsew")
        
        # Create tabs
        self.output_tab = self.tab_control.add("Copywriting Output")
        self.log_tab = self.tab_control.add("Agent Thought Log")
        self.prompt_tab = self.tab_control.add("Prompt Compiler")
        self.score_tab = self.tab_control.add("Quality Scorecard")
        
        # Output Tab Layout
        self.output_tab.grid_columnconfigure(0, weight=1)
        self.output_tab.grid_rowconfigure(0, weight=1)
        self.output_tab.grid_rowconfigure(1, weight=0)
        
        self.output_textbox = ctk.CTkTextbox(
            self.output_tab, 
            fg_color="#111318", 
            font=ctk.CTkFont(family="Inter", size=13),
            border_color="#3b3e45",
            border_width=1
        )
        self.output_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.output_textbox.insert("1.0", "Generated copy will appear here after clicking 'GENERATE MARKETING COPY'...")
        
        output_actions = ctk.CTkFrame(self.output_tab, fg_color="transparent")
        output_actions.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.char_count_lbl = ctk.CTkLabel(output_actions, text="Words: 0 | Characters: 0", font=ctk.CTkFont(size=12))
        self.char_count_lbl.pack(side="left", padx=5)
        
        self.copy_btn = ctk.CTkButton(
            output_actions, 
            text="Copy to Clipboard", 
            width=140, 
            fg_color="#333742",
            hover_color="#454b5a",
            command=self.copy_to_clipboard
        )
        self.copy_btn.pack(side="right", padx=5)
        
        # Agent Thought Log Tab Layout
        self.log_tab.grid_columnconfigure(0, weight=1)
        self.log_tab.grid_rowconfigure(0, weight=1)
        self.log_textbox = ctk.CTkTextbox(
            self.log_tab, 
            fg_color="#111318", 
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color="#89DDFF",
            border_color="#3b3e45",
            border_width=1
        )
        self.log_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.log_textbox.insert("1.0", "[LOG] Agent is currently idle. Configure settings and start generation.")
        
        # Prompt Compiler Tab Layout
        self.prompt_tab.grid_columnconfigure(0, weight=1)
        self.prompt_tab.grid_rowconfigure(0, weight=1)
        self.prompt_textbox = ctk.CTkTextbox(
            self.prompt_tab, 
            fg_color="#111318", 
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color="#C3E88D",
            border_color="#3b3e45",
            border_width=1
        )
        self.prompt_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Quality Scorecard Tab Layout
        self.score_tab.grid_columnconfigure(0, weight=1)
        self.score_tab.grid_rowconfigure(0, weight=1)
        self.score_textbox = ctk.CTkTextbox(
            self.score_tab, 
            fg_color="#111318", 
            font=ctk.CTkFont(family="Inter", size=13),
            border_color="#3b3e45",
            border_width=1
        )
        self.score_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.score_textbox.insert("1.0", "Quality evaluation will appear here once the agent reviews the final copywriting.")
        
    def on_temp_slide(self, val):
        self.temp_label.configure(text=f"Temperature: {val:.2f} (Creativity Control)")
        
    def on_top_p_slide(self, val):
        self.top_p_label.configure(text=f"Top P: {val:.2f} (Nucleus Sampling)")
        
    def get_description(self):
        return self.desc_text.get("1.0", "end-1c").strip()
        
    def update_prompt_preview(self):
        product_name = self.product_name_var.get()
        platform = self.platform_var.get()
        tone = self.tone_var.get()
        description = self.get_description()
        
        compiled = self.prompt_template_str.format(
            product_name=product_name,
            platform=platform,
            tone=tone,
            description=description
        )
        
        self.prompt_textbox.configure(state="normal")
        self.prompt_textbox.delete("1.0", "end")
        self.prompt_textbox.insert("1.0", compiled)
        self.prompt_textbox.configure(state="disabled")
        
    def log(self, text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"\n{text}")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        
    def clear_log(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        
    def start_generation_thread(self):
        # Disable button to prevent multiple concurrent requests
        self.generate_btn.configure(state="disabled", text="GENERATING...")
        self.status_label.configure(text="Agent Status: Executing Task...", text_color="#E5C07B")
        
        # Start execution in a background thread
        thread = threading.Thread(target=self.run_agent_pipeline)
        thread.daemon = True
        thread.start()
        
    def run_agent_pipeline(self):
        self.clear_log()
        self.log("[START] Launching Autonomous Copywriting Agent...")
        
        # 1. Compile variables
        product_name = self.product_name_var.get()
        platform = self.platform_var.get()
        tone = self.tone_var.get()
        description = self.get_description()
        temperature = self.temp_var.get()
        top_p = self.top_p_var.get()
        
        # Validation
        if not product_name or not description:
            self.log("[ERROR] Product Name or Description is empty. Cannot compile prompt.")
            self.status_label.configure(text="Agent Status: Input Error", text_color="#F85149")
            self.generate_btn.configure(state="normal", text="GENERATE MARKETING COPY")
            return
            
        self.log(f"[INFO] Settings: Temperature={temperature:.2f}, Top_P={top_p:.2f}")
        
        # Update Prompt
        self.update_prompt_preview()
        compiled_prompt = self.prompt_textbox.get("1.0", "end-1c")
        
        self.log("[STEP 1] Compiling dynamic prompt template...")
        self.log(f"[INFO] Prompt length: {len(compiled_prompt)} characters.")
        
        # Switch to logs tab to show output to user
        self.tab_control.set("Agent Thought Log")
        
        # 2. First stage API call: Create initial draft
        self.log(f"[STEP 2] Calling Groq API using model '{MODEL_NAME}' for Initial Draft...")
        
        if not self.groq_client:
            self.log("[ERROR] Groq client not initialized. Check your internet connection or API Key.")
            self.status_label.configure(text="Agent Status: Failed", text_color="#F85149")
            self.generate_btn.configure(state="normal", text="GENERATE MARKETING COPY")
            return
            
        try:
            # First inference
            response = self.groq_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a professional copywriting assistant."},
                    {"role": "user", "content": compiled_prompt}
                ],
                temperature=temperature,
                top_p=top_p,
                max_tokens=1500
            )
            initial_draft = response.choices[0].message.content
            self.log("[SUCCESS] Received initial draft from LLM.")
            
            # If multi-stage refinement is disabled
            if not self.refinement_var.get():
                self.log("[INFO] Multi-stage refinement disabled. Polishing and rendering final output.")
                self.render_final_output(initial_draft)
                self.generate_scorecard(initial_draft, platform, tone)
                return
                
            # 3. Critique Stage (Agentic Step)
            self.log("[STEP 3] Entering Critique & Self-Correction stage...")
            self.log("[INFO] Analyzing draft against platform conventions and tone consistency...")
            
            critique_prompt = (
                f"You are a critical senior editor and copy auditor.\n"
                f"Analyze the following marketing copy draft for:\n"
                f"Product: {product_name}\n"
                f"Platform: {platform}\n"
                f"Requested Tone: {tone}\n\n"
                f"Draft:\n\"\"\"\n{initial_draft}\n\"\"\"\n\n"
                f"Identify if there are issues with word length, appropriate call to actions, overuse of generic buzzwords, or misalignment with the tone.\n"
                f"Output a precise list of improvements needed. Keep your analysis concise."
            )
            
            critique_response = self.groq_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a strict, helpful copy editor."},
                    {"role": "user", "content": critique_prompt}
                ],
                temperature=0.3, # low temperature for analytical task
                max_tokens=1000
            )
            critique_feedback = critique_response.choices[0].message.content
            self.log("[SUCCESS] Critic Agent Feedback:\n" + "-"*40 + f"\n{critique_feedback}\n" + "-"*40)
            
            # 4. Refinement Stage
            self.log("[STEP 4] Executing refinement based on Critique feedback...")
            
            refine_prompt = (
                f"You are an expert AI copywriter. Refine the initial marketing copy by applying all the editor's feedback.\n\n"
                f"Product: {product_name}\n"
                f"Platform: {platform}\n"
                f"Tone: {tone}\n\n"
                f"Initial Draft:\n\"\"\"\n{initial_draft}\n\"\"\"\n\n"
                f"Editor's Critique:\n\"\"\"\n{critique_feedback}\n\"\"\"\n\n"
                f"Output the highly optimized, final copy clearly marked under a '### FINAL COPY' header."
            )
            
            refine_response = self.groq_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a master copywriter executing final revisions."},
                    {"role": "user", "content": refine_prompt}
                ],
                temperature=temperature,
                top_p=top_p,
                max_tokens=1500
            )
            final_copy = refine_response.choices[0].message.content
            self.log("[SUCCESS] Refinement complete. Generating final output.")
            
            self.render_final_output(final_copy)
            self.generate_scorecard(final_copy, platform, tone)
            
        except Exception as ex:
            self.log(f"[EXCEPTION] Groq API call failed: {str(ex)}")
            self.status_label.configure(text="Agent Status: Error", text_color="#F85149")
            
        finally:
            self.generate_btn.configure(state="normal", text="GENERATE MARKETING COPY")
            
    def render_final_output(self, copy_text):
        # Extract copy if structured under ### FINAL COPY
        display_text = copy_text
        if "### FINAL COPY" in copy_text:
            parts = copy_text.split("### FINAL COPY")
            if len(parts) > 1 and len(parts[1].strip()) > 50:
                display_text = parts[1].strip()
                
        # Update output tab
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", display_text)
        
        # Calculate words and chars
        words = len(display_text.split())
        chars = len(display_text)
        self.char_count_lbl.configure(text=f"Words: {words} | Characters: {chars}")
        
        # Update status
        self.status_label.configure(text="Agent Status: Copy Generated successfully!", text_color="#00D2C4")
        self.tab_control.set("Copywriting Output")
        
    def generate_scorecard(self, final_copy, platform, tone):
        self.log("[STEP 5] Generating quality scorecard analysis...")
        
        score_prompt = (
            f"Review this final copy for platform: {platform} and tone: {tone}.\n"
            f"Copy:\n\"\"\"\n{final_copy}\n\"\"\"\n\n"
            f"Provide a structured analysis in this exact markdown format:\n"
            f"### COPYWRITING QUALITY SCORECARD\n"
            f"- **Tone Match**: [Rating out of 10] & explanation\n"
            f"- **Platform Compatibility**: [Rating out of 10] & explanation\n"
            f"- **Engagement Score**: [Rating out of 10] & explanation\n"
            f"- **Best Elements**: Bullet points of strengths\n"
            f"- **Formatting Tips**: Actionable feedback if any"
        )
        
        try:
            score_response = self.groq_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a senior copywriting evaluator."},
                    {"role": "user", "content": score_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            scorecard = score_response.choices[0].message.content
            
            self.score_textbox.configure(state="normal")
            self.score_textbox.delete("1.0", "end")
            self.score_textbox.insert("1.0", scorecard)
            self.score_textbox.configure(state="disabled")
            self.log("[SUCCESS] Scorecard generated successfully.")
        except Exception as e:
            self.log(f"[WARNING] Could not generate scorecard: {str(e)}")
            
    def copy_to_clipboard(self):
        text = self.output_textbox.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.copy_btn.configure(text="Copied!")
        self.after(2000, lambda: self.copy_btn.configure(text="Copy to Clipboard"))


if __name__ == "__main__":
    app = CopywritingAgentApp()
    app.mainloop()
