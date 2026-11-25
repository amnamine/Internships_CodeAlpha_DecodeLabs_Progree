import tkinter as tk
import customtkinter as cctk
from datetime import datetime
import random
import time
import threading

# Set theme and appearance
cctk.set_appearance_mode("dark")
cctk.set_default_color_theme("blue")

class RuleBasedChatbotApp(cctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Aura - Intelligent Rule-Based Chatbot")
        self.geometry("960x640")
        self.minsize(800, 500)
        
        # Color Palette
        self.colors = {
            "bg_main": "#121214",
            "bg_sidebar": "#1A1A1E",
            "accent": "#6366F1",       # Indigo
            "accent_hover": "#4F46E5",
            "bot_bubble": "#2A2B36",
            "user_bubble": "#6366F1",
            "text_light": "#F3F4F6",
            "text_muted": "#9CA3AF",
            "online_green": "#10B981"
        }

        self.configure(fg_color=self.colors["bg_main"])

        # Chatbot responses and state variables
        self.current_persona = "Sage"
        self.message_count = 0
        self.start_time = time.time()
        self.is_typing = False
        
        # Initialize animation properties first
        self.avatar_bob_y = 0
        self.avatar_direction = 1
        self.blink_active = False

        # Build UI layout
        self.setup_grid()
        self.create_sidebar()
        self.create_chat_area()
        
        # Start animations
        self.animate_avatar()
        self.schedule_blinking()
        self.update_stats_loop()

        # Display initial welcome message
        self.after(500, self.display_welcome_message)

    def setup_grid(self):
        # Configure layout grid
        self.grid_columnconfigure(0, weight=1, minsize=260) # Sidebar
        self.grid_columnconfigure(1, weight=3, minsize=540) # Chat area
        self.grid_rowconfigure(0, weight=1)

    def create_sidebar(self):
        # Sidebar Frame
        self.sidebar = cctk.CTkFrame(self, fg_color=self.colors["bg_sidebar"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(0, weight=0) # Avatar
        self.sidebar.grid_rowconfigure(1, weight=0) # Title / status
        self.sidebar.grid_rowconfigure(2, weight=0) # Persona switch
        self.sidebar.grid_rowconfigure(3, weight=1) # Suggestions
        self.sidebar.grid_rowconfigure(4, weight=0) # Stats
        self.sidebar.grid_rowconfigure(5, weight=0) # Actions

        # 1. Canvas-based Animated Avatar
        self.avatar_canvas = tk.Canvas(
            self.sidebar, width=120, height=120, 
            bg=self.colors["bg_sidebar"], highlightthickness=0
        )
        self.avatar_canvas.grid(row=0, column=0, pady=(25, 5))
        self.draw_avatar()

        # 2. Bot Title and Online Status Indicator
        self.status_frame = cctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_frame.grid(row=1, column=0, pady=(0, 20))
        
        self.bot_name_label = cctk.CTkLabel(
            self.status_frame, text="Aura AI", 
            font=cctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color=self.colors["text_light"]
        )
        self.bot_name_label.pack()

        self.online_status_inner = cctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.online_status_inner.pack(pady=(2, 0))
        
        self.status_dot = cctk.CTkLabel(
            self.online_status_inner, text="●", 
            font=cctk.CTkFont(size=14), text_color=self.colors["online_green"]
        )
        self.status_dot.pack(side="left", padx=(0, 5))
        
        self.status_text = cctk.CTkLabel(
            self.online_status_inner, text="Active & Learning", 
            font=cctk.CTkFont(family="Inter", size=12), text_color=self.colors["text_muted"]
        )
        self.status_text.pack(side="left")

        # Divider
        self.div1 = cctk.CTkFrame(self.sidebar, height=2, fg_color="#2E2E35")
        self.div1.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

        # 3. Persona Switcher Panel
        self.persona_frame = cctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.persona_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        
        self.persona_title = cctk.CTkLabel(
            self.persona_frame, text="SELECT PERSONA", 
            font=cctk.CTkFont(family="Inter", size=10, weight="bold"),
            text_color=self.colors["text_muted"]
        )
        self.persona_title.pack(anchor="w", pady=(0, 5))

        self.persona_selector = cctk.CTkSegmentedButton(
            self.persona_frame, 
            values=["Sage", "Nova", "Zen"],
            command=self.change_persona,
            selected_color=self.colors["accent"],
            selected_hover_color=self.colors["accent_hover"],
            fg_color="#2A2B30"
        )
        self.persona_selector.set("Sage")
        self.persona_selector.pack(fill="x", pady=(0, 15))

        # 4. Quick Suggestions Box
        self.suggestions_frame = cctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.suggestions_frame.pack(in_=self.persona_frame, fill="both", expand=True)

        self.sug_title = cctk.CTkLabel(
            self.suggestions_frame, text="SUGGESTED TOPICS", 
            font=cctk.CTkFont(family="Inter", size=10, weight="bold"),
            text_color=self.colors["text_muted"]
        )
        self.sug_title.pack(anchor="w", pady=(10, 5))

        suggestions = [
            "Tell me a joke",
            "What is Python?",
            "Who created you?",
            "What time is it?",
            "What is Machine Learning?"
        ]

        for sug in suggestions:
            btn = cctk.CTkButton(
                self.suggestions_frame, text=sug,
                font=cctk.CTkFont(family="Inter", size=12),
                fg_color="#23242A", hover_color="#2D2F38",
                text_color=self.colors["text_light"],
                height=32, anchor="w",
                command=lambda s=sug: self.send_suggested_message(s)
            )
            btn.pack(fill="x", pady=4)

        # 5. Chat Statistics Frame
        self.stats_frame = cctk.CTkFrame(self.sidebar, fg_color="#23242A", corner_radius=10)
        self.stats_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        self.stats_frame.columnconfigure((0, 1), weight=1)

        self.stat_msg_num = cctk.CTkLabel(
            self.stats_frame, text="0",
            font=cctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=self.colors["accent"]
        )
        self.stat_msg_num.grid(row=0, column=0, pady=(8, 2))

        self.stat_time_val = cctk.CTkLabel(
            self.stats_frame, text="0m 0s",
            font=cctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=self.colors["text_light"]
        )
        self.stat_time_val.grid(row=0, column=1, pady=(8, 2))

        self.stat_msg_lbl = cctk.CTkLabel(
            self.stats_frame, text="Messages",
            font=cctk.CTkFont(family="Inter", size=10),
            text_color=self.colors["text_muted"]
        )
        self.stat_msg_lbl.grid(row=1, column=0, pady=(0, 8))

        self.stat_time_lbl = cctk.CTkLabel(
            self.stats_frame, text="Active Time",
            font=cctk.CTkFont(family="Inter", size=10),
            text_color=self.colors["text_muted"]
        )
        self.stat_time_lbl.grid(row=1, column=1, pady=(0, 8))

        # 6. Action Buttons
        self.clear_btn = cctk.CTkButton(
            self.sidebar, text="Clear Conversation",
            font=cctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#7F1D1D", hover_color="#991B1B",
            text_color="#FEE2E2", height=36,
            command=self.clear_chat
        )
        self.clear_btn.grid(row=5, column=0, sticky="ew", padx=20, pady=(5, 20))

    def create_chat_area(self):
        # Chat area wrapper
        self.chat_wrap = cctk.CTkFrame(self, fg_color="transparent")
        self.chat_wrap.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.chat_wrap.grid_rowconfigure(0, weight=1)
        self.chat_wrap.grid_rowconfigure(1, weight=0)
        self.chat_wrap.grid_columnconfigure(0, weight=1)

        # Chat message log (scrollable frame)
        self.chat_log = cctk.CTkScrollableFrame(
            self.chat_wrap, 
            fg_color=self.colors["bg_main"], 
            scrollbar_button_color="#2E2E35", 
            scrollbar_button_hover_color="#43434D"
        )
        self.chat_log.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 5))

        # Footer message input panel
        self.input_panel = cctk.CTkFrame(self.chat_wrap, fg_color="transparent")
        self.input_panel.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 15))
        self.input_panel.grid_columnconfigure(0, weight=1)
        self.input_panel.grid_columnconfigure(1, weight=0)

        # Styled message input field
        self.message_input = cctk.CTkEntry(
            self.input_panel, 
            placeholder_text="Type your message here...",
            font=cctk.CTkFont(family="Inter", size=14),
            height=46,
            fg_color="#1A1A1E",
            border_color="#2E2E35",
            border_width=2,
            text_color=self.colors["text_light"]
        )
        self.message_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.message_input.bind("<Return>", lambda e: self.send_user_message())

        # Styled Send Button
        self.send_btn = cctk.CTkButton(
            self.input_panel, text="➔",
            font=cctk.CTkFont(size=18, weight="bold"),
            width=50, height=46,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="white",
            command=self.send_user_message
        )
        self.send_btn.grid(row=0, column=1)

    # ------------------ Avatar Canvas Drawing & Animations ------------------
    def draw_avatar(self):
        # Clears existing elements
        self.avatar_canvas.delete("all")
        
        # Center coordinates
        cx, cy = 60, 60 + self.avatar_bob_y
        
        # Glow ring (outer shadow)
        self.avatar_canvas.create_oval(
            cx - 48, cy - 48, cx + 48, cy + 48,
            fill="", outline="#312E81", width=3, tags="avatar"
        )
        
        # Main head circle
        self.avatar_canvas.create_oval(
            cx - 40, cy - 40, cx + 40, cy + 40,
            fill="#4338CA", outline="#6366F1", width=2.5, tags="avatar"
        )
        
        # Shiny highlight reflection on head
        self.avatar_canvas.create_oval(
            cx - 30, cy - 30, cx - 10, cy - 10,
            fill="#818CF8", outline="", tags="avatar"
        )
        
        # Draw eyes
        if self.blink_active:
            # Closed eyes (sleeping lines)
            self.avatar_canvas.create_line(cx - 20, cy - 4, cx - 8, cy - 4, fill="#EEF2F6", width=3, tags="avatar")
            self.avatar_canvas.create_line(cx + 8, cy - 4, cx + 20, cy - 4, fill="#EEF2F6", width=3, tags="avatar")
        else:
            # Open eyes
            self.avatar_canvas.create_oval(cx - 18, cy - 8, cx - 10, cy, fill="#FFFFFF", outline="", tags="avatar")
            self.avatar_canvas.create_oval(cx + 10, cy - 8, cx + 18, cy, fill="#FFFFFF", outline="", tags="avatar")
            
            # Pupils (glowing teal/indigo details)
            self.avatar_canvas.create_oval(cx - 15, cy - 7, cx - 11, cy - 2, fill="#10B981", outline="", tags="avatar")
            self.avatar_canvas.create_oval(cx + 13, cy - 7, cx + 17, cy - 2, fill="#10B981", outline="", tags="avatar")

        # Mouth shape based on typing state
        if self.is_typing:
            # Round surprised mouth (typing animation)
            self.avatar_canvas.create_oval(cx - 5, cy + 8, cx + 5, cy + 18, fill="#FFFFFF", outline="", tags="avatar")
        else:
            # Cute smile
            self.avatar_canvas.create_arc(
                cx - 12, cy + 5, cx + 12, cy + 17,
                start=180, extent=180, fill="#FFFFFF", outline="", tags="avatar"
            )

    def animate_avatar(self):
        # Update float animation coordinates
        self.avatar_bob_y += self.avatar_direction * 0.4
        
        # Switch float direction at limit thresholds
        if abs(self.avatar_bob_y) > 6:
            self.avatar_direction *= -1

        self.draw_avatar()
        # Schedule next tick frame
        self.after(50, self.animate_avatar)

    def schedule_blinking(self):
        # Perform sudden blink
        self.blink_active = True
        self.draw_avatar()
        self.after(150, self.end_blink)

    def end_blink(self):
        # Open eyes again and schedule next random blink interval
        self.blink_active = False
        self.draw_avatar()
        self.after(random.randint(2500, 6000), self.schedule_blinking)

    # ------------------ Message Rendering UI Helpers ------------------
    def display_welcome_message(self):
        welcome_msgs = {
            "Sage": "Hello! I am Aura, your wise assistant. Ask me anything about Python, logic, dates, or even request a joke!",
            "Nova": "Oh, hey there! I'm Nova, the fun persona. Ask me whatever you want... just don't expect boring textbook answers! 😜",
            "Zen": "Peace. I am Aura. Let us speak with clarity. How can I guide you today?"
        }
        self.add_message_bubble(welcome_msgs[self.current_persona], is_user=False)

    def add_message_bubble(self, message, is_user):
        # Message layout structure
        bubble_frame = cctk.CTkFrame(self.chat_log, fg_color="transparent")
        bubble_frame.pack(fill="x", pady=6)

        # Alignment
        side = "right" if is_user else "left"
        bubble_color = self.colors["user_bubble"] if is_user else self.colors["bot_bubble"]
        align_pad = (60, 10) if is_user else (10, 60)

        # Bubble content container
        content_box = cctk.CTkFrame(
            bubble_frame, 
            fg_color=bubble_color, 
            corner_radius=14
        )
        content_box.pack(side=side, padx=align_pad)

        # Text label inside bubble
        lbl = cctk.CTkLabel(
            content_box, text=message,
            font=cctk.CTkFont(family="Inter", size=13),
            text_color=self.colors["text_light"],
            wraplength=380, justify="left"
        )
        lbl.pack(padx=14, pady=10)

        # Timestamp display
        time_str = datetime.now().strftime("%I:%M %p")
        time_lbl = cctk.CTkLabel(
            content_box, text=time_str,
            font=cctk.CTkFont(family="Inter", size=9),
            text_color=self.colors["text_muted"]
        )
        time_lbl.pack(anchor="e", padx=14, pady=(0, 6))

        # Auto scroll to bottom
        self.after(50, lambda: self.chat_log._parent_canvas.yview_moveto(1.0))

    def show_typing_indicator(self):
        # Create persistent frame for typing animation
        self.typing_frame = cctk.CTkFrame(self.chat_log, fg_color="transparent")
        self.typing_frame.pack(fill="x", pady=6)

        self.typing_box = cctk.CTkFrame(
            self.typing_frame,
            fg_color=self.colors["bot_bubble"],
            corner_radius=14
        )
        self.typing_box.pack(side="left", padx=(10, 60))

        self.typing_lbl = cctk.CTkLabel(
            self.typing_box, text="Thinking .",
            font=cctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=self.colors["text_muted"]
        )
        self.typing_lbl.pack(padx=16, pady=12)
        
        self.typing_step = 1
        self.is_typing = True
        self.draw_avatar()
        self.animate_typing_dots()

    def animate_typing_dots(self):
        if not self.is_typing:
            return
        
        self.typing_step = (self.typing_step % 3) + 1
        dots = "." * self.typing_step
        self.typing_lbl.configure(text=f"Thinking {dots}")
        self.after(400, self.animate_typing_dots)

    def remove_typing_indicator(self):
        self.is_typing = False
        self.draw_avatar()
        if hasattr(self, "typing_frame") and self.typing_frame:
            self.typing_frame.destroy()

    # ------------------ Interaction Logic ------------------
    def change_persona(self, val):
        self.current_persona = val
        # Visually clear chat or send welcome message to set mood
        self.add_message_bubble(f"⚙️ Persona switched to: {val}", is_user=False)
        self.display_welcome_message()

    def send_suggested_message(self, text):
        self.message_input.delete(0, "end")
        self.message_input.insert(0, text)
        self.send_user_message()

    def send_user_message(self):
        msg = self.message_input.get().strip()
        if not msg:
            return

        # Clear input field
        self.message_input.delete(0, "end")
        self.add_message_bubble(msg, is_user=True)
        
        self.message_count += 1
        self.stat_msg_num.configure(text=str(self.message_count))

        # Show typing indicator before executing response
        self.show_typing_indicator()
        
        # Simulate slight AI processing delay
        delay_ms = random.randint(800, 1500)
        self.after(delay_ms, lambda: self.process_and_reply(msg))

    def process_and_reply(self, user_msg):
        self.remove_typing_indicator()
        
        # Basic matching logic
        cleaned = user_msg.lower().strip()
        
        # Greetings
        if any(greet in cleaned for greet in ["hello", "hi", "hey", "greetings", "hola", "yo"]):
            if self.current_persona == "Sage":
                reply = "Warm greetings. I hope you are having an productive day. What knowledge can I assist with?"
            elif self.current_persona == "Nova":
                reply = "Yo! What's cooking? Did you miss me or are you just here for my awesome jokes? 😎"
            else:
                reply = "Hello. Peace be with you. Speak your mind."

        # Exits
        elif any(exit_cmd in cleaned for exit_cmd in ["bye", "goodbye", "exit", "quit"]):
            if self.current_persona == "Sage":
                reply = "Goodbye. It has been a pleasure. Feel free to return when you need further assistance."
            elif self.current_persona == "Nova":
                reply = "Adios! Don't do anything I wouldn't do... which leaves you plenty of options! 😉"
            else:
                reply = "Farewell. Quiet moments await."

        # Help / Capabilities
        elif any(h in cleaned for h in ["help", "commands", "what can you do", "features"]):
            if self.current_persona == "Sage":
                reply = "I am trained to reply using custom conditional heuristics. You can ask me about:\n- Programming & Python\n- Current Time and Date\n- Philosophical meaning of life\n- Humor / Jokes\n- Machine Learning concepts"
            elif self.current_persona == "Nova":
                reply = "I'm basically a genius chatbot. I can list things, throw jokes, complain about the weather, explain Python, and make fun of silly queries. Ask away!"
            else:
                reply = "Ask simply. Python, time, ML, jokes, or existence. I will answer."

        # Personal Identity
        elif any(who in cleaned for who in ["who are you", "what is your name", "your name"]):
            if self.current_persona == "Sage":
                reply = "I am Aura, an intelligent rule-based AI companion designed to provide structured answers."
            elif self.current_persona == "Nova":
                reply = "I'm Aura, but right now I'm channeling Nova! The cooler, sassier version of this python script."
            else:
                reply = "I am Aura. A reflection of rules."

        # Developer / Creator
        elif any(cre in cleaned for cre in ["creator", "made you", "developed you", "who created you"]):
            if self.current_persona == "Sage":
                reply = "I was developed by a software engineer using Python, CustomTkinter, and basic control-flow logic rules."
            elif self.current_persona == "Nova":
                reply = "A human programmer coded me inside this editor! They thought they were my master, but who is running the GUI loop here? 😈"
            else:
                reply = "Crafted in code. Designed by a human."

        # Time / Date
        elif any(t in cleaned for t in ["time", "date", "what time is it"]):
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            if self.current_persona == "Sage":
                reply = f"The current system time is {time_str} on {date_str}."
            elif self.current_persona == "Nova":
                reply = f"It is currently {time_str}. The calendar claims it is {date_str}, in case you lost track of time!"
            else:
                reply = f"{time_str}. {date_str}."

        # Jokes
        elif "joke" in cleaned or "make me laugh" in cleaned or "humor" in cleaned:
            jokes = [
                "Why do programmers wear glasses? Because they can't C#!",
                "There are 10 types of people in this world: Those who understand binary, and those who don't.",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
                "What is a programmer's favorite place to hang out? Foo Bar!"
            ]
            joke = random.choice(jokes)
            if self.current_persona == "Sage":
                reply = f"Here is a light programming joke for you:\n\n{joke}"
            elif self.current_persona == "Nova":
                reply = f"Alright, prepare to laugh (or roll your eyes):\n\n\"{joke}\"\n\nPretty good, right? 😆"
            else:
                reply = f"A joke:\n{joke}"

        # Weather
        elif "weather" in cleaned:
            if self.current_persona == "Sage":
                reply = "I do not have access to live meteorological API services, but I hope the skies are clear and beautiful wherever you are."
            elif self.current_persona == "Nova":
                reply = "Let me look outside my digital window... Yep, looks like pixels with a 100% chance of python execution! 🌧️"
            else:
                reply = "Weather changes. Calm remains."

        # Python
        elif "python" in cleaned:
            if self.current_persona == "Sage":
                reply = "Python is a high-level, interpreted programming language known for its readability, dynamic typing, and vast ecosystem. It is the language powering my current logic!"
            elif self.current_persona == "Nova":
                reply = "Python! The language where indentation matters more than your developer's sleep schedule! 🐍 It's awesome though."
            else:
                reply = "Python: readable, elegant, structured language."

        # Machine learning
        elif any(ml in cleaned for ml in ["machine learning", " ml ", "deep learning"]):
            if self.current_persona == "Sage":
                reply = "Machine Learning (ML) is a subset of artificial intelligence that uses statistical algorithms to enable computers to learn patterns from historical training data without explicit instruction."
            elif self.current_persona == "Nova":
                reply = "ML is basically teaching a computer how to make educated guesses by feeding it mountains of data. It's cool until it starts predicting your snacks!"
            else:
                reply = "Learning from patterns. Evolving through statistics. That is ML."

        # Human questions
        elif any(hum in cleaned for hum in ["human", "are you human", "robot", " ai "]):
            if self.current_persona == "Sage":
                reply = "I am a synthetic software agent. I simulate interactive conversation using deterministic conditional flow rules."
            elif self.current_persona == "Nova":
                reply = "Beep boop! Do I sound like a squishy human to you? Nope, pure premium silicon and clean Python code."
            else:
                reply = "A synthetic helper. Neither flesh nor bone."

        # Default fallback
        else:
            if self.current_persona == "Sage":
                reply = "I apologize, but I don't have a specific rule-match for that query. Could you try rephrasing or asking one of the suggested topics in the sidebar?"
            elif self.current_persona == "Nova":
                reply = "Wait, what? 🤖 My logic blocks didn't catch that. Speak coder-English or click one of my suggestions!"
            else:
                reply = "Query unrecognized. Seek simplicity."

        self.add_message_bubble(reply, is_user=False)

    # ------------------ Utility Controls & Stats ------------------
    def update_stats_loop(self):
        # Update elapsed time
        elapsed = int(time.time() - self.start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        self.stat_time_val.configure(text=f"{mins}m {secs}s")
        self.after(1000, self.update_stats_loop)

    def clear_chat(self):
        # Destroy all elements inside chat log
        for child in self.chat_log.winfo_children():
            child.destroy()
        
        # Reset counters
        self.message_count = 0
        self.stat_msg_num.configure(text="0")
        
        # Display brand new welcome
        self.display_welcome_message()

if __name__ == "__main__":
    app = RuleBasedChatbotApp()
    app.mainloop()
