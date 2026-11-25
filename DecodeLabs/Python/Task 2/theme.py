"""
theme.py - Theme and Style Constants for ApexExpense
Defines dark and light color palettes, font configurations, category icons/colors, and helper functions.
"""

DARK_THEME = {
    "bg_dim": "#0F172A",          # Deep midnight background
    "bg_card": "#1E293B",         # Sleek dark card container
    "bg_card_hover": "#334155",   # Card hover state
    "bg_input": "#0F172A",        # Input background
    "border": "#334155",          # Border line
    "border_highlight": "#6366F1",# Focused border
    
    "text_primary": "#F8FAFC",    # Primary white-ish text
    "text_secondary": "#94A3B8",  # Muted grey text
    "text_accent": "#38BDF8",     # Sky blue accent
    
    "accent_primary": "#6366F1",  # Indigo accent
    "accent_hover": "#4F46E5",    # Dark indigo hover
    "accent_success": "#10B981",  # Emerald green
    "accent_warning": "#F59E0B",  # Amber gold
    "accent_danger": "#EF4444",   # Rose red
    "accent_info": "#06B6D4",      # Cyan
    
    "chart_bg": "#1E293B",
    "chart_text": "#F8FAFC"
}

LIGHT_THEME = {
    "bg_dim": "#F1F5F9",          # Soft light slate background
    "bg_card": "#FFFFFF",         # Pure white card container
    "bg_card_hover": "#F8FAFC",   # Card hover state
    "bg_input": "#FFFFFF",        # Input background
    "border": "#E2E8F0",          # Light border
    "border_highlight": "#4338CA",# Focused border
    
    "text_primary": "#0F172A",    # Dark primary text
    "text_secondary": "#64748B",  # Slate muted text
    "text_accent": "#0284C7",     # Sky blue accent
    
    "accent_primary": "#4F46E5",  # Deep indigo
    "accent_hover": "#4338CA",    # Indigo hover
    "accent_success": "#059669",  # Emerald green
    "accent_warning": "#D97706",  # Amber gold
    "accent_danger": "#DC2626",   # Red accent
    "accent_info": "#0891B2",      # Cyan accent
    
    "chart_bg": "#FFFFFF",
    "chart_text": "#0F172A"
}

# Default palette active
THEME = DARK_THEME.copy()

# Category Color Mapping & Icons
CATEGORY_PRESETS = {
    "Food & Dining": {"color": "#EF4444", "icon": "🍔"},
    "Transport & Fuel": {"color": "#F59E0B", "icon": "🚗"},
    "Shopping & Retail": {"color": "#EC4899", "icon": "🛍️"},
    "Bills & Utilities": {"color": "#3B82F6", "icon": "💡"},
    "Entertainment & Fun": {"color": "#8B5CF6", "icon": "🎬"},
    "Health & Fitness": {"color": "#10B981", "icon": "💊"},
    "Travel & Vacation": {"color": "#06B6D4", "icon": "✈️"},
    "Education & Courses": {"color": "#6366F1", "icon": "📚"},
    "Salary & Income": {"color": "#10B981", "icon": "💰"},
    "Investment & Stocks": {"color": "#14B8A6", "icon": "📈"},
    "Miscellaneous": {"color": "#64748B", "icon": "📦"}
}

PAYMENT_METHODS = [
    "💳 Credit Card",
    "🏦 Bank Transfer",
    "💵 Cash",
    "📱 PayPal / E-Wallet",
    "🪙 Crypto",
    "📄 Check / Other"
]

CURRENCIES = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "JPY (¥)": "¥",
    "MAD (DH)": "DH",
    "CAD ($)": "CA$",
    "AUD ($)": "A$",
    "INR (₹)": "₹"
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 14, "bold"),
    "heading": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10, "normal"),
    "body_bold": ("Segoe UI", 10, "bold"),
    "caption": ("Segoe UI", 9, "normal"),
    "number_large": ("Segoe UI", 24, "bold"),
    "number_medium": ("Segoe UI", 16, "bold"),
    "icon": ("Segoe UI Emoji", 14)
}
