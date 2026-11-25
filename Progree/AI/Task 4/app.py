import os
import sys
import time
import math
import glob
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from ultralytics import YOLO

# ---------------------------------------------------------
# UI Color Palette & Design System (Sleek Dark Cyber Studio)
# ---------------------------------------------------------
THEME = {
    "bg_main": "#0d1117",         # Deep dark canvas
    "bg_panel": "#161b22",        # Card background
    "bg_panel_alt": "#21262d",    # Higher elevation
    "bg_sidebar": "#11141a",      # Left sidebar background
    "border": "#30363d",          # Subtle border
    "border_focus": "#58a6ff",    # Neon focus border
    "text_main": "#f0f6fc",       # High contrast white
    "text_muted": "#8b949e",      # Muted gray
    "text_dim": "#484f58",        # Dim label
    "primary": "#238636",         # GitHub Green / Success
    "primary_hover": "#2ea043",
    "accent_cyan": "#38bdf8",     # Cyan / Sky
    "accent_purple": "#a855f7",   # Violet
    "accent_orange": "#fb923c",   # Amber / Warning
    "accent_red": "#f87171",      # Coral / Alert
    "accent_blue": "#3b82f6",     # Vibrant blue
    "card_hover": "#1c2128",
    "chip_bg": "#21262d",
    "chip_active": "#1f6feb"
}

# 80 distinct colors for YOLO classes
CLASS_PALETTE = [
    (56, 189, 248), (168, 85, 247), (251, 146, 60), (248, 113, 113),
    (74, 222, 128), (250, 204, 21), (236, 72, 153), (45, 212, 191),
    (129, 140, 248), (244, 114, 182), (96, 165, 250), (52, 211, 153),
    (251, 191, 36), (239, 68, 68), (147, 51, 234), (59, 130, 246),
    (16, 185, 129), (245, 158, 11), (236, 72, 153), (99, 102, 241),
    (14, 165, 233), (168, 85, 247), (249, 115, 22), (239, 68, 68),
    (34, 197, 94), (234, 179, 8), (217, 70, 239), (20, 184, 166),
    (99, 102, 241), (244, 63, 94), (59, 130, 246), (16, 185, 129),
    (245, 158, 11), (225, 29, 72), (139, 92, 246), (37, 99, 235),
    (5, 150, 105), (217, 119, 6), (190, 24, 93), (79, 70, 229)
]

def get_class_color(cls_id):
    return CLASS_PALETTE[cls_id % len(CLASS_PALETTE)]


class ModernButton(tk.Canvas):
    """Custom styled animated Canvas Button with smooth hover and click transitions."""
    def __init__(self, parent, text, command=None, bg_color=THEME["chip_bg"], 
                 hover_color=THEME["card_hover"], fg_color=THEME["text_main"],
                 accent_color=THEME["accent_cyan"], icon="", font=("Segoe UI", 10, "bold"),
                 width=140, height=36, corner_radius=8, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], 
                         highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self.text = text
        self.icon = icon
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.accent_color = accent_color
        self.font = font
        self.w = width
        self.h = height
        self.r = corner_radius
        self.is_hovered = False
        self.is_active = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.draw()

    def set_text(self, text, icon=None):
        self.text = text
        if icon is not None:
            self.icon = icon
        self.draw()

    def set_active(self, active=True):
        self.is_active = active
        self.draw()

    def _on_enter(self, event):
        self.is_hovered = True
        self.config(cursor="hand2")
        self.draw()

    def _on_leave(self, event):
        self.is_hovered = False
        self.draw()

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_release(self, event):
        self.draw()

    def draw(self):
        self.delete("all")
        bg = self.accent_color if self.is_active else (self.hover_color if self.is_hovered else self.bg_color)
        fg = "#ffffff" if self.is_active else (self.accent_color if self.is_hovered else self.fg_color)
        
        # Rounded rectangle outline / fill
        self._create_rounded_rect(2, 2, self.w-2, self.h-2, self.r, fill=bg, 
                                  outline=self.accent_color if (self.is_active or self.is_hovered) else THEME["border"])
        
        full_text = f"{self.icon} {self.text}".strip() if self.icon else self.text
        self.create_text(self.w // 2, self.h // 2, text=full_text, fill=fg, font=self.font)

    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)


class YOLOVisionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO26 & OpenCV Contour Segmentation Studio")
        self.root.geometry("1420x920")
        self.root.minsize(1180, 760)
        self.root.configure(bg=THEME["bg_main"])

        # Base Paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() and __file__ else os.getcwd()
        
        # Candidate model & images paths
        candidate_model_paths = [
            os.path.join(self.script_dir, "yolo26n.pt"),
            os.path.join(os.getcwd(), "yolo26n.pt"),
            r"d:\AMINE2\COURS FAC\travaux\PROGREE_INTERNSHIP\AI\Task 4\yolo26n.pt"
        ]
        self.default_model_path = next((p for p in candidate_model_paths if os.path.exists(p)), candidate_model_paths[0])

        candidate_coco_dirs = [
            os.path.join(self.script_dir, "images"),
            os.path.join(os.getcwd(), "images"),
            r"d:\AMINE2\COURS FAC\travaux\PROGREE_INTERNSHIP\AI\Task 4\images"
        ]
        self.default_coco_dir = next((p for p in candidate_coco_dirs if os.path.exists(p)), candidate_coco_dirs[0])
        
        # Application State
        self.current_mode = "coco128" # 'coco128' or 'realtime'
        self.model = None
        self.model_loaded = False
        self.conf_threshold = 0.35
        self.iou_threshold = 0.45
        
        # Pipeline Feature Toggles (OpenCV Adaptive Contour & Gaussian Segmentation Pipeline)
        self.enable_yolo = True
        self.enable_contours = True
        self.enable_gaussian = True
        self.enable_adaptive_thresh = True
        self.enable_class_counts = True
        self.enable_fps_overlay = True
        self.adaptive_block_size = 11
        self.adaptive_c = 2
        self.gaussian_ksize = 5
        
        # Dataset Mode State
        self.image_files = []
        self.current_img_index = 0
        self.cached_current_raw = None
        self.cached_current_processed = None
        self.is_slideshow = False
        self.slideshow_speed = 1.0 # seconds
        self.slideshow_job = None
        
        # Real-time Camera State
        self.cap = None
        self.cam_running = False
        self.cam_fps = 0.0
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.cam_device_id = 0

        # Stats & Metrics
        self.inference_time_ms = 0.0
        self.detected_objects_count = {}
        self.total_detections = 0
        self.contours_found = 0

        # Build GUI
        self._setup_styles()
        self._build_header()
        self._build_main_layout()
        self._build_statusbar()

        # Load resources asynchronously
        self.root.after(100, self._init_pipeline)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Custom Scales & Sliders
        style.configure("Cyber.Horizontal.TScale", 
                        background=THEME["bg_panel"],
                        troughcolor=THEME["bg_main"], 
                        bordercolor=THEME["border"],
                        lightcolor=THEME["accent_cyan"],
                        darkcolor=THEME["accent_cyan"])
        
        # Custom Scrollbars
        style.configure("Cyber.Vertical.TScrollbar",
                        background=THEME["bg_panel_alt"],
                        troughcolor=THEME["bg_panel"],
                        bordercolor=THEME["border"],
                        arrowcolor=THEME["accent_cyan"])

    def _build_header(self):
        self.header_frame = tk.Frame(self.root, bg=THEME["bg_sidebar"], height=64, bd=0)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(False)

        # Border line under header
        header_border = tk.Frame(self.root, bg=THEME["border"], height=1)
        header_border.pack(side=tk.TOP, fill=tk.X)

        # Title / Brand Area
        title_box = tk.Frame(self.header_frame, bg=THEME["bg_sidebar"])
        title_box.pack(side=tk.LEFT, padx=20, pady=12)

        logo_label = tk.Label(title_box, text="⚡", font=("Segoe UI", 16, "bold"), 
                              fg=THEME["accent_cyan"], bg=THEME["bg_sidebar"])
        logo_label.pack(side=tk.LEFT, padx=(0, 8))

        brand_label = tk.Label(title_box, text="YOLO26 & OpenCV CV-Pipeline Studio", 
                               font=("Segoe UI", 13, "bold"), fg=THEME["text_main"], bg=THEME["bg_sidebar"])
        brand_label.pack(side=tk.LEFT)

        badge_label = tk.Label(title_box, text=" TASK 4 REAL-TIME / COCO128 ", 
                               font=("Segoe UI", 8, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_panel_alt"],
                               padx=6, pady=2)
        badge_label.pack(side=tk.LEFT, padx=12)

        # Navigation Mode Switcher in Header (Tab Buttons)
        self.mode_nav_frame = tk.Frame(self.header_frame, bg=THEME["bg_sidebar"])
        self.mode_nav_frame.pack(side=tk.RIGHT, padx=20, pady=10)

        self.btn_mode_coco = ModernButton(
            self.mode_nav_frame, text="COCO128 Dataset (128)", icon="🖼️",
            width=175, height=36, bg_color=THEME["bg_panel_alt"],
            accent_color=THEME["accent_cyan"],
            command=lambda: self.switch_mode("coco128")
        )
        self.btn_mode_coco.pack(side=tk.LEFT, padx=6)
        self.btn_mode_coco.set_active(True)

        self.btn_mode_cam = ModernButton(
            self.mode_nav_frame, text="Real-Time Camera", icon="📹",
            width=165, height=36, bg_color=THEME["bg_panel_alt"],
            accent_color=THEME["accent_purple"],
            command=lambda: self.switch_mode("realtime")
        )
        self.btn_mode_cam.pack(side=tk.LEFT, padx=6)

    def _build_main_layout(self):
        self.main_container = tk.Frame(self.root, bg=THEME["bg_main"])
        self.main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Left Column: Interactive Viewport & Live Stream Area
        self.viewport_card = tk.Frame(self.main_container, bg=THEME["bg_panel"], 
                                      highlightbackground=THEME["border"], highlightthickness=1)
        self.viewport_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Viewport Header Bar
        self.vp_header = tk.Frame(self.viewport_card, bg=THEME["bg_panel_alt"], height=42)
        self.vp_header.pack(side=tk.TOP, fill=tk.X)
        self.vp_header.pack_propagate(False)

        self.vp_title_lbl = tk.Label(self.vp_header, text="📷 High-Resolution Canvas Viewport", 
                                     font=("Segoe UI", 10, "bold"), fg=THEME["text_main"], bg=THEME["bg_panel_alt"])
        self.vp_title_lbl.pack(side=tk.LEFT, padx=14)

        self.vp_res_lbl = tk.Label(self.vp_header, text="Res: 0x0 | Latency: 0.0ms", 
                                   font=("Consolas", 9), fg=THEME["accent_cyan"], bg=THEME["bg_panel_alt"])
        self.vp_res_lbl.pack(side=tk.RIGHT, padx=14)

        # Main Canvas with auto resize handler
        self.canvas = tk.Canvas(self.viewport_card, bg="#080b0f", highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Viewport Bottom Controls (Dataset navigation / Playback bar)
        self.vp_controls = tk.Frame(self.viewport_card, bg=THEME["bg_panel_alt"], height=52)
        self.vp_controls.pack(side=tk.BOTTOM, fill=tk.X)
        self.vp_controls.pack_propagate(False)

        self._build_viewport_controls()

        # Right Column: Side Control Dashboard & Diagnostics Panel
        self.sidebar_card = tk.Frame(self.main_container, bg=THEME["bg_panel"], width=420,
                                     highlightbackground=THEME["border"], highlightthickness=1)
        self.sidebar_card.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        self.sidebar_card.pack_propagate(False)

        self._build_sidebar_controls()

    def _build_viewport_controls(self):
        # Container inside vp_controls
        self.dataset_nav_box = tk.Frame(self.vp_controls, bg=THEME["bg_panel_alt"])
        self.dataset_nav_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # Prev Button
        self.btn_prev = ModernButton(self.dataset_nav_box, text="Prev", icon="◀", width=80, height=32,
                                     bg_color=THEME["bg_panel"], hover_color=THEME["border"],
                                     command=self.prev_image)
        self.btn_prev.pack(side=tk.LEFT, padx=4)

        # Index / Count Indicator
        self.lbl_img_counter = tk.Label(self.dataset_nav_box, text="Image 001 / 128", 
                                        font=("Segoe UI", 10, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_panel_alt"])
        self.lbl_img_counter.pack(side=tk.LEFT, padx=10)

        # Next Button
        self.btn_next = ModernButton(self.dataset_nav_box, text="Next", icon="▶", width=80, height=32,
                                     bg_color=THEME["bg_panel"], hover_color=THEME["border"],
                                     command=self.next_image)
        self.btn_next.pack(side=tk.LEFT, padx=4)

        # Slideshow / Auto-Play Button
        self.btn_play = ModernButton(self.dataset_nav_box, text="Play Loop", icon="▶️", width=105, height=32,
                                     bg_color=THEME["bg_panel"], hover_color=THEME["primary"],
                                     command=self.toggle_slideshow)
        self.btn_play.pack(side=tk.LEFT, padx=10)

        # Direct Image Slider
        self.img_slider = ttk.Scale(self.dataset_nav_box, from_=1, to=128, orient=tk.HORIZONTAL,
                                    style="Cyber.Horizontal.TScale", command=self._on_slider_move)
        self.img_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 4))

        # Real-time Camera Controls Box (Hidden by default until camera mode activated)
        self.camera_ctrl_box = tk.Frame(self.vp_controls, bg=THEME["bg_panel_alt"])
        
        self.btn_cam_toggle = ModernButton(self.camera_ctrl_box, text="Start Stream", icon="▶", width=130, height=32,
                                           bg_color=THEME["primary"], hover_color=THEME["primary_hover"],
                                           command=self.toggle_camera)
        self.btn_cam_toggle.pack(side=tk.LEFT, padx=6)

        self.btn_cam_snapshot = ModernButton(self.camera_ctrl_box, text="Save Snapshot", icon="📸", width=130, height=32,
                                             bg_color=THEME["bg_panel"], hover_color=THEME["border"],
                                             command=self.save_snapshot)
        self.btn_cam_snapshot.pack(side=tk.LEFT, padx=6)

        self.lbl_cam_status = tk.Label(self.camera_ctrl_box, text="Camera: Idle", 
                                       font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_panel_alt"])
        self.lbl_cam_status.pack(side=tk.RIGHT, padx=12)

    def _build_sidebar_controls(self):
        canvas_sidebar = tk.Canvas(self.sidebar_card, bg=THEME["bg_panel"], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.sidebar_card, orient="vertical", command=canvas_sidebar.yview,
                                  style="Cyber.Vertical.TScrollbar")
        self.scroll_content = tk.Frame(canvas_sidebar, bg=THEME["bg_panel"])

        self.scroll_content.bind(
            "<Configure>",
            lambda e: canvas_sidebar.configure(scrollregion=canvas_sidebar.bbox("all"))
        )

        canvas_sidebar.create_window((0, 0), window=self.scroll_content, anchor="nw", width=400)
        canvas_sidebar.configure(yscrollcommand=scrollbar.set)

        canvas_sidebar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        pad = 12

        # ---------------- Section 1: AI Model & Pipeline Status ----------------
        sec1 = self._create_section_card(self.scroll_content, "🧠 AI Model & Pipeline Architecture")
        
        self.lbl_model_info = tk.Label(sec1, text="Model: YOLO26 Nano (yolo26n.pt)\nTask: 2D Object Detection & Frame Segmentation",
                                       font=("Segoe UI", 9), fg=THEME["text_main"], bg=THEME["bg_panel_alt"],
                                       justify=tk.LEFT, anchor="w")
        self.lbl_model_info.pack(fill=tk.X, padx=pad, pady=(6, 8))

        # Confidence Slider
        cf_box = tk.Frame(sec1, bg=THEME["bg_panel_alt"])
        cf_box.pack(fill=tk.X, padx=pad, pady=3)
        self.lbl_conf = tk.Label(cf_box, text=f"Confidence Threshold: {int(self.conf_threshold*100)}%", 
                                 font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_panel_alt"])
        self.lbl_conf.pack(anchor="w")
        self.slider_conf = ttk.Scale(cf_box, from_=0.05, to=0.95, value=self.conf_threshold,
                                     orient=tk.HORIZONTAL, style="Cyber.Horizontal.TScale",
                                     command=self._on_conf_change)
        self.slider_conf.pack(fill=tk.X, pady=2)

        # IOU NMS Slider
        iou_box = tk.Frame(sec1, bg=THEME["bg_panel_alt"])
        iou_box.pack(fill=tk.X, padx=pad, pady=3)
        self.lbl_iou = tk.Label(iou_box, text=f"IoU NMS Threshold: {int(self.iou_threshold*100)}%", 
                                font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_panel_alt"])
        self.lbl_iou.pack(anchor="w")
        self.slider_iou = ttk.Scale(iou_box, from_=0.10, to=0.90, value=self.iou_threshold,
                                    orient=tk.HORIZONTAL, style="Cyber.Horizontal.TScale",
                                    command=self._on_iou_change)
        self.slider_iou.pack(fill=tk.X, pady=2)

        # ---------------- Section 2: OpenCV Pipeline Toggles ----------------
        sec2 = self._create_section_card(self.scroll_content, "⚙️ Image & Stream Pipeline Filters")

        self.var_yolo = tk.BooleanVar(value=self.enable_yolo)
        self.var_contours = tk.BooleanVar(value=self.enable_contours)
        self.var_gaussian = tk.BooleanVar(value=self.enable_gaussian)
        self.var_thresh = tk.BooleanVar(value=self.enable_adaptive_thresh)
        self.var_counts = tk.BooleanVar(value=self.enable_class_counts)

        self._create_check_item(sec2, "YOLO26 Bounding Boxes & Confidence Tags", self.var_yolo, self._on_toggle_pipeline)
        self._create_check_item(sec2, "Adaptive Threshold Matrix Shapes", self.var_thresh, self._on_toggle_pipeline)
        self._create_check_item(sec2, "Gaussian Filter Contour Smoothing", self.var_gaussian, self._on_toggle_pipeline)
        self._create_check_item(sec2, "Extract & Draw Pixel Bound Contours", self.var_contours, self._on_toggle_pipeline)
        self._create_check_item(sec2, "Dynamic Text Count Vectors Overlay", self.var_counts, self._on_toggle_pipeline)

        # ---------------- Section 3: Live Detection Telemetry ----------------
        sec3 = self._create_section_card(self.scroll_content, "📊 Frame Metrics & Dynamic Count Vectors")

        metrics_grid = tk.Frame(sec3, bg=THEME["bg_panel_alt"])
        metrics_grid.pack(fill=tk.X, padx=pad, pady=4)

        self.lbl_stat_objects = self._create_metric_pill(metrics_grid, "Detections", "0", THEME["accent_cyan"], col=0)
        self.lbl_stat_contours = self._create_metric_pill(metrics_grid, "Contours", "0", THEME["accent_purple"], col=1)
        self.lbl_stat_fps = self._create_metric_pill(metrics_grid, "Inference", "0 ms", THEME["accent_orange"], col=2)

        # Detected Classes Summary Tree / Table
        self.tree_frame = tk.Frame(sec3, bg=THEME["bg_panel_alt"])
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=pad, pady=6)

        self.class_listbox = tk.Text(self.tree_frame, height=7, bg=THEME["bg_main"], fg=THEME["text_main"],
                                     font=("Consolas", 9), bd=0, highlightbackground=THEME["border"],
                                     highlightthickness=1, wrap=tk.NONE)
        self.class_listbox.pack(fill=tk.BOTH, expand=True)

        # ---------------- Section 4: Quick Actions ----------------
        sec4 = self._create_section_card(self.scroll_content, "🚀 Actions & Dataset Explorer")
        
        btn_action_box = tk.Frame(sec4, bg=THEME["bg_panel_alt"])
        btn_action_box.pack(fill=tk.X, padx=pad, pady=6)

        btn_open_custom = ModernButton(btn_action_box, text="Load Custom Image", icon="📂", width=170, height=32,
                                       bg_color=THEME["bg_panel"], hover_color=THEME["border"],
                                       command=self.load_custom_image)
        btn_open_custom.pack(side=tk.LEFT, padx=3)

        btn_save_result = ModernButton(btn_action_box, text="Export Detection", icon="💾", width=170, height=32,
                                       bg_color=THEME["bg_panel"], hover_color=THEME["border"],
                                       command=self.export_processed_image)
        btn_save_result.pack(side=tk.LEFT, padx=3)

    def _create_section_card(self, parent, title):
        card = tk.Frame(parent, bg=THEME["bg_panel_alt"], highlightbackground=THEME["border"], highlightthickness=1)
        card.pack(fill=tk.X, padx=12, pady=6)

        header = tk.Frame(card, bg=THEME["bg_panel_alt"])
        header.pack(fill=tk.X, padx=10, pady=(8, 4))

        lbl = tk.Label(header, text=title, font=("Segoe UI", 9, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_panel_alt"])
        lbl.pack(side=tk.LEFT)

        sep = tk.Frame(card, bg=THEME["border"], height=1)
        sep.pack(fill=tk.X, pady=2)
        return card

    def _create_check_item(self, parent, text, var, callback):
        box = tk.Frame(parent, bg=THEME["bg_panel_alt"])
        box.pack(fill=tk.X, padx=12, pady=3)

        cb = tk.Checkbutton(box, text=text, variable=var, command=callback,
                            bg=THEME["bg_panel_alt"], fg=THEME["text_main"],
                            selectcolor=THEME["bg_main"], activebackground=THEME["bg_panel_alt"],
                            activeforeground=THEME["accent_cyan"], font=("Segoe UI", 9))
        cb.pack(anchor="w")

    def _create_metric_pill(self, parent, label_txt, val_txt, color, col=0):
        parent.grid_columnconfigure(col, weight=1)
        pill = tk.Frame(parent, bg=THEME["bg_main"], highlightbackground=THEME["border"], highlightthickness=1)
        pill.grid(row=0, column=col, padx=3, pady=4, sticky="nsew")

        lbl = tk.Label(pill, text=label_txt, font=("Segoe UI", 8), fg=THEME["text_muted"], bg=THEME["bg_main"])
        lbl.pack(pady=(4, 0))

        val = tk.Label(pill, text=val_txt, font=("Segoe UI", 11, "bold"), fg=color, bg=THEME["bg_main"])
        val.pack(pady=(0, 4))
        return val

    def _build_statusbar(self):
        self.statusbar = tk.Frame(self.root, bg=THEME["bg_sidebar"], height=28)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.statusbar.pack_propagate(False)

        status_border = tk.Frame(self.root, bg=THEME["border"], height=1)
        status_border.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status = tk.Label(self.statusbar, text="Initializing YOLO26 Engine...", 
                                   font=("Segoe UI", 8), fg=THEME["text_muted"], bg=THEME["bg_sidebar"])
        self.lbl_status.pack(side=tk.LEFT, padx=16)

        self.lbl_engine_info = tk.Label(self.statusbar, text="Ultralytics YOLO26 | OpenCV 4.10 | Tkinter UI", 
                                        font=("Segoe UI", 8), fg=THEME["text_dim"], bg=THEME["bg_sidebar"])
        self.lbl_engine_info.pack(side=tk.RIGHT, padx=16)

    # ---------------------------------------------------------
    # Pipeline & Model Initialization
    # ---------------------------------------------------------
    def _init_pipeline(self):
        try:
            self.lbl_status.config(text="Loading YOLO26 weights (yolo26n.pt)...", fg=THEME["accent_orange"])
            self.root.update_idletasks()

            # Load YOLO26 model
            if os.path.exists(self.default_model_path):
                self.model = YOLO(self.default_model_path)
                self.model_loaded = True
                self.lbl_status.config(text="✅ YOLO26 Model Loaded Successfully", fg=THEME["accent_cyan"])
            else:
                messagebox.showerror("Model Not Found", f"Cannot find {self.default_model_path}")
                self.lbl_status.config(text="❌ Failed to find model file", fg=THEME["accent_red"])

            # Load COCO128 images
            if os.path.exists(self.default_coco_dir):
                valid_exts = (".jpg", ".jpeg", ".png", ".bmp")
                self.image_files = sorted([
                    os.path.join(self.default_coco_dir, f) for f in os.listdir(self.default_coco_dir)
                    if f.lower().endswith(valid_exts)
                ])
                if self.image_files:
                    self.img_slider.config(to=len(self.image_files))
                    self.current_img_index = 0
                    self.display_current_image()
                else:
                    self.lbl_status.config(text="No images found in images folder", fg=THEME["accent_red"])
            else:
                self.lbl_status.config(text="Images directory not found", fg=THEME["accent_red"])

        except Exception as e:
            self.lbl_status.config(text=f"Error: {str(e)}", fg=THEME["accent_red"])
            messagebox.showerror("Initialization Error", str(e))

    # ---------------------------------------------------------
    # Mode Switching: COCO128 Dataset vs Real-Time Camera
    # ---------------------------------------------------------
    def switch_mode(self, mode):
        if self.current_mode == mode:
            return

        self.current_mode = mode

        if mode == "coco128":
            self.stop_camera()
            self.btn_mode_coco.set_active(True)
            self.btn_mode_cam.set_active(False)
            
            self.camera_ctrl_box.pack_forget()
            self.dataset_nav_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
            self.vp_title_lbl.config(text="🖼️ COCO128 Dataset Browser & Computer Vision Inspector")
            
            self.display_current_image()
        
        elif mode == "realtime":
            self.stop_slideshow()
            self.btn_mode_coco.set_active(False)
            self.btn_mode_cam.set_active(True)

            self.dataset_nav_box.pack_forget()
            self.camera_ctrl_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
            self.vp_title_lbl.config(text="📹 Live Camera Real-Time Object & Contour Stream")

            self.start_camera()

    # ---------------------------------------------------------
    # Core Image Processing & YOLO Computer Vision Pipeline
    # ---------------------------------------------------------
    def process_frame(self, frame_bgr):
        h, w = frame_bgr.shape[:2]
        output_frame = frame_bgr.copy()
        
        t0 = time.time()
        class_counts = {}
        total_dets = 0
        contour_count = 0

        # Step 1: Pre-processing & Adaptive Contour Extraction
        if self.enable_contours or self.enable_adaptive_thresh:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            if self.enable_gaussian:
                gray_blurred = cv2.GaussianBlur(gray, (self.gaussian_ksize, self.gaussian_ksize), 0)
            else:
                gray_blurred = gray

            if self.enable_adaptive_thresh:
                thresh = cv2.adaptiveThreshold(
                    gray_blurred, 255, 
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY_INV, 
                    self.adaptive_block_size, 
                    self.adaptive_c
                )
            else:
                _, thresh = cv2.threshold(gray_blurred, 127, 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if self.enable_contours:
                prominent_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 150]
                contour_count = len(prominent_contours)
                cv2.drawContours(output_frame, prominent_contours, -1, (255, 200, 0), 1, cv2.LINE_AA)

        # Step 2: YOLO26 Object Detection
        if self.enable_yolo and self.model_loaded and self.model is not None:
            results = self.model.predict(
                source=frame_bgr, 
                conf=self.conf_threshold, 
                iou=self.iou_threshold, 
                verbose=False
            )
            
            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None:
                    total_dets = len(boxes)
                    
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        conf = float(box.conf[0].item())
                        xyxy = box.xyxy[0].cpu().numpy().astype(int)
                        x1, y1, x2, y2 = xyxy

                        class_name = self.model.names.get(cls_id, f"Class {cls_id}")
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1

                        rgb_color = get_class_color(cls_id)
                        bgr_color = (int(rgb_color[2]), int(rgb_color[1]), int(rgb_color[0]))

                        cv2.rectangle(output_frame, (x1, y1), (x2, y2), bgr_color, 2, cv2.LINE_AA)
                        
                        corner_len = min(15, (x2 - x1) // 4, (y2 - y1) // 4)
                        cv2.line(output_frame, (x1, y1), (x1 + corner_len, y1), (255, 255, 255), 3)
                        cv2.line(output_frame, (x1, y1), (x1, y1 + corner_len), (255, 255, 255), 3)
                        cv2.line(output_frame, (x2, y2), (x2 - corner_len, y2), (255, 255, 255), 3)
                        cv2.line(output_frame, (x2, y2), (x2, y2 - corner_len), (255, 255, 255), 3)

                        tag_text = f"{class_name} {int(conf * 100)}%"
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.52
                        thickness = 1
                        (text_w, text_h), baseline = cv2.getTextSize(tag_text, font, font_scale, thickness)
                        
                        tag_y1 = max(0, y1 - text_h - 8)
                        tag_y2 = y1
                        cv2.rectangle(output_frame, (x1, tag_y1), (x1 + text_w + 10, tag_y2), bgr_color, -1)
                        cv2.putText(output_frame, tag_text, (x1 + 5, y1 - 4), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

        t1 = time.time()
        inf_ms = (t1 - t0) * 1000.0

        # Step 3: Overlay Dynamic Text Count Vectors
        if self.enable_class_counts and class_counts:
            overlay_h = 30 + len(class_counts) * 22
            overlay_w = 220
            overlay = output_frame.copy()
            cv2.rectangle(overlay, (12, 12), (12 + overlay_w, 12 + overlay_h), (15, 18, 24), -1)
            cv2.addWeighted(overlay, 0.75, output_frame, 0.25, 0, output_frame)
            cv2.rectangle(output_frame, (12, 12), (12 + overlay_w, 12 + overlay_h), (80, 180, 240), 1)

            cv2.putText(output_frame, "DYNAMIC CLASS VECTORS", (20, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (56, 189, 248), 1, cv2.LINE_AA)

            row_y = 52
            for c_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:6]:
                txt = f"• {c_name}: {count}"
                cv2.putText(output_frame, txt, (22, row_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 246, 252), 1, cv2.LINE_AA)
                row_y += 20

        return output_frame, inf_ms, total_dets, contour_count, class_counts

    # ---------------------------------------------------------
    # COCO128 Dataset Navigation & Rendering
    # ---------------------------------------------------------
    def display_current_image(self):
        if not self.image_files:
            return

        img_path = self.image_files[self.current_img_index]
        self.lbl_img_counter.config(text=f"Image {self.current_img_index + 1:03d} / {len(self.image_files):03d}")
        self.img_slider.set(self.current_img_index + 1)
        
        raw_bgr = cv2.imread(img_path)
        if raw_bgr is None:
            self.lbl_status.config(text=f"Failed to read image: {os.path.basename(img_path)}", fg=THEME["accent_red"])
            return

        self.cached_current_raw = raw_bgr
        
        processed_bgr, inf_ms, total_dets, contour_cnt, class_counts = self.process_frame(raw_bgr)
        self.cached_current_processed = processed_bgr

        self._update_metrics(inf_ms, total_dets, contour_cnt, class_counts)
        self._render_to_canvas(processed_bgr)
        
        filename = os.path.basename(img_path)
        h, w = raw_bgr.shape[:2]
        self.vp_res_lbl.config(text=f"{filename} | {w}x{h} | Latency: {inf_ms:.1f}ms")
        self.lbl_status.config(text=f"Processed: {filename} ({total_dets} objects, {contour_cnt} contours)", fg=THEME["text_muted"])

    def _render_to_canvas(self, bgr_img):
        if bgr_img is None:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw < 50 or ch < 50:
            cw = 860
            ch = 620

        ih, iw = bgr_img.shape[:2]
        scale = min(cw / iw, ch / ih)
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))

        resized = cv2.resize(bgr_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        rgb_img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        self.tk_photo = ImageTk.PhotoImage(image=pil_img)

        self.canvas.delete("all")
        pos_x = (cw - new_w) // 2
        pos_y = (ch - new_h) // 2
        self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self.tk_photo)

    def _on_canvas_resize(self, event):
        if self.current_mode == "coco128" and self.cached_current_processed is not None:
            self._render_to_canvas(self.cached_current_processed)

    def next_image(self):
        if not self.image_files:
            return
        self.current_img_index = (self.current_img_index + 1) % len(self.image_files)
        self.display_current_image()

    def prev_image(self):
        if not self.image_files:
            return
        self.current_img_index = (self.current_img_index - 1) % len(self.image_files)
        self.display_current_image()

    def _on_slider_move(self, val):
        idx = int(float(val)) - 1
        if 0 <= idx < len(self.image_files) and idx != self.current_img_index:
            self.current_img_index = idx
            self.display_current_image()

    def toggle_slideshow(self):
        if self.is_slideshow:
            self.stop_slideshow()
        else:
            self.is_slideshow = True
            self.btn_play.set_text("Pause", icon="⏸️")
            self.btn_play.set_active(True)
            self._run_slideshow_step()

    def stop_slideshow(self):
        self.is_slideshow = False
        self.btn_play.set_text("Play Loop", icon="▶️")
        self.btn_play.set_active(False)
        if self.slideshow_job is not None:
            self.root.after_cancel(self.slideshow_job)
            self.slideshow_job = None

    def _run_slideshow_step(self):
        if not self.is_slideshow:
            return
        self.next_image()
        self.slideshow_job = self.root.after(int(self.slideshow_speed * 1000), self._run_slideshow_step)

    # ---------------------------------------------------------
    # Real-Time Camera Stream Handler
    # ---------------------------------------------------------
    def start_camera(self):
        if self.cam_running:
            return

        self.cap = cv2.VideoCapture(self.cam_device_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.cam_device_id)

        if not self.cap.isOpened():
            self.lbl_cam_status.config(text="Camera Error: Device not accessible", fg=THEME["accent_red"])
            messagebox.showwarning("Camera Warning", "Could not open webcam. Ensure your camera is connected and not in use by another program.")
            return

        self.cam_running = True
        self.btn_cam_toggle.set_text("Stop Stream", icon="⏹")
        self.btn_cam_toggle.bg_color = THEME["accent_red"]
        self.btn_cam_toggle.draw()
        self.lbl_cam_status.config(text="Live Stream: RUNNING (60 FPS)", fg=THEME["primary_hover"])

        self.last_frame_time = time.time()
        self.frame_count = 0
        self._camera_loop()

    def stop_camera(self):
        self.cam_running = False
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        self.btn_cam_toggle.set_text("Start Stream", icon="▶")
        self.btn_cam_toggle.bg_color = THEME["primary"]
        self.btn_cam_toggle.draw()
        self.lbl_cam_status.config(text="Camera: Idle", fg=THEME["text_muted"])

    def toggle_camera(self):
        if self.cam_running:
            self.stop_camera()
        else:
            self.start_camera()

    def _camera_loop(self):
        if not self.cam_running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret and frame is not None:
            processed_frame, inf_ms, total_dets, contour_cnt, class_counts = self.process_frame(frame)
            self.cached_current_processed = processed_frame

            self.frame_count += 1
            now = time.time()
            dt = now - self.last_frame_time
            if dt >= 0.5:
                self.cam_fps = self.frame_count / dt
                self.frame_count = 0
                self.last_frame_time = now

            h, w = frame.shape[:2]
            self.vp_res_lbl.config(text=f"Camera ({w}x{h}) | FPS: {self.cam_fps:.1f} | Latency: {inf_ms:.1f}ms")
            self._update_metrics(inf_ms, total_dets, contour_cnt, class_counts)
            self._render_to_canvas(processed_frame)

        if self.cam_running:
            self.root.after(15, self._camera_loop)

    def save_snapshot(self):
        if self.cached_current_processed is None:
            messagebox.showinfo("Snapshot", "No frame available to save.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.png"
        save_path = os.path.join(self.script_dir, filename)
        
        cv2.imwrite(save_path, self.cached_current_processed)
        messagebox.showinfo("Snapshot Saved", f"Saved successfully to:\n{save_path}")

    # ---------------------------------------------------------
    # Custom File Loader & Export
    # ---------------------------------------------------------
    def load_custom_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if file_path:
            if file_path not in self.image_files:
                self.image_files.append(file_path)
                self.img_slider.config(to=len(self.image_files))
            
            self.current_img_index = self.image_files.index(file_path)
            self.switch_mode("coco128")
            self.display_current_image()

    def export_processed_image(self):
        if self.cached_current_processed is None:
            messagebox.showinfo("Export", "No image currently processed.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")]
        )
        if file_path:
            cv2.imwrite(file_path, self.cached_current_processed)
            messagebox.showinfo("Export Success", f"Image exported successfully to:\n{file_path}")

    # ---------------------------------------------------------
    # Dashboard Telemetry & UI Event Handlers
    # ---------------------------------------------------------
    def _update_metrics(self, inf_ms, total_dets, contour_cnt, class_counts):
        self.lbl_stat_fps.config(text=f"{inf_ms:.1f} ms")
        self.lbl_stat_objects.config(text=str(total_dets))
        self.lbl_stat_contours.config(text=str(contour_cnt))

        self.class_listbox.config(state=tk.NORMAL)
        self.class_listbox.delete("1.0", tk.END)
        
        if not class_counts:
            self.class_listbox.insert(tk.END, "  No target objects detected.\n")
        else:
            self.class_listbox.insert(tk.END, f"{'CLASS':<16}{'COUNT':<8}\n")
            self.class_listbox.insert(tk.END, "-" * 26 + "\n")
            for cls_name, cnt in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
                self.class_listbox.insert(tk.END, f"  {cls_name:<14} x{cnt:<6}\n")

        self.class_listbox.config(state=tk.DISABLED)

    def _on_conf_change(self, val):
        self.conf_threshold = float(val)
        self.lbl_conf.config(text=f"Confidence Threshold: {int(self.conf_threshold*100)}%")
        if self.current_mode == "coco128":
            self.display_current_image()

    def _on_iou_change(self, val):
        self.iou_threshold = float(val)
        self.lbl_iou.config(text=f"IoU NMS Threshold: {int(self.iou_threshold*100)}%")
        if self.current_mode == "coco128":
            self.display_current_image()

    def _on_toggle_pipeline(self):
        self.enable_yolo = self.var_yolo.get()
        self.enable_contours = self.var_contours.get()
        self.enable_gaussian = self.var_gaussian.get()
        self.enable_adaptive_thresh = self.var_thresh.get()
        self.enable_class_counts = self.var_counts.get()
        if self.current_mode == "coco128":
            self.display_current_image()

    def on_closing(self):
        self.stop_slideshow()
        self.stop_camera()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = YOLOVisionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
