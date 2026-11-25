import os
import sys
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from openai import OpenAI

# Pygments imports for code syntax highlighting
try:
    import pygments
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.token import Keyword, Name, Comment, String, Number, Operator, Punctuation
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

# Set theme and appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CodeEditor(ctk.CTkFrame):
    """Custom code editor component with line numbers and basic syntax highlighting."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Grid layout: line numbers column 0, text box column 1, scrollbar column 2
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Line numbers text widget
        self.line_nums = tk.Text(
            self, width=4, padx=5, takefocus=0, border=0,
            background="#1E1E2E", foreground="#585B70",
            state="disabled", wrap="none", font=("Consolas", 11)
        )
        self.line_nums.grid(row=0, column=0, sticky="nsew")
        
        # Main text widget
        self.textbox = tk.Text(
            self, wrap="none", border=0,
            background="#1E1E2E", foreground="#CDD6F4",
            insertbackground="#CDD6F4", font=("Consolas", 11),
            padx=10, pady=5, undo=True
        )
        self.textbox.grid(row=0, column=1, sticky="nsew")
        
        # Scrollbars
        self.v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.on_scrollbar)
        self.v_scroll.grid(row=0, column=2, sticky="ns")
        self.textbox.configure(yscrollcommand=self.v_scroll.set)
        
        self.h_scroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self.textbox.xview)
        self.h_scroll.grid(row=1, column=1, sticky="ew")
        self.textbox.configure(xscrollcommand=self.h_scroll.set)
        
        # Bind events for updating line numbers
        self.textbox.bind("<KeyRelease>", self.update_line_numbers)
        self.textbox.bind("<MouseWheel>", self.update_line_numbers)
        self.textbox.bind("<Button-1>", self.update_line_numbers)
        self.textbox.bind("<Configure>", self.update_line_numbers)
        
        # Configure tags for basic local syntax highlighting (optional fallback)
        self.setup_tags()
        self.textbox.bind("<KeyRelease>", self.trigger_highlighting, add="+")
        
        # Initial draw
        self.update_line_numbers()

    def setup_tags(self):
        # Syntax highlighting tags for the editor
        self.textbox.tag_configure("editor_keyword", foreground="#CBA6F7")
        self.textbox.tag_configure("editor_string", foreground="#A6E3A1")
        self.textbox.tag_configure("editor_comment", foreground="#7F849C", font=("Consolas", 11, "italic"))
        self.textbox.tag_configure("editor_number", foreground="#F9E2AF")

    def trigger_highlighting(self, event=None):
        # Quick basic highlight of keywords in editor
        if not PYGMENTS_AVAILABLE:
            return
        
        content = self.textbox.get("1.0", "end-1c")
        
        # Clear tags
        for tag in ["editor_keyword", "editor_string", "editor_comment", "editor_number"]:
            self.textbox.tag_remove(tag, "1.0", "end")
            
        try:
            lexer = guess_lexer(content)
        except Exception:
            try:
                lexer = get_lexer_by_name("python")
            except Exception:
                return
                
        for token_type, value in pygments.lex(content, lexer):
            if not value:
                continue
            
            # Map pygments tokens to tags
            tag = None
            if token_type in Keyword or token_type in Operator.Word:
                tag = "editor_keyword"
            elif token_type in String:
                tag = "editor_string"
            elif token_type in Comment:
                tag = "editor_comment"
            elif token_type in Number:
                tag = "editor_number"
                
            if tag:
                # Find occurrences and tag them
                start = "1.0"
                while True:
                    start = self.textbox.search(value, start, stopindex="end")
                    if not start:
                        break
                    end = f"{start} + {len(value)}c"
                    self.textbox.tag_add(tag, start, end)
                    start = end

    def on_scrollbar(self, *args):
        self.textbox.yview(*args)
        self.line_nums.yview(*args)
        self.update_line_numbers()

    def update_line_numbers(self, event=None):
        self.line_nums.configure(state="normal")
        self.line_nums.delete("1.0", "end")
        
        # Sync viewports
        self.line_nums.yview_moveto(self.textbox.yview()[0])
        
        # Count lines
        line_count = int(self.textbox.index("end-1c").split(".")[0])
        line_nums_str = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_nums.insert("1.0", line_nums_str)
        self.line_nums.configure(state="disabled")

    def get_text(self):
        return self.textbox.get("1.0", "end-1c")

    def set_text(self, text):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.update_line_numbers()
        self.trigger_highlighting()


class MarkdownViewer(ctk.CTkFrame):
    """A beautiful markdown renderer rendering text headers, lists, and formatted code blocks."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.textbox = tk.Text(
            self, wrap="word", border=0,
            background="#181825", foreground="#CDD6F4",
            insertbackground="#CDD6F4", font=("Segoe UI", 11),
            padx=15, pady=15
        )
        self.textbox.grid(row=0, column=0, sticky="nsew")
        
        self.v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.textbox.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.textbox.configure(yscrollcommand=self.v_scroll.set)
        
        self.setup_markdown_tags()
        
    def setup_markdown_tags(self):
        # Header fonts and sizes
        self.textbox.tag_configure("h1", font=("Segoe UI", 16, "bold"), foreground="#89B4FA", spacing1=10, spacing3=5)
        self.textbox.tag_configure("h2", font=("Segoe UI", 14, "bold"), foreground="#74C7EC", spacing1=8, spacing3=4)
        self.textbox.tag_configure("h3", font=("Segoe UI", 12, "bold"), foreground="#89DCEB", spacing1=6, spacing3=3)
        self.textbox.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        self.textbox.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        
        # Inline code styles
        self.textbox.tag_configure("inline_code", font=("Consolas", 10), background="#313244", foreground="#F38BA8")
        
        # List tag
        self.textbox.tag_configure("bullet", font=("Segoe UI", 11), lmargin1=15, lmargin2=25, spacing1=3)
        
        # Block code tag
        self.textbox.tag_configure("code_block", font=("Consolas", 10), background="#11111B", lmargin1=20, lmargin2=20, spacing1=5, spacing3=5)
        
        # Pygments code styling tags inside blocks
        if PYGMENTS_AVAILABLE:
            self.textbox.tag_configure("keyword", foreground="#CBA6F7", font=("Consolas", 10, "bold"))
            self.textbox.tag_configure("name", foreground="#89B4FA")
            self.textbox.tag_configure("comment", foreground="#7F849C", font=("Consolas", 10, "italic"))
            self.textbox.tag_configure("string", foreground="#A6E3A1")
            self.textbox.tag_configure("number", foreground="#F9E2AF")
            self.textbox.tag_configure("operator", foreground="#89DCEB")

    def render_markdown(self, markdown_text):
        """Parses the raw markdown string and renders it into the text widget with styling."""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        
        lines = markdown_text.split("\n")
        in_code_block = False
        code_block_content = []
        code_lang = "python"
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Code block starts or ends
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block, render it
                    self.render_code_block("\n".join(code_block_content), code_lang)
                    in_code_block = False
                    code_block_content = []
                else:
                    in_code_block = True
                    # Try to extract language
                    lang_part = line.strip()[3:].strip().lower()
                    code_lang = lang_part if lang_part else "python"
                i += 1
                continue
                
            if in_code_block:
                code_block_content.append(line)
                i += 1
                continue
                
            # Headers
            if line.startswith("# "):
                self.textbox.insert("end", line[2:] + "\n", "h1")
            elif line.startswith("## "):
                self.textbox.insert("end", line[3:] + "\n", "h2")
            elif line.startswith("### "):
                self.textbox.insert("end", line[4:] + "\n", "h3")
            # Bullet lists
            elif line.strip().startswith("- ") or line.strip().startswith("* "):
                bullet_char = " •  "
                # Strip marker and process inline formatting
                self.textbox.insert("end", bullet_char, "bullet")
                self.insert_inline_formatted_text(line.strip()[2:] + "\n", "bullet")
            else:
                # Regular paragraph with inline formatting
                self.insert_inline_formatted_text(line + "\n")
            i += 1
            
        # Handle case where block didn't close before the end of stream
        if in_code_block and code_block_content:
            self.render_code_block("\n".join(code_block_content), code_lang)
            
        self.textbox.configure(state="disabled")

    def insert_inline_formatted_text(self, text, base_tag=None):
        """Processes formatting like **bold**, *italic*, and `inline code`."""
        tags = [base_tag] if base_tag else []
        
        # Simple inline scanner
        j = 0
        n = len(text)
        current_chunk = ""
        
        while j < n:
            # Inline code block
            if text[j] == '`':
                if current_chunk:
                    self.textbox.insert("end", current_chunk, tuple(tags))
                    current_chunk = ""
                # Find ending backtick
                end_idx = text.find('`', j + 1)
                if end_idx != -1:
                    code_val = text[j+1:end_idx]
                    self.textbox.insert("end", code_val, tuple(tags + ["inline_code"]))
                    j = end_idx + 1
                    continue
            
            # Bold check
            if text[j:j+2] == '**':
                if current_chunk:
                    self.textbox.insert("end", current_chunk, tuple(tags))
                    current_chunk = ""
                end_idx = text.find('**', j + 2)
                if end_idx != -1:
                    bold_val = text[j+2:end_idx]
                    self.textbox.insert("end", bold_val, tuple(tags + ["bold"]))
                    j = end_idx + 2
                    continue
                    
            # Italic check
            if text[j] == '*' and (j == 0 or text[j-1] != '*'):
                if current_chunk:
                    self.textbox.insert("end", current_chunk, tuple(tags))
                    current_chunk = ""
                end_idx = text.find('*', j + 1)
                if end_idx != -1 and text[end_idx:end_idx+2] != '**':
                    italic_val = text[j+1:end_idx]
                    self.textbox.insert("end", italic_val, tuple(tags + ["italic"]))
                    j = end_idx + 1
                    continue
                    
            current_chunk += text[j]
            j += 1
            
        if current_chunk:
            self.textbox.insert("end", current_chunk, tuple(tags))

    def render_code_block(self, code_text, lang):
        """Renders code blocks using Pygments lexers and maps colors/tokens."""
        start_index = self.textbox.index("end-1c")
        
        # Write code lines prefixed with custom background margins
        self.textbox.insert("end", code_text + "\n", "code_block")
        end_index = self.textbox.index("end-1c")
        
        if not PYGMENTS_AVAILABLE:
            return
            
        try:
            lexer = get_lexer_by_name(lang)
        except Exception:
            try:
                lexer = guess_lexer(code_text)
            except Exception:
                lexer = None
                
        if not lexer:
            return
            
        # Parse and apply token styling inside the written block
        block_text = self.textbox.get(start_index, end_index)
        for token_type, value in pygments.lex(block_text, lexer):
            if not value or value.isspace():
                continue
                
            # Determine target tag
            tag = None
            if token_type in Keyword or token_type in Operator.Word:
                tag = "keyword"
            elif token_type in Name:
                tag = "name"
            elif token_type in Comment:
                tag = "comment"
            elif token_type in String:
                tag = "string"
            elif token_type in Number:
                tag = "number"
            elif token_type in Operator or token_type in Punctuation:
                tag = "operator"
                
            if tag:
                # Search and tag only within the block
                search_start = start_index
                while True:
                    pos = self.textbox.search(value, search_start, stopindex=end_index)
                    if not pos:
                        break
                    match_end = f"{pos} + {len(value)}c"
                    self.textbox.tag_add(tag, pos, match_end)
                    search_start = match_end


class CodeReviewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Intelligent Code Reviewer & Explainer Agent")
        self.geometry("1200x800")
        self.configure(fg_color="#11111B")
        
        # Threading communication queue
        self.update_queue = queue.Queue()
        
        self.setup_ui()
        self.check_queue_loop()
        
        # Hardcoded NVIDIA NIM API Key
        self.api_key = ""
        self.model_name = "nvidia/nemotron-3-super-120b-a12b"
        
        # Load sample python code initially
        self.editor.set_text(
            "def calculate_factorial(n):\n"
            "    # This is a sample code block with a bug\n"
            "    if n < 0:\n"
            "        return None\n"
            "    result = 1\n"
            "    for i in range(1, n):  # BUG: range should be 1 to n+1 to calculate factorial correctly\n"
            "        result = result * i\n"
            "    return result\n"
        )
        
    def setup_ui(self):
        # 1. Main Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)
        
        # 2. Sidebar Layout
        self.sidebar = ctk.CTkFrame(self, fg_color="#181825", corner_radius=10, width=280)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(15, 10), pady=15)
        self.sidebar.grid_propagate(False)
        
        # Sidebar elements
        title_lbl = ctk.CTkLabel(
            self.sidebar, text="🤖 Code Reviewer", 
            font=("Segoe UI", 18, "bold"), text_color="#89B4FA"
        )
        title_lbl.pack(pady=(20, 10), padx=15, anchor="w")
        
        subtitle_lbl = ctk.CTkLabel(
            self.sidebar, text="NVIDIA NIM AI Agent", 
            font=("Segoe UI", 11, "italic"), text_color="#A6ADC8"
        )
        subtitle_lbl.pack(pady=(0, 20), padx=15, anchor="w")
        
        # Ingestion buttons
        ingest_lbl = ctk.CTkLabel(self.sidebar, text="FILE INGESTION", font=("Segoe UI", 10, "bold"), text_color="#6C7086")
        ingest_lbl.pack(padx=15, anchor="w", pady=(10, 5))
        
        self.btn_load = ctk.CTkButton(
            self.sidebar, text="📂 Load Code File", command=self.load_file,
            fg_color="#313244", hover_color="#45475A", text_color="#CDD6F4"
        )
        self.btn_load.pack(fill="x", padx=15, pady=5)
        
        # Feature Pipelines
        pipeline_lbl = ctk.CTkLabel(self.sidebar, text="ANALYSIS PIPELINES", font=("Segoe UI", 10, "bold"), text_color="#6C7086")
        pipeline_lbl.pack(padx=15, anchor="w", pady=(20, 5))
        
        self.analysis_mode = ctk.StringVar(value="full")
        modes = [
            ("🔍 Full Review & Report", "full"),
            ("🪲 Identify Bugs", "bugs"),
            ("💡 Plain Explanation", "explain"),
            ("⚡ Code Optimization", "optimize")
        ]
        for name, value in modes:
            rb = ctk.CTkRadioButton(
                self.sidebar, text=name, variable=self.analysis_mode, value=value,
                font=("Segoe UI", 12), text_color="#CDD6F4",
                fg_color="#89B4FA", border_color="#585B70"
            )
            rb.pack(anchor="w", padx=20, pady=6)
            
        # Reasoning budget configuration
        budget_lbl = ctk.CTkLabel(self.sidebar, text="REASONING BUDGET (TOKENS)", font=("Segoe UI", 10, "bold"), text_color="#6C7086")
        budget_lbl.pack(padx=15, anchor="w", pady=(20, 5))
        
        self.budget_slider = ctk.CTkSlider(
            self.sidebar, from_=1024, to=16384, number_of_steps=15,
            button_color="#89B4FA", button_hover_color="#B4BEFE"
        )
        self.budget_slider.set(8192)
        self.budget_slider.pack(fill="x", padx=15, pady=5)
        
        self.budget_val_lbl = ctk.CTkLabel(self.sidebar, text="8192 tokens", font=("Segoe UI", 11), text_color="#A6ADC8")
        self.budget_val_lbl.pack(padx=15, anchor="e")
        self.budget_slider.configure(command=self.update_budget_lbl)
        
        # Execute button
        self.btn_analyze = ctk.CTkButton(
            self.sidebar, text="🚀 Run Autonomous Agent", command=self.run_agent,
            fg_color="#89B4FA", hover_color="#B4BEFE", text_color="#11111B",
            font=("Segoe UI", 13, "bold")
        )
        self.btn_analyze.pack(fill="x", padx=15, pady=25)
        
        # API status label
        self.status_lbl = ctk.CTkLabel(
            self.sidebar, text="● Status: Ready", text_color="#A6E3A1",
            font=("Segoe UI", 11)
        )
        self.status_lbl.pack(side="bottom", anchor="w", padx=15, pady=15)
        
        # 3. Main Display Panel
        self.main_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 15), pady=15)
        self.main_panel.grid_columnconfigure(0, weight=1)
        self.main_panel.grid_rowconfigure(0, weight=1)  # Input Code Editor
        self.main_panel.grid_rowconfigure(1, weight=1)  # Output tab view
        
        # Input Editor Frame
        self.input_frame = ctk.CTkFrame(self.main_panel, fg_color="#1E1E2E", corner_radius=10)
        self.input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(1, weight=1)
        
        editor_title_bar = ctk.CTkFrame(self.input_frame, fg_color="transparent", height=40)
        editor_title_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        lbl_editor = ctk.CTkLabel(editor_title_bar, text="💻 Code Block Input", font=("Segoe UI", 13, "bold"), text_color="#CDD6F4")
        lbl_editor.pack(side="left")
        
        self.editor = CodeEditor(self.input_frame)
        self.editor.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Output Tab View Frame
        self.tabview = ctk.CTkTabview(self.main_panel, fg_color="#1E1E2E", segmented_button_selected_color="#89B4FA", segmented_button_selected_hover_color="#B4BEFE", segmented_button_unselected_color="#313244", text_color="#CDD6F4")
        self.tabview.grid(row=1, column=0, sticky="nsew")
        
        self.tab_report = self.tabview.add("📊 Analysis Report")
        self.tab_thinking = self.tabview.add("🧠 Thinking Log")
        self.tab_chat = self.tabview.add("💬 Interactive Chat")
        
        # Tab 1: Analysis Report
        self.tab_report.grid_columnconfigure(0, weight=1)
        self.tab_report.grid_rowconfigure(0, weight=1)
        
        self.report_viewer = MarkdownViewer(self.tab_report)
        self.report_viewer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Report control buttons (Copy, Save)
        self.report_actions = ctk.CTkFrame(self.tab_report, fg_color="transparent")
        self.report_actions.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.btn_copy_code = ctk.CTkButton(
            self.report_actions, text="📋 Copy Code", width=120, command=self.copy_optimized_code,
            fg_color="#313244", hover_color="#45475A", text_color="#CDD6F4"
        )
        self.btn_copy_code.pack(side="left", padx=5)
        
        self.btn_save_report = ctk.CTkButton(
            self.report_actions, text="💾 Save Report", width=120, command=self.save_report,
            fg_color="#313244", hover_color="#45475A", text_color="#CDD6F4"
        )
        self.btn_save_report.pack(side="left", padx=5)
        
        # Tab 2: Thinking Log
        self.tab_thinking.grid_columnconfigure(0, weight=1)
        self.tab_thinking.grid_rowconfigure(0, weight=1)
        
        self.thinking_textbox = ctk.CTkTextbox(
            self.tab_thinking, wrap="word", border_color="#585B70",
            fg_color="#181825", text_color="#F5E0DC", font=("Segoe UI Semibold", 11)
        )
        self.thinking_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tab 3: Interactive Chat
        self.tab_chat.grid_columnconfigure(0, weight=1)
        self.tab_chat.grid_rowconfigure(0, weight=1)
        
        chat_frame = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)
        
        self.chat_history = ctk.CTkTextbox(
            chat_frame, wrap="word", fg_color="#181825", text_color="#CDD6F4",
            font=("Segoe UI", 11), state="disabled"
        )
        self.chat_history.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        self.chat_input = ctk.CTkEntry(
            chat_frame, placeholder_text="Ask the agent anything about the code block...",
            fg_color="#313244", text_color="#CDD6F4", border_color="#585B70"
        )
        self.chat_input.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.chat_input.bind("<Return>", lambda e: self.send_chat_msg())
        
        self.btn_send_chat = ctk.CTkButton(
            chat_frame, text="Send", width=80, command=self.send_chat_msg,
            fg_color="#89B4FA", hover_color="#B4BEFE", text_color="#11111B"
        )
        self.btn_send_chat.grid(row=1, column=1, sticky="e")

    def update_budget_lbl(self, val):
        self.budget_val_lbl.configure(text=f"{int(val)} tokens")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Source Files", "*.py;*.js;*.java;*.cpp;*.c;*.html;*.css"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.set_text(content)
                self.status_lbl.configure(text=f"● Loaded {os.path.basename(file_path)}", text_color="#89B4FA")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file:\n{str(e)}")

    def copy_optimized_code(self):
        text = self.report_viewer.textbox.get("1.0", "end")
        start = text.find("```")
        if start != -1:
            code_start = text.find("\n", start) + 1
            code_end = text.find("```", code_start)
            if code_end != -1:
                code_content = text[code_start:code_end].strip()
                self.clipboard_clear()
                self.clipboard_append(code_content)
                messagebox.showinfo("Success", "Optimized code block copied to clipboard!")
                return
        self.clipboard_clear()
        self.clipboard_append(text.strip())
        messagebox.showinfo("Success", "Full report text copied to clipboard!")

    def save_report(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt")]
        )
        if file_path:
            try:
                content = self.report_viewer.textbox.get("1.0", "end-1c")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Report saved successfully to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save report:\n{str(e)}")

    def run_agent(self):
        code_content = self.editor.get_text().strip()
        if not code_content:
            messagebox.showwarning("Warning", "Please input or load some code to analyze.")
            return
            
        mode = self.analysis_mode.get()
        budget = int(self.budget_slider.get())
        
        system_instruction = (
            "You are an expert software developer and code reviewer. Analyze the code provided by the user.\n"
            "Produce structured output using markdown formatting, and strictly separate your reasoning and final feedback.\n"
        )
        
        if mode == "full":
            prompt = (
                "Please perform a complete code review. Your output must contain three distinct markdown sections:\n"
                "1. ## Bug & Vulnerability Report\n"
                "   Identify logical bugs, syntax issues, performance bottlenecks, and security issues. Refer to line numbers.\n"
                "2. ## Code Explanation\n"
                "   Provide a step-by-step description of the logic in plain language suitable for developers of all skill levels.\n"
                "3. ## Optimized Code Block\n"
                "   Provide the optimized, clean, and bug-free version of the code inside a markdown block with syntax highlighting tags. Do not put comments or descriptions inside this code block that weren't in the original code, keep it clean.\n\n"
                f"Here is the raw code to analyze:\n\n```\n{code_content}\n```"
            )
        elif mode == "bugs":
            prompt = (
                "Please identify all bugs, errors, security threats, and performance pitfalls in this code block. "
                "Structure your output in a clear list under '## Bug & Vulnerability Report'. "
                "Also provide a clean bug-free version under '## Optimized Code Block'.\n\n"
                f"Here is the raw code:\n\n```\n{code_content}\n```"
            )
        elif mode == "explain":
            prompt = (
                "Please provide a plain-language explanation of this code block step-by-step under '## Code Explanation'. "
                "Break down complex variables, algorithm flow, and functions so that a beginner can fully understand it.\n\n"
                f"Here is the raw code:\n\n```\n{code_content}\n```"
            )
        elif mode == "optimize":
            prompt = (
                "Please optimize the time and space complexity of the provided code block, adhering to clean code guidelines. "
                "Output your optimizations under '## Optimization Summary' and the refactored, beautiful code block under '## Optimized Code Block'.\n\n"
                f"Here is the raw code:\n\n```\n{code_content}\n```"
            )

        self.thinking_textbox.configure(state="normal")
        self.thinking_textbox.delete("1.0", "end")
        self.thinking_textbox.configure(state="disabled")
        
        self.report_viewer.render_markdown("Starting AI Agent Analysis... Connecting to NVIDIA NIM API...\n")
        self.tabview.set("🧠 Thinking Log")
        
        self.status_lbl.configure(text="● Status: Thinking...", text_color="#F9E2AF")
        self.btn_analyze.configure(state="disabled")
        
        threading.Thread(target=self.api_worker, args=(system_instruction, prompt, budget), daemon=True).start()

    def send_chat_msg(self):
        msg = self.chat_input.get().strip()
        if not msg:
            return
            
        code_content = self.editor.get_text().strip()
        self.chat_input.delete(0, "end")
        
        self.chat_history._textbox.configure(state="normal")
        self.chat_history._textbox.insert("end", f"👤 You:\n{msg}\n\n", "user_msg")
        self.chat_history._textbox.configure(state="disabled")
        self.chat_history._textbox.see("end")
        
        prompt = (
            f"Here is the context code block:\n```\n{code_content}\n```\n\n"
            f"User's Question: {msg}"
        )
        
        self.status_lbl.configure(text="● Status: Chatting...", text_color="#F9E2AF")
        threading.Thread(target=self.api_worker, args=("You are a programming assistant assisting the user with their code.", prompt, 4096, True), daemon=True).start()

    def api_worker(self, system_instruction, prompt, budget, is_chat=False):
        try:
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.api_key
            )
            
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                top_p=0.95,
                max_tokens=16384,
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": True},
                    "reasoning_budget": budget
                },
                stream=True
            )
            
            for chunk in completion:
                if not chunk.choices:
                    continue
                
                reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
                content = chunk.choices[0].delta.content
                
                if reasoning:
                    self.update_queue.put(("reasoning", reasoning, is_chat))
                if content is not None:
                    self.update_queue.put(("content", content, is_chat))
                    
            self.update_queue.put(("done", "", is_chat))
            
        except Exception as e:
            self.update_queue.put(("error", str(e), is_chat))

    def check_queue_loop(self):
        for _ in range(50):
            try:
                msg_type, val, is_chat = self.update_queue.get_nowait()
            except queue.Empty:
                break
                
            if is_chat:
                self.handle_chat_message(msg_type, val)
            else:
                self.handle_review_message(msg_type, val)
                
            self.update_queue.task_done()
            
        self.after(50, self.check_queue_loop)

    def handle_review_message(self, msg_type, val):
        if msg_type == "reasoning":
            self.thinking_textbox.configure(state="normal")
            self.thinking_textbox.insert("end", val)
            self.thinking_textbox.configure(state="disabled")
            self.thinking_textbox.see("end")
            
        elif msg_type == "content":
            if self.tabview.get() == "🧠 Thinking Log":
                self.tabview.set("📊 Analysis Report")
                
            current_md = getattr(self, "_review_md", "") + val
            self._review_md = current_md
            self.report_viewer.render_markdown(current_md)
            self.report_viewer.textbox.see("end")
            
        elif msg_type == "done":
            self.status_lbl.configure(text="● Status: Analysis Completed", text_color="#A6E3A1")
            self.btn_analyze.configure(state="normal")
            self._review_md = ""
            
        elif msg_type == "error":
            self.status_lbl.configure(text="● Status: Error occurred", text_color="#F7768E")
            self.btn_analyze.configure(state="normal")
            self.report_viewer.render_markdown(f"### ❌ Error calling NVIDIA NIM API\n```\n{val}\n```")
            messagebox.showerror("API Error", f"An error occurred while calling the model:\n{val}")

    def handle_chat_message(self, msg_type, val):
        self.chat_history._textbox.configure(state="normal")
        
        if msg_type == "reasoning":
            if not getattr(self, "_chat_reasoning_started", False):
                self.chat_history._textbox.insert("end", "🧠 Thought Process:\n", "chat_thinking_header")
                self._chat_reasoning_started = True
            self.chat_history._textbox.insert("end", val, "chat_thinking")
            
        elif msg_type == "content":
            if getattr(self, "_chat_reasoning_started", False):
                self.chat_history._textbox.insert("end", "\n\n🤖 Assistant:\n", "assistant_header")
                self._chat_reasoning_started = False
            elif not getattr(self, "_chat_assistant_started", False):
                self.chat_history._textbox.insert("end", "🤖 Assistant:\n", "assistant_header")
                self._chat_assistant_started = True
            
            self.chat_history._textbox.insert("end", val, "chat_response")
            
        elif msg_type == "done":
            self.chat_history._textbox.insert("end", "\n\n" + "-"*40 + "\n\n")
            self._chat_reasoning_started = False
            self._chat_assistant_started = False
            self.status_lbl.configure(text="● Status: Ready", text_color="#A6E3A1")
            
        elif msg_type == "error":
            self.chat_history._textbox.insert("end", f"\n\n❌ Error:\n{val}\n\n")
            self._chat_reasoning_started = False
            self._chat_assistant_started = False
            self.status_lbl.configure(text="● Status: Ready", text_color="#A6E3A1")
            
        self.chat_history._textbox.configure(state="disabled")
        self.chat_history._textbox.see("end")


if __name__ == "__main__":
    app = CodeReviewerApp()
    
    app.chat_history._textbox.tag_configure("user_msg", foreground="#A6E3A1", font=("Segoe UI", 11, "bold"))
    app.chat_history._textbox.tag_configure("chat_thinking_header", foreground="#F9E2AF", font=("Segoe UI", 10, "italic"))
    app.chat_history._textbox.tag_configure("chat_thinking", foreground="#7F849C", font=("Segoe UI", 10, "italic"))
    app.chat_history._textbox.tag_configure("assistant_header", foreground="#89B4FA", font=("Segoe UI", 11, "bold"))
    app.chat_history._textbox.tag_configure("chat_response", foreground="#CDD6F4", font=("Segoe UI", 11))
    
    app.mainloop()
