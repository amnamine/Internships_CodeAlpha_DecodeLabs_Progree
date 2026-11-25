import sys
import math
import random
import array
import pygame

# Initialize Pygame and Mixer
pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
except Exception:
    # Handle environment where audio device is not available
    pass

# Initialize Fonts
pygame.font.init()

# ==============================================================================
# Game Configuration & Constants
# ==============================================================================
class Config:
    WIDTH = 1024
    HEIGHT = 768
    FPS = 60
    
    # Elegant Modern Color Palette (Dark Theme with Pastel/Neon Accents)
    COLOR_BG = (18, 18, 24)           # Deep rich dark blue-gray
    COLOR_CARD = (30, 31, 42)         # Slightly lighter slate for panels
    COLOR_TEXT_MAIN = (240, 240, 245) # Clean off-white
    COLOR_TEXT_MUTED = (140, 143, 160)# Muted grayish purple
    COLOR_ACCENT = (0, 180, 216)      # Cyan Accent
    COLOR_ACCENT_HOVER = (72, 202, 228)
    COLOR_CORRECT = (46, 196, 182)    # Emerald
    COLOR_INCORRECT = (231, 76, 60)   # Coral Red
    COLOR_BORDER = (47, 50, 69)       # Panel borders
    COLOR_KEY_USED = (60, 63, 80)     # Darkened key background
    
    # Word Databases
    CATEGORIES = {
        "TECHNOLOGY": [
            "DEVELOPER", "PYGAME", "PYTHON", "COMPUTER", "ALGORITHM",
            "DATABASE", "SOFTWARE", "HARDWARE", "INTERNET", "CYBERSECURITY"
        ],
        "ANIMALS": [
            "ELEPHANT", "GIRAFFE", "KANGAROO", "DOLPHIN", "PENGUIN",
            "CHEETAH", "CHIMPANZEE", "OCTOPUS", "FLAMINGO", "PLATYPUS"
        ],
        "COUNTRIES": [
            "AUSTRALIA", "BRAZIL", "CANADA", "GERMANY", "JAPAN",
            "MOROCCO", "SWITZERLAND", "THAILAND", "ARGENTINA", "SINGAPORE"
        ],
        "FOOD": [
            "SPAGHETTI", "CHOCOLATE", "CROISSANT", "PANCAKE", "SUSHI",
            "CHEESECAKE", "HAMBURGER", "AVOCADO", "SANDWICH", "BLUEBERRY"
        ]
    }

# ==============================================================================
# Sound Synthesizer (Generates Retro/Synth SFX procedurally)
# ==============================================================================
class SoundSynthesizer:
    @staticmethod
    def play_sound(freq_start, freq_end, duration_ms, type="sine"):
        try:
            if not pygame.mixer.get_init():
                return
            
            sample_rate = 22050
            num_samples = int(sample_rate * (duration_ms / 1000.0))
            buf = array.array('h', [0] * num_samples)
            
            for i in range(num_samples):
                t = float(i) / sample_rate
                # Linearly interpolate frequency
                frac = float(i) / num_samples
                freq = freq_start + (freq_end - freq_start) * frac
                
                # Apply volume envelope (fade out)
                envelope = 1.0 - frac
                
                if type == "sine":
                    val = math.sin(2.0 * math.pi * freq * t)
                elif type == "square":
                    val = 1.0 if math.sin(2.0 * math.pi * freq * t) >= 0 else -1.0
                else: # noise / sawtooth fallback
                    val = 2.0 * (t * freq - math.floor(0.5 + t * freq))
                    
                buf[i] = int(val * 16384 * envelope)
                
            sound = pygame.mixer.Sound(buffer=buf)
            sound.set_volume(0.2)
            sound.play()
        except Exception:
            pass

    @classmethod
    def play_correct(cls):
        cls.play_sound(440, 880, 150, "sine")

    @classmethod
    def play_incorrect(cls):
        cls.play_sound(300, 150, 200, "sawtooth")

    @classmethod
    def play_win(cls):
        cls.play_sound(523.25, 1046.50, 400, "sine") # C5 to C6

    @classmethod
    def play_lose(cls):
        cls.play_sound(200, 80, 500, "square")

