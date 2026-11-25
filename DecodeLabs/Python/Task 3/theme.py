"""
Theme and Design System for VaultShield Pro - Ultimate Tkinter Password Generator & Vault
"""

DARK_THEME = {
    "bg_dark": "#0D1117",
    "bg_card": "#161B22",
    "bg_card_hover": "#21262D",
    "bg_sidebar": "#161B22",
    "bg_input": "#0D1117",
    "fg_primary": "#F0F6FC",
    "fg_secondary": "#8B949E",
    "fg_muted": "#484F58",
    "accent_primary": "#58A6FF",
    "accent_primary_hover": "#79C0FF",
    "accent_success": "#3FB950",
    "accent_success_hover": "#56D364",
    "accent_warning": "#D29922",
    "accent_danger": "#F85149",
    "accent_danger_hover": "#FF7B72",
    "accent_purple": "#A371F7",
    "border_color": "#30363D",
    "border_focus": "#58A6FF",
    "shadow_color": "#010409",
    "strength_weak": "#F85149",
    "strength_fair": "#D29922",
    "strength_good": "#E3B341",
    "strength_strong": "#3FB950",
    "strength_godlike": "#A371F7",
}

LIGHT_THEME = {
    "bg_dark": "#F6F8FA",
    "bg_card": "#FFFFFF",
    "bg_card_hover": "#F3F4F6",
    "bg_sidebar": "#FFFFFF",
    "bg_input": "#F6F8FA",
    "fg_primary": "#1F2328",
    "fg_secondary": "#656D76",
    "fg_muted": "#8C959F",
    "accent_primary": "#0969DA",
    "accent_primary_hover": "#0550AE",
    "accent_success": "#1A7F37",
    "accent_success_hover": "#116329",
    "accent_warning": "#9A6700",
    "accent_danger": "#CF222E",
    "accent_danger_hover": "#A40E26",
    "accent_purple": "#8250DF",
    "border_color": "#D0D7DE",
    "border_focus": "#0969DA",
    "shadow_color": "#EAEEF2",
    "strength_weak": "#CF222E",
    "strength_fair": "#9A6700",
    "strength_good": "#BF8700",
    "strength_strong": "#1A7F37",
    "strength_godlike": "#8250DF",
}

class ThemeManager:
    def __init__(self, mode="dark"):
        self.mode = mode
        self.theme = DARK_THEME if mode == "dark" else LIGHT_THEME
        self.listeners = []

    def toggle_theme(self):
        self.mode = "light" if self.mode == "dark" else "dark"
        self.theme = DARK_THEME if self.mode == "dark" else LIGHT_THEME
        for callback in self.listeners:
            callback(self.theme)
        return self.mode

    def get(self, key):
        return self.theme.get(key, "#000000")

    def register_listener(self, callback):
        self.listeners.append(callback)

GLOBAL_THEME = ThemeManager("dark")
