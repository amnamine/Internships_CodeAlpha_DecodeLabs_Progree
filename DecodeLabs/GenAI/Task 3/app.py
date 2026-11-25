import os
import io
import threading
import queue
import random
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import requests

# Palette/Theme Colors (Deep Cyberpunk/Modern Dark Theme)
COLOR_BG = "#0b0b14"          # Deep dark space background
COLOR_CARD = "#141424"        # Dark slate card containers
COLOR_INPUT_BG = "#1d1d35"    # Slightly lighter dark for inputs
COLOR_TEXT = "#e1e1ec"        # Off-white primary text
COLOR_MUTED = "#8d8da0"       # Muted gray for subtitles/labels
COLOR_ACCENT = "#7c4dff"      # Electric violet for primary actions/accents
COLOR_ACCENT_HOVER = "#9670ff" # Hover violet
COLOR_SUCCESS = "#00e676"     # Bright neon green
COLOR_BORDER = "#2b2b45"      # Border color for cards

class ImageGenerationStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Pollinations.ai Image Studio")
        self.geometry("1100x750")
        self.configure(bg=COLOR_BG)
        
        # Make the window responsive
        self.columnconfigure(0, weight=3) # Main area (prompts + previews)
        self.columnconfigure(1, weight=1) # Sidebar (configurations)
        self.rowconfigure(0, weight=1)
        
        # Style configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Configure standard TTK styles
        self.style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT)
        self.style.configure("TFrame", background=COLOR_BG)
        
        # Card style
        self.style.configure("Card.TFrame", background=COLOR_CARD, relief="flat", borderwidth=0)
        
        # Label styles
        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"), background=COLOR_CARD, foreground=COLOR_TEXT)
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"), background=COLOR_CARD, foreground=COLOR_TEXT)
        self.style.configure("Regular.TLabel", font=("Helvetica", 10), background=COLOR_CARD, foreground=COLOR_TEXT)
        self.style.configure("Muted.TLabel", font=("Helvetica", 9), background=COLOR_CARD, foreground=COLOR_MUTED)
        
        # Combobox styling
        self.style.configure("TCombobox", fieldbackground=COLOR_INPUT_BG, background=COLOR_ACCENT, foreground=COLOR_TEXT)
        
        # State variables
        self.prompt_var = tk.StringVar()
        self.model_var = tk.StringVar(value="flux")
        self.aspect_ratio_var = tk.StringVar(value="1:1")
        self.seed_var = tk.StringVar(value="0") # "0" means random/none
        self.count_var = tk.IntVar(value=1)
        
        self.generated_images = [] # Keeps PIL Image objects
        self.current_image_idx = 0
        self.api_queue = queue.Queue()
        
        # Build components
        self.create_widgets()
        
        # Periodic check for async replies
        self.after(100, self.process_queue)

    def create_widgets(self):
        # ----------------------------------------------------
        # LEFT PANEL: Workspace (Prompt templates + Generator + Preview)
        # ----------------------------------------------------
        workspace_frame = ttk.Frame(self, padding=20)
        workspace_frame.grid(row=0, column=0, sticky="nsew")
        workspace_frame.columnconfigure(0, weight=1)
        workspace_frame.rowconfigure(2, weight=1) # Preview card takes main weight
        
        # App Title banner
        title_banner = ttk.Frame(workspace_frame)
        title_banner.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        title_label = ttk.Label(title_banner, text="🎨 Pollinations.ai Image Studio", font=("Helvetica", 20, "bold"), foreground=COLOR_TEXT)
        title_label.pack(side="left")
        subtitle_label = ttk.Label(title_banner, text="Free, keyless AI generation", font=("Helvetica", 10, "italic"), foreground=COLOR_MUTED)
        subtitle_label.pack(side="left", padx=15, pady=(8, 0))
        
        # Prompt Entry Card
        prompt_card = ttk.Frame(workspace_frame, style="Card.TFrame", padding=15)
        prompt_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        prompt_card.columnconfigure(0, weight=1)
        
        # Border simulation
        canvas_border = tk.Canvas(prompt_card, height=1, bg=COLOR_BORDER, highlightthickness=0)
        canvas_border.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        label_prompt = ttk.Label(prompt_card, text="Enter your creative prompt description:", style="Header.TLabel")
        label_prompt.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        # Quick tags / Presets
        presets_frame = ttk.Frame(prompt_card, style="Card.TFrame")
        presets_frame.grid(row=1, column=1, sticky="e")
        ttk.Label(presets_frame, text="Try template:", style="Muted.TLabel").pack(side="left", padx=5)
        presets = ["Cyberpunk City", "Fantasy Forest", "3D Cartoon", "Oil Painting"]
        for p in presets:
            btn = tk.Button(
                presets_frame, text=p, font=("Helvetica", 8), bg=COLOR_INPUT_BG, fg=COLOR_TEXT, 
                activebackground=COLOR_ACCENT, activeforeground=COLOR_TEXT, bd=0, padx=6, pady=2,
                cursor="hand2", command=lambda template=p: self.load_preset(template)
            )
            btn.pack(side="left", padx=3)
            
        self.text_prompt = tk.Text(
            prompt_card, height=3, font=("Helvetica", 11), bg=COLOR_INPUT_BG, fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT, bd=0, highlightthickness=1, highlightcolor=COLOR_ACCENT,
            highlightbackground=COLOR_BORDER, wrap="word", padx=10, pady=8
        )
        self.text_prompt.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        self.text_prompt.insert("1.0", "A futuristic cyberpunk cityscape with glowing neon billboards, flying vehicles, and rain puddles reflecting the lights.")
        
        # Generate Action Bar
        action_bar = ttk.Frame(prompt_card, style="Card.TFrame")
        action_bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        self.btn_generate = tk.Button(
            action_bar, text="🪄 Generate Artwork", font=("Helvetica", 12, "bold"), 
            bg=COLOR_ACCENT, fg=COLOR_TEXT, activebackground=COLOR_ACCENT_HOVER, 
            activeforeground=COLOR_TEXT, bd=0, padx=25, pady=8, cursor="hand2",
            command=self.start_generation
        )
        self.btn_generate.pack(side="right")
        
        self.progress_bar = ttk.Progressbar(action_bar, mode="indeterminate", length=200)
        
        # Preview Card
        self.preview_card = ttk.Frame(workspace_frame, style="Card.TFrame", padding=15)
        self.preview_card.grid(row=2, column=0, sticky="nsew")
        self.preview_card.columnconfigure(0, weight=1)
        self.preview_card.rowconfigure(1, weight=1)
        
        preview_header = ttk.Frame(self.preview_card, style="Card.TFrame")
        preview_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(preview_header, text="Generated Artwork Preview", style="Header.TLabel").pack(side="left")
        
        # Carousel controls (in case count > 1)
        self.carousel_frame = ttk.Frame(preview_header, style="Card.TFrame")
        self.btn_prev = tk.Button(self.carousel_frame, text="◀ Prev", bg=COLOR_INPUT_BG, fg=COLOR_TEXT, bd=0, padx=8, command=self.prev_image, cursor="hand2")
        self.btn_prev.pack(side="left", padx=2)
        self.lbl_carousel_status = ttk.Label(self.carousel_frame, text="0 / 0", style="Regular.TLabel")
        self.lbl_carousel_status.pack(side="left", padx=8)
        self.btn_next = tk.Button(self.carousel_frame, text="Next ▶", bg=COLOR_INPUT_BG, fg=COLOR_TEXT, bd=0, padx=8, command=self.next_image, cursor="hand2")
        self.btn_next.pack(side="left", padx=2)
        
        # Preview container/Canvas
        self.canvas_preview = tk.Canvas(self.preview_card, bg=COLOR_INPUT_BG, highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.canvas_preview.grid(row=1, column=0, sticky="nsew", pady=5)
        self.canvas_preview.bind("<Configure>", self.on_preview_resize)
        
        # Overlay instructions when empty
        self.canvas_preview.create_text(0, 0, text="Your generated artwork will appear here.\nSet parameters and click Generate!", 
                                         fill=COLOR_MUTED, font=("Helvetica", 12), justify="center", tags="placeholder")
        
        # Image save / Export utilities
        self.utils_frame = ttk.Frame(self.preview_card, style="Card.TFrame")
        self.utils_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.btn_save = tk.Button(
            self.utils_frame, text="💾 Save to File", font=("Helvetica", 10, "bold"), 
            bg=COLOR_INPUT_BG, fg=COLOR_TEXT, activebackground=COLOR_ACCENT, activeforeground=COLOR_TEXT,
            bd=0, padx=15, pady=6, cursor="hand2", command=self.save_current_image, state="disabled"
        )
        self.btn_save.pack(side="right", padx=5)
        
        self.btn_copy_prompt = tk.Button(
            self.utils_frame, text="📋 Copy Prompt", font=("Helvetica", 10), 
            bg=COLOR_INPUT_BG, fg=COLOR_TEXT, activebackground=COLOR_ACCENT, activeforeground=COLOR_TEXT,
            bd=0, padx=15, pady=6, cursor="hand2", command=self.copy_prompt
        )
        self.btn_copy_prompt.pack(side="right", padx=5)

        # ----------------------------------------------------
        # RIGHT PANEL: Configuration Sidebar
        # ----------------------------------------------------
        sidebar = ttk.Frame(self, padding=20, style="Card.TFrame")
        sidebar.grid(row=0, column=1, sticky="nsew")
        sidebar.columnconfigure(0, weight=1)
        
        # Outer border line separating columns
        canvas_sep = tk.Canvas(sidebar, width=1, bg=COLOR_BORDER, highlightthickness=0)
        canvas_sep.place(x=0, y=0, relheight=1)
        
        ttk.Label(sidebar, text="⚙️ Studio Parameters", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # --- MODEL SELECTOR ---
        ttk.Label(sidebar, text="Generation Model:", style="Header.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 2))
        self.combo_model = ttk.Combobox(
            sidebar, textvariable=self.model_var, state="readonly",
            values=["flux", "grok-imagine", "ideogram-v4-turbo", "nanobanana", "nanobanana-pro"]
        )
        self.combo_model.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        # --- ASPECT RATIO ---
        ttk.Label(sidebar, text="Aspect Ratio:", style="Header.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 2))
        self.combo_aspect = ttk.Combobox(
            sidebar, textvariable=self.aspect_ratio_var, state="readonly",
            values=["1:1", "16:9", "9:16", "4:3", "3:4", "21:9"]
        )
        self.combo_aspect.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        
        # --- SEED ---
        ttk.Label(sidebar, text="Seed (0 for random):", style="Header.TLabel").grid(row=5, column=0, sticky="w", pady=(10, 2))
        self.entry_seed = tk.Entry(
            sidebar, textvariable=self.seed_var, font=("Helvetica", 10),
            bg=COLOR_INPUT_BG, fg=COLOR_TEXT, bd=0, insertbackground=COLOR_TEXT, highlightthickness=1,
            highlightbackground=COLOR_BORDER, highlightcolor=COLOR_ACCENT
        )
        self.entry_seed.grid(row=6, column=0, sticky="ew", ipady=6, pady=(0, 15))
        
        # --- IMAGE COUNT ---
        ttk.Label(sidebar, text="Generation Count (Batch Size):", style="Header.TLabel").grid(row=7, column=0, sticky="w", pady=(10, 2))
        
        slider_frame = ttk.Frame(sidebar, style="Card.TFrame")
        slider_frame.grid(row=8, column=0, sticky="ew", pady=(0, 15))
        slider_frame.columnconfigure(0, weight=1)
        
        self.slider_count = tk.Scale(
            slider_frame, from_=1, to=4, orient="horizontal", variable=self.count_var,
            bg=COLOR_CARD, fg=COLOR_TEXT, highlightthickness=0, activebackground=COLOR_ACCENT,
            troughcolor=COLOR_INPUT_BG, resolution=1
        )
        self.slider_count.grid(row=0, column=0, sticky="ew")
        
        # --- STATS / LOG PANEL ---
        stats_border = tk.Canvas(sidebar, height=1, bg=COLOR_BORDER, highlightthickness=0)
        stats_border.grid(row=9, column=0, sticky="ew", pady=15)
        
        ttk.Label(sidebar, text="Studio Log Output:", style="Header.TLabel").grid(row=10, column=0, sticky="w", pady=(0, 5))
        self.log_text = tk.Text(
            sidebar, height=12, font=("Courier", 9), bg=COLOR_INPUT_BG, fg=COLOR_MUTED,
            bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER, wrap="word", state="disabled"
        )
        self.log_text.grid(row=11, column=0, sticky="ew")
        self.log_message("System ready. Pollinations.ai configured.")

    def log_message(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"> {msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def load_preset(self, preset_name):
        presets = {
            "Cyberpunk City": "A futuristic cyberpunk cityscape with glowing neon billboards, flying vehicles, and rain puddles reflecting the lights.",
            "Fantasy Forest": "A magical glowing forest at night, filled with bioluminescent plants, tiny fairies flying around, and a crystal clear stream.",
            "3D Cartoon": "A cute 3D cartoon style robot puppy sitting in a modern high-tech room, bright vivid colors, studio lighting, cinematic render.",
            "Oil Painting": "A classic oil painting of a majestic mountain valley during golden hour, with a small cabin by the river and orange autumn trees."
        }
        if preset_name in presets:
            self.text_prompt.delete("1.0", "end")
            self.text_prompt.insert("1.0", presets[preset_name])
            self.log_message(f"Loaded template: {preset_name}")

    def copy_prompt(self):
        prompt = self.text_prompt.get("1.0", "end-1c").strip()
        self.clipboard_clear()
        self.clipboard_append(prompt)
        self.log_message("Prompt copied to clipboard.")

    def start_generation(self):
        prompt = self.text_prompt.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showerror("Validation Error", "Please enter a prompt description first!")
            return
            
        model = self.model_var.get()
        aspect_ratio = self.aspect_ratio_var.get()
        count = self.count_var.get()
        
        # Parse seed
        try:
            seed_val = int(self.seed_var.get().strip())
        except ValueError:
            seed_val = 0
            self.seed_var.set("0")
            
        # Map aspect ratios to standard dimensions
        ratio_map = {
            "1:1": (1024, 1024),
            "16:9": (1344, 768),
            "9:16": (768, 1344),
            "4:3": (1152, 896),
            "3:4": (896, 1152),
            "21:9": (1216, 832)
        }
        width, height = ratio_map.get(aspect_ratio, (1024, 1024))
        
        # Disable buttons & show loading
        self.btn_generate.config(state="disabled", text="⚡ Generating...")
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.start(10)
        
        # Log state
        self.log_message(f"Starting async request...")
        self.log_message(f"Model: {model}")
        self.log_message(f"Aspect Ratio: {aspect_ratio} ({width}x{height})")
        self.log_message(f"Seed: {seed_val if seed_val > 0 else 'Random'}")
        self.log_message(f"Batch Count: {count}")
        
        # Clear previous images
        self.generated_images = []
        self.current_image_idx = 0
        self.lbl_carousel_status.config(text="0 / 0")
        self.carousel_frame.pack_forget()
        self.btn_save.config(state="disabled")
        
        # Start background task thread
        threading.Thread(
            target=self.run_api_generation,
            args=(model, prompt, width, height, seed_val, count),
            daemon=True
        ).start()

    def run_api_generation(self, model, prompt, width, height, seed, count):
        try:
            images_list = []
            
            # URL-encode the prompt safely
            encoded_prompt = urllib.parse.quote(prompt)
            
            for i in range(count):
                self.log_message(f"Requesting image {i+1} of {count}...")
                
                # If seed is 0, generate a random positive integer
                current_seed = seed if seed > 0 else random.randint(1, 100000000)
                
                url = f"https://image.pollinations.ai/p/{encoded_prompt}"
                params = {
                    "model": model,
                    "width": width,
                    "height": height,
                    "seed": current_seed,
                    "nologo": "true",
                    "private": "true"
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content))
                    images_list.append(img)
                else:
                    err_msg = f"Pollinations.ai Error {response.status_code}: {response.text}"
                    raise ValueError(err_msg)
                    
            if not images_list:
                raise ValueError("No images were returned by the API.")
                
            self.api_queue.put(("SUCCESS", images_list))
            
        except Exception as e:
            self.api_queue.put(("ERROR", str(e)))

    def process_queue(self):
        try:
            while True:
                msg_type, data = self.api_queue.get_nowait()
                
                # Stop progress bar & restore UI
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.btn_generate.config(state="normal", text="🪄 Generate Artwork")
                
                if msg_type == "SUCCESS":
                    self.generated_images = data
                    self.current_image_idx = 0
                    self.log_message(f"Successfully generated {len(self.generated_images)} images.")
                    
                    if len(self.generated_images) > 1:
                        self.carousel_frame.pack(side="right")
                    
                    self.display_current_image()
                    self.btn_save.config(state="normal")
                else:
                    self.log_message(f"API Error: {data}")
                    messagebox.showerror("API Error Details", f"An error occurred during generation:\n\n{data}")
                    
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

    def display_current_image(self):
        if not self.generated_images:
            return
            
        pil_img = self.generated_images[self.current_image_idx]
        self.lbl_carousel_status.config(text=f"{self.current_image_idx + 1} / {len(self.generated_images)}")
        
        # Calculate resize to fit canvas
        canvas_w = self.canvas_preview.winfo_width()
        canvas_h = self.canvas_preview.winfo_height()
        
        # If canvas not yet rendered/loaded fully, use default bounds
        if canvas_w < 10: canvas_w = 600
        if canvas_h < 10: canvas_h = 400
        
        # Calculate aspect fitting
        img_w, img_h = pil_img.size
        ratio = min(canvas_w / img_w, canvas_h / img_h)
        new_w = int(img_w * ratio) - 10
        new_h = int(img_h * ratio) - 10
        
        resized_img = pil_img.resize((max(new_w, 10), max(new_h, 10)), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_img)
        
        # Draw on canvas
        self.canvas_preview.delete("all")
        self.canvas_preview.create_image(canvas_w // 2, canvas_h // 2, image=self.tk_image, anchor="center")

    def on_preview_resize(self, event):
        # Refresh preview layout to fit new size
        if self.generated_images:
            self.display_current_image()
        else:
            # Re-center placeholder text
            self.canvas_preview.delete("placeholder")
            self.canvas_preview.create_text(
                event.width // 2, event.height // 2, 
                text="Your generated artwork will appear here.\nSet parameters and click Generate!", 
                fill=COLOR_MUTED, font=("Helvetica", 12), justify="center", tags="placeholder"
            )

    def prev_image(self):
        if len(self.generated_images) <= 1:
            return
        self.current_image_idx = (self.current_image_idx - 1) % len(self.generated_images)
        self.display_current_image()

    def next_image(self):
        if len(self.generated_images) <= 1:
            return
        self.current_image_idx = (self.current_image_idx + 1) % len(self.generated_images)
        self.display_current_image()

    def save_current_image(self):
        if not self.generated_images:
            return
        
        current_img = self.generated_images[self.current_image_idx]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")],
            title="Save Generated Artwork"
        )
        if file_path:
            try:
                current_img.save(file_path)
                self.log_message(f"Saved image to: {file_path}")
                messagebox.showinfo("Export Successful", f"Image successfully saved to:\n{file_path}")
            except Exception as e:
                self.log_message(f"Failed to save image: {e}")
                messagebox.showerror("Export Error", f"Could not save image to file:\n{e}")

if __name__ == "__main__":
    app = ImageGenerationStudio()
    app.mainloop()
