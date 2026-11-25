# Theme and Design System for Apex TaskMaster Pro

class Theme:
    # --- DARK VELVET THEME (Default) ---
    DARK = {
        'bg_root': '#0F172A',         # Deep slate dark
        'bg_sidebar': '#1E293B',      # Darker slate card
        'bg_card': '#1E293B',         # Card container background
        'bg_card_hover': '#334155',   # Hover elevation card
        'bg_input': '#0F172A',        # Input field background
        'text_primary': '#F8FAFC',    # Crisp white text
        'text_secondary': '#94A3B8',  # Muted slate text
        'text_muted': '#64748B',      # Faded text
        'accent_primary': '#6366F1',  # Electric Indigo
        'accent_hover': '#4F46E5',    # Deep Indigo
        'accent_secondary': '#EC4899',# Neon Pink
        'success': '#10B981',         # Emerald Green
        'warning': '#F59E0B',         # Amber
        'danger': '#EF4444',          # Crimson Red
        'info': '#3B82F6',            # Vibrant Blue
        'border': '#334155',          # Subtle border color
        'border_focus': '#6366F1',    # Focused border outline
        'priority_urgent': '#EF4444',
        'priority_high': '#F97316',
        'priority_medium': '#F59E0B',
        'priority_low': '#10B981'
    }

    # --- MODERN LIGHT THEME ---
    LIGHT = {
        'bg_root': '#F8FAFC',         # Soft bright background
        'bg_sidebar': '#FFFFFF',      # Pure white sidebar
        'bg_card': '#FFFFFF',         # White card container
        'bg_card_hover': '#F1F5F9',   # Subtle hover grey
        'bg_input': '#F8FAFC',        # Off-white input background
        'text_primary': '#0F172A',    # Dark slate text
        'text_secondary': '#64748B',  # Medium slate text
        'text_muted': '#94A3B8',      # Light muted text
        'accent_primary': '#4F46E5',  # Royal Indigo
        'accent_hover': '#4338CA',    # Dark Royal Indigo
        'accent_secondary': '#DB2777',# Magenta Pink
        'success': '#059669',         # Deep Emerald
        'warning': '#D97706',         # Deep Amber
        'danger': '#DC2626',          # Deep Red
        'info': '#2563EB',            # Cobalt Blue
        'border': '#E2E8F0',          # Soft border color
        'border_focus': '#4F46E5',    # Focus line
        'priority_urgent': '#DC2626',
        'priority_high': '#EA580C',
        'priority_medium': '#D97706',
        'priority_low': '#059669'
    }

    current = DARK
    is_dark = True

    FONT_FAMILY = "Segoe UI"
    
    @classmethod
    def toggle_theme(cls):
        cls.is_dark = not cls.is_dark
        cls.current = cls.DARK if cls.is_dark else cls.LIGHT
        return cls.current

    @classmethod
    def get_font(cls, size=10, weight="normal", italic=False):
        style = []
        if weight != "normal":
            style.append(weight)
        if italic:
            style.append("italic")
        return (cls.FONT_FAMILY, size, " ".join(style) if style else "normal")

    @classmethod
    def get_priority_color(cls, priority: str) -> str:
        p = priority.lower()
        if 'urgent' in p:
            return cls.current['priority_urgent']
        elif 'high' in p:
            return cls.current['priority_high']
        elif 'medium' in p:
            return cls.current['priority_medium']
        else:
            return cls.current['priority_low']
