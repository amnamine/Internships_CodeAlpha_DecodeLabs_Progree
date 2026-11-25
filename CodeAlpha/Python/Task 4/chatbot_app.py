import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
from rule_engine import ChatbotRuleEngine

# Theme Color Palette (Neon Slate & Cyan-Purple)
BG_COLOR = "#0c0d12"          # Dark futuristic background
SIDEBAR_BG = "#13151f"        # Dark slate sidebar
BUBBLE_USER = "#202436"       # Deep blue-gray bubble for user
BUBBLE_BOT = "#171a26"        # Deep slate-black bubble for bot
TEXT_COLOR = "#e2e8f0"        # Off-white text
ACCENT_PURPLE = "#8a2be2"     # Purple accents
ACCENT_CYAN = "#00f0ff"       # Cyan highlight
BORDER_COLOR = "#2a2d3d"      # Subtle borders

class ChatbotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antigravity - Advanced Pseudo-LLM Chatbot")
        self.geometry("1000x700")
        self.configure(bg=BG_COLOR)
        
        # Initialize engine
        self.engine = ChatbotRuleEngine()
        self.fullscreen_state = False

        # Apply basic styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.create_widgets()
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        
        # Start initial greeting
        self.display_bot_message("Hello! I am Antigravity, a rules-driven intelligence engine mimicking LLM logic. How can I assist you today?")

    def create_widgets(self):
        # Master Grid Layout
        self.grid_columnconfigure(0, weight=1)  # Sidebar
        self.grid_columnconfigure(1, weight=4)  # Main chat panel
        self.grid_rowconfigure(0, weight=1)

        # ----------------- SIDEBAR -----------------
        sidebar = tk.Frame(self, bg=SIDEBAR_BG, bd=0, highlightbackground=BORDER_COLOR, highlightthickness=1)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Logo / Brand
        logo_label = tk.Label(
            sidebar, text="ANTIGRAVITY", 
            font=("Segoe UI Semibold", 18, "bold"), 
            bg=SIDEBAR_BG, fg=ACCENT_CYAN
        )
        logo_label.pack(pady=(25, 5), padx=10)
        
        sub_label = tk.Label(
            sidebar, text="State-Based Rule Engine", 
            font=("Segoe UI", 9, "italic"), 
            bg=SIDEBAR_BG, fg=TEXT_COLOR
        )
        sub_label.pack(pady=(0, 20))

        # Status Light Indicator
        status_frame = tk.Frame(sidebar, bg=SIDEBAR_BG)
        status_frame.pack(pady=10)
        self.status_dot = tk.Label(status_frame, text="●", font=("Segoe UI", 12), bg=SIDEBAR_BG, fg="#00ff66")
        self.status_dot.pack(side=tk.LEFT, padx=5)
        status_text = tk.Label(status_frame, text="ENGINE ONLINE", font=("Segoe UI Semibold", 8), bg=SIDEBAR_BG, fg=TEXT_COLOR)
        status_text.pack(side=tk.LEFT)
        
        self.animate_status_light()

        # Preset/Quick Action Prompts
        presets_label = tk.Label(sidebar, text="Quick Commands", font=("Segoe UI Semibold", 10), bg=SIDEBAR_BG, fg=ACCENT_PURPLE)
        presets_label.pack(pady=(20, 10), anchor="w", padx=20)

        presets = [
            ("🐍 Python Snippet", "Python code example"),
            ("🎮 Text Adventure", "Play game"),
            ("🧠 Ask a Riddle", "Ask me a riddle"),
            ("🌌 Scientific Fact", "Tell me a fact"),
            ("⚡ Motivation", "Give me motivation"),
            ("🤣 Tell a Joke", "Tell me a joke")
        ]

        for label, cmd in presets:
            btn = tk.Button(
                sidebar, text=label, font=("Segoe UI", 10),
                bg="#1a1c29", fg=TEXT_COLOR, activebackground=ACCENT_PURPLE,
                activeforeground="#ffffff", bd=0, relief=tk.FLAT,
                cursor="hand2", anchor="w", padx=15, pady=8,
                command=lambda c=cmd: self.send_preset(c)
            )
            btn.pack(fill=tk.X, padx=20, pady=4)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#242738", fg=ACCENT_CYAN))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#1a1c29", fg=TEXT_COLOR))

        # Utility Buttons Bottom Section
        util_frame = tk.Frame(sidebar, bg=SIDEBAR_BG)
        util_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20, padx=20)

        clear_btn = tk.Button(
            util_frame, text="Clear Chat", font=("Segoe UI Semibold", 9),
            bg="#2a1b2e", fg="#ff4d4d", activebackground="#ff4d4d", activeforeground="#ffffff",
            bd=1, relief=tk.SOLID, highlightbackground="#ff4d4d", cursor="hand2", pady=6,
            command=self.clear_chat
        )
        clear_btn.pack(fill=tk.X, pady=5)

        fs_btn = tk.Button(
            util_frame, text="Fullscreen [F11]", font=("Segoe UI Semibold", 9),
            bg="#1d243a", fg=TEXT_COLOR, activebackground=ACCENT_CYAN, activeforeground="#000000",
            bd=1, relief=tk.SOLID, highlightbackground=BORDER_COLOR, cursor="hand2", pady=6,
            command=self.toggle_fullscreen
        )
        fs_btn.pack(fill=tk.X, pady=5)

        # ----------------- MAIN CHAT SCREEN -----------------
        main_panel = tk.Frame(self, bg=BG_COLOR)
        main_panel.grid(row=0, column=1, sticky="nsew")
        main_panel.grid_rowconfigure(0, weight=1)  # Message Area
        main_panel.grid_rowconfigure(1, weight=0)  # Typing indicator
        main_panel.grid_rowconfigure(2, weight=0)  # Input Frame
        main_panel.grid_columnconfigure(0, weight=1)  # Canvas column
        main_panel.grid_columnconfigure(1, weight=0)  # Scrollbar column

        # Custom Scrollable Canvas for Messages
        self.canvas = tk.Canvas(main_panel, bg=BG_COLOR, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_panel, orient="vertical", command=self.canvas.yview)
        self.chat_viewport = tk.Frame(self.canvas, bg=BG_COLOR)
        
        self.chat_viewport.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.chat_viewport, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 0))
        self.scrollbar.grid(row=0, column=1, sticky="ns", pady=(15, 0))
        
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Typing Indicator Box
        self.typing_frame = tk.Frame(main_panel, bg=BG_COLOR)
        self.typing_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=30, pady=(5, 5))
        self.typing_label = tk.Label(
            self.typing_frame, text="Antigravity is formulating rules...", 
            font=("Segoe UI Italic", 10), bg=BG_COLOR, fg="#6b7280"
        )
        self.typing_label.pack(side=tk.LEFT)
        self.typing_frame.grid_remove() # Hidden by default

        # Input Control Frame
        input_frame = tk.Frame(main_panel, bg=BG_COLOR, pady=15)
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20)
        input_frame.grid_columnconfigure(0, weight=1)

        # Text input field
        self.entry_box = tk.Entry(
            input_frame, font=("Segoe UI", 12), bg="#181a24", fg=TEXT_COLOR,
            insertbackground=ACCENT_CYAN, bd=0, highlightthickness=1,
            highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_PURPLE,
            relief=tk.FLAT
        )
        self.entry_box.grid(row=0, column=0, sticky="ew", ipady=12, padx=(10, 10))
        self.entry_box.bind("<Return>", self.process_user_message)
        self.entry_box.focus_set()

        # Send Button
        self.send_btn = tk.Button(
            input_frame, text="Send 🚀", font=("Segoe UI Semibold", 10, "bold"),
            bg=ACCENT_PURPLE, fg="#ffffff", activebackground=ACCENT_CYAN,
            activeforeground="#000000", bd=0, relief=tk.FLAT, cursor="hand2",
            padx=20, command=self.process_user_message
        )
        self.send_btn.grid(row=0, column=1, sticky="ns", padx=(0, 10))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def animate_status_light(self):
        """Creates a smooth pulsing neon glow effect for the online dot indicator."""
        current_color = self.status_dot.cget("fg")
        next_color = "#10b981" if current_color == "#059669" else "#059669"
        self.status_dot.configure(fg=next_color)
        self.after(800, self.animate_status_light)

    def send_preset(self, text):
        self.entry_box.delete(0, tk.END)
        self.entry_box.insert(0, text)
        self.process_user_message()

    def display_user_message(self, text):
        bubble_frame = tk.Frame(self.chat_viewport, bg=BG_COLOR)
        bubble_frame.pack(fill=tk.X, anchor="w", pady=10, padx=15)
        
        # Spacer on left
        bubble_frame.grid_columnconfigure(0, weight=1)
        
        # User Label content wrapper
        msg_lbl = tk.Label(
            bubble_frame, text=text, font=("Segoe UI", 11),
            bg=BUBBLE_USER, fg=TEXT_COLOR, justify=tk.RIGHT,
            anchor="e", wraplength=450, padx=14, pady=10,
            highlightbackground="#343a4e", highlightthickness=1
        )
        msg_lbl.pack(side=tk.RIGHT)
        
        self.scroll_to_bottom()

    def display_bot_message(self, text):
        bubble_frame = tk.Frame(self.chat_viewport, bg=BG_COLOR)
        bubble_frame.pack(fill=tk.X, anchor="e", pady=10, padx=15)
        
        # Bot Label content wrapper
        msg_lbl = tk.Label(
            bubble_frame, text=text, font=("Segoe UI", 11),
            bg=BUBBLE_BOT, fg=TEXT_COLOR, justify=tk.LEFT,
            anchor="w", wraplength=450, padx=14, pady=10,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        msg_lbl.pack(side=tk.LEFT)
        
        self.scroll_to_bottom()

    def process_user_message(self, event=None):
        msg = self.entry_box.get().strip()
        if not msg:
            return
        
        self.entry_box.delete(0, tk.END)
        self.display_user_message(msg)

        # Show typing indicator to simulate LLM latency
        self.typing_frame.grid()
        self.entry_box.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)

        # Run response delay on background timer event
        self.after(random.randint(400, 1000), lambda: self.finish_bot_response(msg))

    def finish_bot_response(self, user_msg):
        # Retrieve computed result from rule engine
        response = self.engine.get_response(user_msg)
        
        self.typing_frame.grid_remove()
        self.entry_box.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.entry_box.focus_set()

        self.display_bot_message(response)

    def scroll_to_bottom(self):
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def clear_chat(self):
        for widget in self.chat_viewport.winfo_children():
            widget.destroy()
        self.engine.reset_state()
        self.display_bot_message("Chat history cleared. State reset successfully! How can I help you?")

    def toggle_fullscreen(self, event=None):
        self.fullscreen_state = not self.fullscreen_state
        self.attributes("-fullscreen", self.fullscreen_state)
        return "break"

    def exit_fullscreen(self, event=None):
        self.fullscreen_state = False
        self.attributes("-fullscreen", False)
        return "break"


if __name__ == "__main__":
    app = ChatbotApp()
    app.mainloop()