# ==============================================================================
# Particle Effects System
# ==============================================================================
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 2)
        self.color = color
        self.radius = random.randint(3, 6)
        self.alpha = 255
        self.decay = random.uniform(5, 10)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.alpha -= self.decay
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, surface):
        if self.alpha > 0:
            # Render particle with alpha using a temporary surface
            p_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, int(self.alpha))
            pygame.draw.circle(p_surf, color_with_alpha, (self.radius, self.radius), self.radius)
            surface.blit(p_surf, (self.x - self.radius, self.y - self.radius))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.alpha <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# ==============================================================================
# UI Component: Rounded Button with hover animations
# ==============================================================================
class Button:
    def __init__(self, x, y, width, height, text, font, base_color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.scale = 1.0
        self.target_scale = 1.0

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.target_scale = 1.05 if self.is_hovered else 1.0

    def update(self):
        # Smooth interpolation of scale for premium micro-animation feel
        self.scale += (self.target_scale - self.scale) * 0.2

    def draw(self, surface):
        # Calculate scaled dimensions around the center
        center_x, center_y = self.rect.center
        w = int(self.rect.width * self.scale)
        h = int(self.rect.height * self.scale)
        draw_rect = pygame.Rect(center_x - w // 2, center_y - h // 2, w, h)

        color = self.hover_color if self.is_hovered else self.base_color
        
        # Draw soft shadow
        shadow_rect = draw_rect.copy()
        shadow_rect.y += 4
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (10, 10, 15, 80), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=12)
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Draw main button body
        pygame.draw.rect(surface, color, draw_rect, border_radius=12)
        pygame.draw.rect(surface, Config.COLOR_BORDER, draw_rect, width=2, border_radius=12)

        # Render centered text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(center_x, center_y))
        surface.blit(text_surf, text_rect)

# ==============================================================================
# Main Hangman Game Class
# ==============================================================================
class HangmanGame:
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_GAMEOVER = "game_over"

    def __init__(self):
        # Obtain actual display info to set up responsive fullscreen window
        info = pygame.display.Info()
        self.screen_w = info.current_w
        self.screen_h = info.current_h

        self.window = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        self.screen = pygame.Surface((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Hangman: Premium Edition")
        
        self.clock = pygame.time.Clock()
        self.running = True

        # Calculate responsive aspect ratio layout dimensions (Letterboxing)
        self.scale_rect = self.get_scale_rect()

        # System Fonts Fallbacks
        self.font_large = self.load_sys_font(["Trebuchet MS", "Arial", "sans-serif"], 48, bold=True)
        self.font_medium = self.load_sys_font(["Trebuchet MS", "Arial", "sans-serif"], 28, bold=True)
        self.font_normal = self.load_sys_font(["Trebuchet MS", "Arial", "sans-serif"], 20)
        self.font_small = self.load_sys_font(["Trebuchet MS", "Arial", "sans-serif"], 16)

        self.particles = ParticleSystem()
        self.state = self.STATE_MENU
        
        # User statistics
        self.stats = {"wins": 0, "losses": 0, "streak": 0}
        
        # Game State Variables
        self.category = ""
        self.word = ""
        self.guessed_letters = set()
        self.incorrect_guesses = 0
        self.max_attempts = 6
        self.game_result = "" # "win" or "lose"
        
        # UI Elements
        self.menu_buttons = []
        self.playing_buttons = []
        self.gameover_buttons = []
        self.keyboard_keys = {} # key: (Rect, char)
        
        # Animated Hangman Progress Tracker (for drawing parts smoothly)
        self.draw_progress = 0.0
        self.last_incorrect_guesses = 0
        
        # Init components
        self.setup_menu()
        self.setup_keyboard()
        self.setup_playing_controls()
        self.setup_gameover_controls()

    def get_scale_rect(self):
        scale = min(self.screen_w / Config.WIDTH, self.screen_h / Config.HEIGHT)
        new_w = int(Config.WIDTH * scale)
        new_h = int(Config.HEIGHT * scale)
        x = (self.screen_w - new_w) // 2
        y = (self.screen_h - new_h) // 2
        return pygame.Rect(x, y, new_w, new_h)

    def get_virtual_mouse_pos(self, raw_pos):
        x, y = raw_pos
        vx = (x - self.scale_rect.x) * Config.WIDTH / self.scale_rect.width
        vy = (y - self.scale_rect.y) * Config.HEIGHT / self.scale_rect.height
        return int(vx), int(vy)

    def load_sys_font(self, names, size, bold=False):
        for name in names:
            try:
                return pygame.font.SysFont(name, size, bold=bold)
            except Exception:
                continue
        return pygame.font.Font(None, size)

    def setup_menu(self):
        self.menu_buttons = []
        start_y = 260
        # Create Category Selection Buttons
        for i, cat in enumerate(Config.CATEGORIES.keys()):
            btn = Button(
                x=Config.WIDTH // 2 - 150,
                y=start_y + i * 75,
                width=300,
                height=55,
                text=cat,
                font=self.font_medium,
                base_color=Config.COLOR_CARD,
                hover_color=Config.COLOR_ACCENT,
                text_color=Config.COLOR_TEXT_MAIN
            )
            self.menu_buttons.append((btn, cat))
            
        # Add Exit game button at the bottom of Main Menu
        exit_btn = Button(
            x=Config.WIDTH // 2 - 150,
            y=start_y + len(Config.CATEGORIES) * 75,
            width=300,
            height=55,
            text="EXIT GAME",
            font=self.font_medium,
            base_color=Config.COLOR_CARD,
            hover_color=Config.COLOR_INCORRECT,
            text_color=Config.COLOR_TEXT_MAIN
        )
        self.menu_buttons.append((exit_btn, "EXIT"))

    def setup_keyboard(self):
        self.keyboard_keys = {}
        keyboard_origin_x = 480
        keyboard_origin_y = 440
        key_size = 45
        gap = 12
        
        rows = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
        
        for r_idx, row in enumerate(rows):
            # Center alignment per row
            row_width = len(row) * key_size + (len(row) - 1) * gap
            start_x = keyboard_origin_x + (500 - row_width) // 2
            
            for c_idx, char in enumerate(row):
                x = start_x + c_idx * (key_size + gap)
                y = keyboard_origin_y + r_idx * (key_size + gap)
                rect = pygame.Rect(x, y, key_size, key_size)
                self.keyboard_keys[char] = rect

    def setup_playing_controls(self):
        self.playing_buttons = [
            Button(50, Config.HEIGHT - 90, 160, 50, "Main Menu", self.font_normal, Config.COLOR_CARD, Config.COLOR_INCORRECT, Config.COLOR_TEXT_MAIN),
            Button(230, Config.HEIGHT - 90, 160, 50, "Reset Game", self.font_normal, Config.COLOR_CARD, Config.COLOR_ACCENT, Config.COLOR_TEXT_MAIN),
            Button(410, Config.HEIGHT - 90, 160, 50, "Reset Stats", self.font_normal, Config.COLOR_CARD, Config.COLOR_INCORRECT, Config.COLOR_TEXT_MAIN)
        ]

    def setup_gameover_controls(self):
        self.gameover_buttons = [
            Button(Config.WIDTH // 2 - 210, 480, 200, 60, "Play Again", self.font_medium, Config.COLOR_ACCENT, Config.COLOR_ACCENT_HOVER, Config.COLOR_TEXT_MAIN),
            Button(Config.WIDTH // 2 + 10, 480, 200, 60, "Main Menu", self.font_medium, Config.COLOR_CARD, Config.COLOR_INCORRECT, Config.COLOR_TEXT_MAIN)
        ]

    def start_game(self, category):
        self.category = category
        self.word = random.choice(Config.CATEGORIES[category]).upper()
        self.guessed_letters.clear()
        self.incorrect_guesses = 0
        self.last_incorrect_guesses = 0
        self.draw_progress = 0.0
        self.state = self.STATE_PLAYING

    def make_guess(self, letter):
        if self.state != self.STATE_PLAYING or letter in self.guessed_letters:
            return
        
        self.guessed_letters.add(letter)
        
        if letter in self.word:
            SoundSynthesizer.play_correct()
            # Spawn green success particles around the screen or guess letter area
            self.particles.spawn(Config.WIDTH // 2 + 100, 250, Config.COLOR_CORRECT)
            
            # Check Win condition
            if all(char in self.guessed_letters for char in self.word):
                self.game_result = "win"
                self.stats["wins"] += 1
                self.stats["streak"] += 1
                self.state = self.STATE_GAMEOVER
                SoundSynthesizer.play_win()
        else:
            self.incorrect_guesses += 1
            SoundSynthesizer.play_incorrect()
            # Spawn red error particles around the hangman
            self.particles.spawn(220, 300, Config.COLOR_INCORRECT, count=25)
            
            # Check Lose condition
            if self.incorrect_guesses >= self.max_attempts:
                self.game_result = "lose"
                self.stats["losses"] += 1
                self.stats["streak"] = 0
                self.state = self.STATE_GAMEOVER
                SoundSynthesizer.play_lose()

    def update(self):
        # Update particles
        self.particles.update()

        # Get mouse pos and state (transformed into virtual coordinates)
        mouse_pos = self.get_virtual_mouse_pos(pygame.mouse.get_pos())

        # Update button hover states & micro-animations
        if self.state == self.STATE_MENU:
            for btn, _ in self.menu_buttons:
                btn.check_hover(mouse_pos)
                btn.update()
        elif self.state == self.STATE_PLAYING:
            for btn in self.playing_buttons:
                btn.check_hover(mouse_pos)
                btn.update()
        elif self.state == self.STATE_GAMEOVER:
            for btn in self.gameover_buttons:
                btn.check_hover(mouse_pos)
                btn.update()

        # Handle smooth animation drawing rate for Hangman lines
        if self.incorrect_guesses > self.last_incorrect_guesses:
            self.draw_progress += 0.08
            if self.draw_progress >= 1.0:
                self.draw_progress = 0.0
                self.last_incorrect_guesses += 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = self.get_virtual_mouse_pos(event.pos)
                
                if self.state == self.STATE_MENU:
                    for btn, cat in self.menu_buttons:
                        if btn.rect.collidepoint(mouse_pos):
                            if cat == "EXIT":
                                self.running = False
                            else:
                                SoundSynthesizer.play_correct()
                                self.start_game(cat)
                            break
                            
                elif self.state == self.STATE_PLAYING:
                    # On-Screen Keyboard input
                    for char, rect in self.keyboard_keys.items():
                        if rect.collidepoint(mouse_pos) and char not in self.guessed_letters:
                            self.make_guess(char)
                            break
                    
                    # Bottom buttons
                    if self.playing_buttons[0].rect.collidepoint(mouse_pos):
                        self.state = self.STATE_MENU
                        SoundSynthesizer.play_incorrect()
                    elif self.playing_buttons[1].rect.collidepoint(mouse_pos):
                        self.start_game(self.category)
                        SoundSynthesizer.play_correct()
                    elif self.playing_buttons[2].rect.collidepoint(mouse_pos):
                        self.stats = {"wins": 0, "losses": 0, "streak": 0}
                        SoundSynthesizer.play_incorrect()

                elif self.state == self.STATE_GAMEOVER:
                    if self.gameover_buttons[0].rect.collidepoint(mouse_pos):
                        self.start_game(self.category)
                    elif self.gameover_buttons[1].rect.collidepoint(mouse_pos):
                        self.state = self.STATE_MENU

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == self.STATE_MENU:
                        self.running = False
                    else:
                        self.state = self.STATE_MENU
                elif self.state == self.STATE_PLAYING:
                    # Physical Keyboard letter guesses
                    char = event.unicode.upper()
                    if char.isalpha() and len(char) == 1:
                        self.make_guess(char)
                elif self.state == self.STATE_GAMEOVER:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_game(self.category)

    # ==============================================================================
    # Drawing Helpers
    # ==============================================================================
    def draw_menu(self):
        # Title
        title_surf = self.font_large.render("HANGMAN", True, Config.COLOR_ACCENT)
        title_rect = title_surf.get_rect(center=(Config.WIDTH // 2, 110))
        self.screen.blit(title_surf, title_rect)

        sub_surf = self.font_normal.render("SELECT A CATEGORY TO BEGIN PLAYING", True, Config.COLOR_TEXT_MUTED)
        sub_rect = sub_surf.get_rect(center=(Config.WIDTH // 2, 180))
        self.screen.blit(sub_surf, sub_rect)

        # Draw category buttons
        for btn, _ in self.menu_buttons:
            btn.draw(self.screen)

    def draw_playing(self):
        # Draw Panel Cards
        left_panel = pygame.Rect(40, 40, 400, 580)
        right_panel = pygame.Rect(470, 40, 514, 580)
        
        # Left Panel (Hangman Scaffold)
        pygame.draw.rect(self.screen, Config.COLOR_CARD, left_panel, border_radius=16)
        pygame.draw.rect(self.screen, Config.COLOR_BORDER, left_panel, width=2, border_radius=16)

        # Right Panel (Main game state)
        pygame.draw.rect(self.screen, Config.COLOR_CARD, right_panel, border_radius=16)
        pygame.draw.rect(self.screen, Config.COLOR_BORDER, right_panel, width=2, border_radius=16)

        # Category and Stats
        cat_surf = self.font_medium.render(self.category, True, Config.COLOR_ACCENT)
        self.screen.blit(cat_surf, (500, 70))

        streak_text = f"Streak: {self.stats['streak']}"
        streak_surf = self.font_normal.render(streak_text, True, Config.COLOR_TEXT_MUTED)
        self.screen.blit(streak_surf, (860, 75))

        # Hidden Word representation
        word_y = 230
        display_word = [char if char in self.guessed_letters else "_" for char in self.word]
        
        # Dynamic gap spacing depending on word length
        char_width = 32
        gap = 12
        total_word_width = len(display_word) * char_width + (len(display_word) - 1) * gap
        start_word_x = 470 + (514 - total_word_width) // 2

        for idx, char in enumerate(display_word):
            x = start_word_x + idx * (char_width + gap)
            
            # Bottom line indicator
            pygame.draw.line(self.screen, Config.COLOR_BORDER if char == "_" else Config.COLOR_ACCENT, 
                             (x, word_y + 40), (x + char_width, word_y + 40), width=3)
            
            if char != "_":
                letter_surf = self.font_large.render(char, True, Config.COLOR_TEXT_MAIN)
                self.screen.blit(letter_surf, (x + (char_width - letter_surf.get_width()) // 2, word_y - 10))

        # On-Screen Keyboard
        mouse_pos = self.get_virtual_mouse_pos(pygame.mouse.get_pos())
        for char, rect in self.keyboard_keys.items():
            used = char in self.guessed_letters
            hovered = rect.collidepoint(mouse_pos) and not used
            
            # Keyboard coloring and styling
            if used:
                bg_color = Config.COLOR_KEY_USED
                text_color = Config.COLOR_BORDER
            elif hovered:
                bg_color = Config.COLOR_ACCENT
                text_color = Config.COLOR_BG
            else:
                bg_color = Config.COLOR_BG
                text_color = Config.COLOR_TEXT_MAIN
                
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, Config.COLOR_BORDER, rect, width=2, border_radius=8)
            
            char_surf = self.font_normal.render(char, True, text_color)
            self.screen.blit(char_surf, (rect.x + (rect.width - char_surf.get_width()) // 2, 
                                         rect.y + (rect.height - char_surf.get_height()) // 2))

        # Bottom buttons
        for btn in self.playing_buttons:
            btn.draw(self.screen)

        self.draw_hangman_scaffold()

    def draw_hangman_scaffold(self):
        # Center of the left panel is x=240, panel bottom is y=620, top is y=40
        # Draw base
        pygame.draw.line(self.screen, Config.COLOR_TEXT_MUTED, (100, 520), (380, 520), width=5)
        # Vertical post
        pygame.draw.line(self.screen, Config.COLOR_TEXT_MUTED, (180, 520), (180, 160), width=5)
        # Horizontal post
        pygame.draw.line(self.screen, Config.COLOR_TEXT_MUTED, (180, 160), (280, 160), width=5)
        # Diagonal support
        pygame.draw.line(self.screen, Config.COLOR_TEXT_MUTED, (180, 220), (240, 160), width=4)
        # Rope
        pygame.draw.line(self.screen, (200, 170, 110), (280, 160), (280, 210), width=3)

        # Hangman body parts
        steps = self.last_incorrect_guesses
        active_progress = self.draw_progress if steps < self.max_attempts else 0.0

        # Define points
        head_center = (280, 235)
        head_radius = 25
        
        # Draw limbs based on incorrect guesses count
        if steps >= 1: # Head
            pygame.draw.circle(self.screen, Config.COLOR_TEXT_MAIN, head_center, head_radius, width=3)
            
        if steps >= 2: # Torso
            start = (280, 260)
            end = (280, 380)
            self.draw_animated_line(start, end, steps == 2, active_progress, 4)

        if steps >= 3: # Left Arm
            start = (280, 290)
            end = (230, 330)
            self.draw_animated_line(start, end, steps == 3, active_progress, 3)

        if steps >= 4: # Right Arm
            start = (280, 290)
            end = (330, 330)
            self.draw_animated_line(start, end, steps == 4, active_progress, 3)

        if steps >= 5: # Left Leg
            start = (280, 380)
            end = (235, 450)
            self.draw_animated_line(start, end, steps == 5, active_progress, 3)

        if steps >= 6: # Right Leg
            start = (280, 380)
            end = (325, 450)
            self.draw_animated_line(start, end, steps == 6, active_progress, 3)

    def draw_animated_line(self, start, end, is_animating, progress, width):
        if is_animating:
            current_x = start[0] + (end[0] - start[0]) * progress
            current_y = start[1] + (end[1] - start[1]) * progress
            pygame.draw.line(self.screen, Config.COLOR_TEXT_MAIN, start, (int(current_x), int(current_y)), width=width)
        else:
            pygame.draw.line(self.screen, Config.COLOR_TEXT_MAIN, start, end, width=width)

    def draw_gameover(self):
        # Draw overlay dialog card
        overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 200)) # Dark transparent dimming
        self.screen.blit(overlay, (0, 0))

        card_rect = pygame.Rect(Config.WIDTH // 2 - 250, 160, 500, 420)
        pygame.draw.rect(self.screen, Config.COLOR_CARD, card_rect, border_radius=20)
        pygame.draw.rect(self.screen, Config.COLOR_BORDER, card_rect, width=2, border_radius=20)

        # Result title
        if self.game_result == "win":
            title_text = "VICTORY!"
            title_color = Config.COLOR_CORRECT
        else:
            title_text = "GAME OVER"
            title_color = Config.COLOR_INCORRECT

        title_surf = self.font_large.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(center=(Config.WIDTH // 2, 230))
        self.screen.blit(title_surf, title_rect)

        # Word Reveal info
        word_label = self.font_normal.render("THE WORD WAS:", True, Config.COLOR_TEXT_MUTED)
        word_label_rect = word_label.get_rect(center=(Config.WIDTH // 2, 300))
        self.screen.blit(word_label, word_label_rect)

        word_val_surf = self.font_medium.render(self.word, True, Config.COLOR_TEXT_MAIN)
        word_val_rect = word_val_surf.get_rect(center=(Config.WIDTH // 2, 340))
        self.screen.blit(word_val_surf, word_val_rect)

        # Current session statistics inside game over screen
        stats_text = f"Wins: {self.stats['wins']}  |  Losses: {self.stats['losses']}  |  Streak: {self.stats['streak']}"
        stats_surf = self.font_normal.render(stats_text, True, Config.COLOR_TEXT_MUTED)
        stats_rect = stats_surf.get_rect(center=(Config.WIDTH // 2, 400))
        self.screen.blit(stats_surf, stats_rect)

        # Draw overlay controls
        for btn in self.gameover_buttons:
            btn.draw(self.screen)

    def draw(self):
        # We first clear our virtual screen and draw the states
        self.screen.fill(Config.COLOR_BG)

        # Render content based on states
        if self.state == self.STATE_MENU:
            self.draw_menu()
        elif self.state == self.STATE_PLAYING:
            self.draw_playing()
        elif self.state == self.STATE_GAMEOVER:
            self.draw_playing() # Draw playing screen in background
            self.draw_gameover() # Draw overlay on top

        # Draw active particles
        self.particles.draw(self.screen)

        # Clear physical window and scale-blit virtual screen with aspect ratio preservation
        self.window.fill((10, 10, 12))
        scaled_surf = pygame.transform.smoothscale(self.screen, (self.scale_rect.width, self.scale_rect.height))
        self.window.blit(scaled_surf, self.scale_rect.topleft)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(Config.FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = HangmanGame()
    game.run()
