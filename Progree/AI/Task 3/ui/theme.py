"""
Modern Dark Theme Design System and Color Tokens.
"""

class Theme:
    # App Backgrounds
    BG_DARK = "#090d16"         # Deep obsidian
    BG_PANEL = "#0f172a"        # Slate 900 panel background
    BG_CARD = "#1e293b"         # Slate 800 card background
    BG_CARD_HOVER = "#334155"   # Slate 700
    BG_INPUT = "#0f172a"        # Deep input field bg
    BORDER_COLOR = "#334155"    # Subtle divider border
    BORDER_ACCENT = "#38bdf8"   # Sky blue focus border

    # Typography Colors
    TEXT_PRIMARY = "#f8fafc"    # Bright white
    TEXT_SECONDARY = "#94a3b8"  # Muted slate
    TEXT_MUTED = "#64748b"      # Dark slate
    TEXT_ACCENT = "#38bdf8"     # Electric cyan

    # Neon Brand Accents
    ACCENT_CYAN = "#06b6d4"
    ACCENT_SKY = "#38bdf8"
    ACCENT_INDIGO = "#6366f1"
    ACCENT_VIOLET = "#8b5cf6"
    ACCENT_EMERALD = "#10b981"
    ACCENT_ROSE = "#f43f5e"
    ACCENT_AMBER = "#f59e0b"

    # Grid Cell Visual Styling
    CELL_BG_EMPTY = "#131b2e"
    CELL_BORDER = "#1e293b"
    CELL_WALL = "#334155"
    CELL_WALL_BORDER = "#475569"
    CELL_MUD = "#78350f"        # Mud brown/amber
    CELL_WATER = "#0369a1"      # Water deep cyan
    CELL_FOREST = "#065f46"     # Forest green

    # Pathfinding Animation States
    NODE_START = "#10b981"       # Glowing Emerald
    NODE_GOAL = "#f43f5e"        # Glowing Rose
    NODE_CURRENT = "#fbbf24"     # Active yellow search head
    NODE_OPEN = "#0284c7"        # Sky blue frontier
    NODE_OPEN_PULSE = "#38bdf8"
    NODE_CLOSED = "#4f46e5"      # Indigo explored
    NODE_CLOSED_PALE = "#4338ca"
    NODE_PATH = "#22c55e"        # Neon spring green final path
    NODE_PATH_GLOW = "#86efac"
    AGENT_TOKEN = "#e11d48"      # Bright crimson virtual agent pin

    # Typography configurations
    FONT_FAMILY = "Segoe UI"
    FONT_HEADING = ("Segoe UI", 16, "bold")
    FONT_SUBHEADING = ("Segoe UI", 12, "bold")
    FONT_BODY = ("Segoe UI", 10)
    FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
    FONT_CODE = ("Consolas", 10)
    FONT_METRIC_VAL = ("Segoe UI", 18, "bold")
    FONT_METRIC_LABEL = ("Segoe UI", 9)
