import tkinter as tk
from tkinter import messagebox, filedialog
import os
import threading
import time

# Suppress Pygame welcome banner
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

try:
    import pygame
except ImportError:
    pygame = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from plyer import notification
except ImportError:
    notification = None


# ─────────────────────────────────────────────────────────────────────────────
# CENTRALISED THEME TOKENS (Linear / Raycast / Apple HIG)
# ─────────────────────────────────────────────────────────────────────────────
DARK = {
    # Canvas & Card surfaces
    "canvas_bg":          "#0F1115",
    "card_bg":            "#181B21",
    "card_border":        "#2A2E37",

    # Elevated / Secondary buttons
    "btn_sec_bg":         "#242832",
    "btn_sec_hover":      "#2E3340",
    "btn_sec_fg":         "#F3F4F6",

    # Typography
    "text_primary":       "#F3F4F6",   # WCAG AAA (13.7:1 on #0F1115)
    "text_secondary":     "#D1D5DB",   # WCAG AAA (9.5:1 on #181B21)
    "text_muted":         "#9CA3AF",   # WCAG AA (5.2:1 on #181B21)

    # Brand & Semantic Accents
    "accent_primary":     "#6366F1",   # Linear Indigo
    "accent_hover":       "#4F46E5",
    "accent_break":       "#10B981",   # Emerald-500
    "accent_break_hover": "#059669",
    "accent_break_badge": "#064E3B",   # Emerald-900 badge background
    "accent_break_fg":    "#34D399",   # Emerald-400 badge text

    # Destructive (Reset / Clear)
    "accent_danger":      "#EF4444",   # Rose-500
    "accent_danger_bg":   "#2A1619",   # Subtle red tint
    "accent_danger_hover":"#3D1B20",
    "accent_danger_border":"#7F1D1D",

    # Progress & Inputs
    "track_bg":           "#2A2E37",
    "input_bg":           "#101216",
    "input_border":       "#2A2E37",
    "pill_focus_bg":      "#1E1B4B",   # Indigo-950 badge background
    "pill_focus_fg":      "#818CF8",   # Indigo-400 badge text

    # Theme Toggle Pill
    "toggle_bg":          "#242832",
    "toggle_hover":       "#2E3340",
    "toggle_fg":          "#F3F4F6",
    "toggle_icon":        "☀",
    "toggle_label":       "Light",

    # Slider Elements
    "slider_thumb_bg":    "#F3F4F6",
    "slider_thumb_stroke":"#6366F1",
    "divider":            "#2A2E37",
}

LIGHT = {
    # Canvas & Card surfaces
    "canvas_bg":          "#F5F7FA",
    "card_bg":            "#FFFFFF",
    "card_border":        "#E5E7EB",

    # Elevated / Secondary buttons
    "btn_sec_bg":         "#F3F4F6",
    "btn_sec_hover":      "#E5E7EB",
    "btn_sec_fg":         "#111827",

    # Typography
    "text_primary":       "#111827",   # WCAG AAA (16.1:1 on #F5F7FA)
    "text_secondary":     "#4B5563",   # WCAG AA (7.2:1 on #FFFFFF)
    "text_muted":         "#6B7280",   # WCAG AA (5.0:1 on #FFFFFF)

    # Brand & Semantic Accents
    "accent_primary":     "#6366F1",   # Linear Indigo
    "accent_hover":       "#4F46E5",
    "accent_break":       "#10B981",   # Emerald-500
    "accent_break_hover": "#059669",
    "accent_break_badge": "#D1FAE5",   # Emerald-100 badge background
    "accent_break_fg":    "#065F46",   # Emerald-800 badge text

    # Destructive (Reset / Clear)
    "accent_danger":      "#EF4444",   # Rose-500
    "accent_danger_bg":   "#FEF2F2",   # Subtle red tint
    "accent_danger_hover":"#FEE2E2",
    "accent_danger_border":"#FECACA",

    # Progress & Inputs
    "track_bg":           "#E5E7EB",
    "input_bg":           "#F9FAFB",
    "input_border":       "#E5E7EB",
    "pill_focus_bg":      "#EEF2FF",   # Indigo-50 badge background
    "pill_focus_fg":      "#4F46E5",   # Indigo-600 badge text

    # Theme Toggle Pill
    "toggle_bg":          "#F3F4F6",
    "toggle_hover":       "#E5E7EB",
    "toggle_fg":          "#111827",
    "toggle_icon":        "☾",
    "toggle_label":       "Dark",

    # Slider Elements
    "slider_thumb_bg":    "#FFFFFF",
    "slider_thumb_stroke":"#6366F1",
    "divider":            "#E5E7EB",
}


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM INTERACTIVE UI COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────
class HoverButton(tk.Button):
    """Button with dynamic theme-aware hover, active, and focus transitions."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.normal_bg = kwargs.get("bg", "#F3F4F6")
        self.hover_bg = kwargs.get("bg", "#E5E7EB")
        self.normal_fg = kwargs.get("fg", "#111827")
        self.hover_fg = kwargs.get("fg", "#111827")
        self.border_color = kwargs.get("highlightbackground", "")

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def set_colors(self, normal_bg, hover_bg, normal_fg=None, hover_fg=None,
                   active_bg=None, active_fg=None, border_color=None):
        self.normal_bg = normal_bg
        self.hover_bg = hover_bg
        if normal_fg is not None:
            self.normal_fg = normal_fg
        if hover_fg is not None:
            self.hover_fg = hover_fg
        self.border_color = border_color

        cfg = {
            "bg": self.normal_bg,
            "fg": self.normal_fg,
            "activebackground": active_bg or hover_bg,
            "activeforeground": active_fg or self.normal_fg,
        }
        if border_color is not None:
            cfg["highlightbackground"] = border_color
            cfg["highlightcolor"] = border_color

        self.config(**cfg)

    def _on_enter(self, e):
        try:
            if self["state"] != "disabled":
                self.config(bg=self.hover_bg, fg=self.hover_fg)
        except Exception:
            pass

    def _on_leave(self, e):
        try:
            if self["state"] != "disabled":
                self.config(bg=self.normal_bg, fg=self.normal_fg)
        except Exception:
            pass


class CanvasVolumeSlider(tk.Canvas):
    """
    Unified modern slider with 6px rounded filled track and circular thumb.
    Eliminates native X11/Tk split-groove rendering glitches on Linux.
    """
    def __init__(self, master, from_=0, to=100, initial=70, command=None, height=22, width=180, **kwargs):
        super().__init__(master, height=height, width=width, highlightthickness=0, bd=0, **kwargs)
        self.min_val = from_
        self.max_val = to
        self.value = initial
        self.command = command

        # Theme colors
        self.track_bg = "#E5E7EB"
        self.fill_color = "#6366F1"
        self.thumb_color = "#FFFFFF"
        self.thumb_stroke = "#6366F1"

        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)

    def set_theme(self, bg, track_bg, fill_color, thumb_color, thumb_stroke):
        self.config(bg=bg)
        self.track_bg = track_bg
        self.fill_color = fill_color
        self.thumb_color = thumb_color
        self.thumb_stroke = thumb_stroke
        self._draw()

    def set(self, val):
        self.value = max(self.min_val, min(self.max_val, float(val)))
        self._draw()

    def get(self):
        return self.value

    def _get_coords(self):
        w = max(self.winfo_width(), 160)
        h = max(self.winfo_height(), 22)
        padding = 10
        usable_w = w - (2 * padding)
        y = h // 2
        fraction = (self.value - self.min_val) / max(1.0, (self.max_val - self.min_val))
        thumb_x = padding + int(usable_w * fraction)
        return padding, padding + usable_w, y, thumb_x

    def _draw(self):
        self.delete("all")
        x_start, x_end, y, thumb_x = self._get_coords()

        # Background rounded 6px track
        self.create_line(x_start, y, x_end, y, fill=self.track_bg, width=6, capstyle="round")

        # Active filled track
        if thumb_x > x_start:
            self.create_line(x_start, y, thumb_x, y, fill=self.fill_color, width=6, capstyle="round")

        # Circular thumb (radius 7px, 2px accent stroke)
        r = 7
        self.create_oval(thumb_x - r, y - r, thumb_x + r, y + r,
                         fill=self.thumb_color, outline=self.thumb_stroke, width=2)

    def _update_from_x(self, x):
        x_start, x_end, y, _ = self._get_coords()
        usable_w = x_end - x_start
        if usable_w > 0:
            fraction = max(0.0, min(1.0, (x - x_start) / usable_w))
            self.value = self.min_val + fraction * (self.max_val - self.min_val)
            self._draw()
            if self.command:
                self.command(self.value)

    def _on_click(self, event):
        self._update_from_x(event.x)

    def _on_drag(self, event):
        self._update_from_x(event.x)


def truncate_filename(name, max_len=24):
    """Truncates long audio file names with an ellipsis to prevent header collisions."""
    if not name or name == "None (Silent)":
        return "No track"
    if len(name) <= max_len:
        return name
    return name[:max_len - 3] + "..."


def center_window(root, width=520, height=730):
    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    x = max(0, (sw - width) // 2)
    y = max(0, (sh - height) // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.minsize(460, 680)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN POMODORO APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro")

        # ── Theme State ────────────────────────────────────────────
        self._dark_mode = False          # starts in Light mode
        self.T = LIGHT                   # active palette alias

        self.root.config(bg=self.T["canvas_bg"])
        center_window(self.root, width=520, height=730)

        # ── Core Timer State ───────────────────────────────────────
        self.checkmark = 0
        self.total_work_time = 0
        self.total_break_time = 0
        self.pomodoro_count = 0
        self.running = False
        self.paused = False
        self.remaining_time = 0
        self.end_time = 0.0
        self.after_id = None
        self.timer_mode = "work"
        self.task = ""
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60

        # ── Audio State ────────────────────────────────────────────
        self.music_playing = False
        self.music_paused = False
        self.music_volume = 0.7

        self.audio_available = False
        if pygame:
            try:
                pygame.mixer.init()
                pygame.mixer.music.set_volume(self.music_volume)
                self.audio_available = True
            except Exception as e:
                print(f"Audio init failed: {e}")

        self.tts_available = False
        self.engine = None
        self.tts_lock = threading.Lock()
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.tts_available = True
            except Exception as e:
                print(f"TTS init failed: {e}")

        # ── Typography & Monospace Numeral Selection ────────────────
        base_font = "Helvetica"
        mono_font = "Courier"
        try:
            import tkinter.font as tkfont
            available = set(tkfont.families(self.root))
            for f in ("Inter", "Geist", "Segoe UI", "SF Pro Display",
                      "Ubuntu", "DejaVu Sans", "Helvetica Neue", "Arial"):
                if f in available:
                    base_font = f
                    break
            for m in ("SF Mono", "JetBrains Mono", "Fira Code", "DejaVu Sans Mono",
                      "Ubuntu Mono", "Consolas", "Courier New", "Courier"):
                if m in available:
                    mono_font = m
                    break
        except Exception:
            pass

        # Tabular monospace font for zero jitter during countdown ticking
        self.font_display = (mono_font, 48, "bold")
        self.font_title   = (base_font, 14, "bold")
        self.font_h1      = (base_font, 13, "bold")
        self.font_body    = (base_font, 11)
        self.font_small   = (base_font, 10)
        self.font_badge   = (base_font, 9, "bold")
        self.font_mono    = (mono_font, 10)

        # ── Music Discovery ────────────────────────────────────────
        self.music_file = None
        self.bundled_music = []
        music_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
        if os.path.isdir(music_dir):
            for fname in sorted(os.listdir(music_dir)):
                if fname.lower().endswith((".mp3", ".wav")):
                    self.bundled_music.append(os.path.join(music_dir, fname))
        if self.bundled_music:
            self.music_file = self.bundled_music[0]

        # ── Build UI Hierarchy ─────────────────────────────────────
        self._build_ui()

        # ── Keyboard Shortcuts ─────────────────────────────────────
        self.root.bind("<space>", lambda e: self.toggle_timer_shortcut())
        self.root.bind("<Escape>", lambda e: self.pause_timer())

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ─────────────────────────────────────────────────────────────────────────
    # UI CONSTRUCTION (8px Grid & Linear Aesthetic)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        T = self.T

        # ── Top Chrome Header (Title + Swapped Moon/Sun Toggle) ──────
        self.chrome = tk.Frame(self.root, bg=T["canvas_bg"], height=48)
        self.chrome.pack(fill=tk.X, padx=24, pady=(16, 8))

        self.app_title = tk.Label(
            self.chrome,
            text="Pomodoro",
            font=self.font_title,
            bg=T["canvas_bg"],
            fg=T["text_primary"]   # High contrast header
        )
        self.app_title.pack(side=tk.LEFT)

        # Theme toggle pill: Displays Moon icon in Light mode (switch to Dark)
        # Displays Sun icon in Dark mode (switch to Light)
        self.theme_btn = HoverButton(
            self.chrome,
            text=f"{T['toggle_icon']}  {T['toggle_label']}",
            command=self.toggle_theme,
            font=self.font_small,
            bg=T["toggle_bg"],
            fg=T["toggle_fg"],
            activebackground=T["toggle_hover"],
            activeforeground=T["toggle_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["card_border"],
            cursor="hand2",
            padx=14,
            pady=5
        )
        self.theme_btn.set_colors(
            normal_bg=T["toggle_bg"],
            hover_bg=T["toggle_hover"],
            normal_fg=T["toggle_fg"],
            border_color=T["card_border"]
        )
        self.theme_btn.pack(side=tk.RIGHT)

        # ── Main Content Container ──────────────────────────────────
        self.container = tk.Frame(self.root, bg=T["canvas_bg"])
        self.container.pack(fill=tk.BOTH, expand=True, padx=24, pady=8)

        # ════════════════════════════════════════════════════════════
        # CARD 1 — HERO TIMER CARD (12px Card Gap, 16px Padding)
        # ════════════════════════════════════════════════════════════
        self.hero_card = tk.Frame(
            self.container,
            bg=T["card_bg"],
            highlightthickness=1,
            highlightbackground=T["card_border"],
            bd=0
        )
        self.hero_card.pack(fill=tk.X, pady=(0, 12))

        hero = tk.Frame(self.hero_card, bg=T["card_bg"])
        hero.pack(fill=tk.X, padx=16, pady=20)

        # Mode Badge Pill (e.g. FOCUS SESSION)
        self.mode_badge = tk.Label(
            hero,
            text="FOCUS SESSION",
            font=self.font_badge,
            bg=T["pill_focus_bg"],
            fg=T["pill_focus_fg"],
            padx=12,
            pady=4
        )
        self.mode_badge.pack(anchor="center", pady=(0, 12))

        # Current Task Display Header
        self.current_task_label = tk.Label(
            hero,
            text="What are you working on?",
            font=self.font_h1,
            bg=T["card_bg"],
            fg=T["text_secondary"],
            wraplength=440
        )
        self.current_task_label.pack(anchor="center", pady=(0, 12))

        # Task Input Row (8px gap)
        self.task_input_frame = tk.Frame(hero, bg=T["card_bg"])
        self.task_input_frame.pack(fill=tk.X, pady=(0, 16))

        self.task_entry = tk.Entry(
            self.task_input_frame,
            font=self.font_body,
            bg=T["input_bg"],
            fg=T["text_primary"],
            insertbackground=T["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=T["input_border"],
            highlightcolor=T["accent_primary"]
        )
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7, padx=(0, 8))
        self.task_entry.bind("<Return>", lambda e: self.on_task_return())

        self.set_task_button = HoverButton(
            self.task_input_frame,
            text="Set",
            command=self.set_task,
            font=self.font_small,
            bg=T["btn_sec_bg"],
            fg=T["btn_sec_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["card_border"],
            cursor="hand2",
            padx=14,
            pady=5
        )
        self.set_task_button.set_colors(
            normal_bg=T["btn_sec_bg"],
            hover_bg=T["btn_sec_hover"],
            normal_fg=T["btn_sec_fg"],
            border_color=T["card_border"]
        )
        self.set_task_button.pack(side=tk.RIGHT)

        # Tabular Monospace Countdown Display (Zero Digit Jitter)
        self.timer_label = tk.Label(
            hero,
            text="25:00",
            font=self.font_display,
            bg=T["card_bg"],
            fg=T["text_primary"]
        )
        self.timer_label.pack(anchor="center", pady=(0, 12))

        # Sleek Rounded 6px Progress Bar
        self.progress_canvas = tk.Canvas(
            hero,
            height=6,
            bg=T["card_bg"],
            highlightthickness=0,
            bd=0
        )
        self.progress_canvas.pack(fill=tk.X, pady=(0, 20))
        self.progress_canvas.bind("<Configure>", lambda e: self.update_progress_bar(self._get_current_progress_fraction()))

        # Hero Action Buttons (Primary Accent + Elevated Secondary + Subtle Destructive)
        self.btn_frame = tk.Frame(hero, bg=T["card_bg"])
        self.btn_frame.pack(fill=tk.X)

        self.start_button = HoverButton(
            self.btn_frame,
            text="Start Focus",
            command=self.start_timer,
            font=self.font_h1,
            bg=T["accent_primary"],
            fg="#FFFFFF",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=20,
            pady=9
        )
        self.start_button.set_colors(
            normal_bg=T["accent_primary"],
            hover_bg=T["accent_hover"],
            normal_fg="#FFFFFF",
            active_bg=T["accent_hover"],
            active_fg="#FFFFFF"
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.pause_button = HoverButton(
            self.btn_frame,
            text="Pause",
            command=self.pause_timer,
            font=self.font_body,
            bg=T["btn_sec_bg"],
            fg=T["btn_sec_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["card_border"],
            cursor="hand2",
            padx=16,
            pady=9
        )
        self.pause_button.set_colors(
            normal_bg=T["btn_sec_bg"],
            hover_bg=T["btn_sec_hover"],
            normal_fg=T["btn_sec_fg"],
            border_color=T["card_border"]
        )
        self.pause_button.pack(side=tk.LEFT, padx=(0, 8))

        self.reset_button = HoverButton(
            self.btn_frame,
            text="Reset",
            command=self.reset_timer,
            font=self.font_body,
            bg=T["accent_danger_bg"],
            fg=T["accent_danger"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["accent_danger_border"],
            cursor="hand2",
            padx=16,
            pady=9
        )
        self.reset_button.set_colors(
            normal_bg=T["accent_danger_bg"],
            hover_bg=T["accent_danger_hover"],
            normal_fg=T["accent_danger"],
            border_color=T["accent_danger_border"]
        )
        self.reset_button.pack(side=tk.RIGHT)

        # ════════════════════════════════════════════════════════════
        # CARD 2 — BREAK AUDIO STATION
        # ════════════════════════════════════════════════════════════
        self.audio_card = tk.Frame(
            self.container,
            bg=T["card_bg"],
            highlightthickness=1,
            highlightbackground=T["card_border"],
            bd=0
        )
        self.audio_card.pack(fill=tk.X, pady=(0, 12))

        audio = tk.Frame(self.audio_card, bg=T["card_bg"])
        audio.pack(fill=tk.X, padx=16, pady=16)

        # Header Row (with Ellipsis Truncation to Prevent Collisions)
        audio_hdr = tk.Frame(audio, bg=T["card_bg"])
        audio_hdr.pack(fill=tk.X, pady=(0, 10))

        self.break_audio_title = tk.Label(
            audio_hdr,
            text="BREAK AUDIO",
            font=self.font_badge,
            bg=T["card_bg"],
            fg=T["text_muted"]
        )
        self.break_audio_title.pack(side=tk.LEFT)

        raw_track = os.path.basename(self.music_file) if self.music_file else "No track"
        self.music_label = tk.Label(
            audio_hdr,
            text=truncate_filename(raw_track),
            font=self.font_small,
            bg=T["card_bg"],
            fg=T["text_secondary"]
        )
        self.music_label.pack(side=tk.RIGHT)

        # Audio Transport Buttons (Elevated Secondary Styling)
        self.audio_ctrl_row = tk.Frame(audio, bg=T["card_bg"])
        self.audio_ctrl_row.pack(fill=tk.X, pady=(0, 12))

        self.music_button = HoverButton(
            self.audio_ctrl_row,
            text="Select",
            command=self.load_music,
            font=self.font_small,
            bg=T["btn_sec_bg"],
            fg=T["btn_sec_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["card_border"],
            cursor="hand2",
            padx=12,
            pady=5
        )
        self.music_button.set_colors(T["btn_sec_bg"], T["btn_sec_hover"], T["btn_sec_fg"], border_color=T["card_border"])
        self.music_button.pack(side=tk.LEFT, padx=(0, 8))

        self.play_music_button = HoverButton(
            self.audio_ctrl_row,
            text="▶",
            command=self.play_music_manual,
            font=self.font_small,
            bg=T["btn_sec_bg"],
            fg=T["accent_primary"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["card_border"],
            cursor="hand2",
            padx=12,
            pady=5
        )
        self.play_music_button.set_colors(T["btn_sec_bg"], T["btn_sec_hover"], T["accent_primary"], border_color=T["card_border"])
        self.play_music_button.pack(side=tk.LEFT, padx=(0, 8))

        self.pause_music_button = HoverButton(
            self.audio_ctrl_row,
            text="⏸",
            command=self.pause_music_manual,
            font=self.font_small,
            bg=T["btn_sec_bg"],
            fg=T["btn_sec_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["card_border"],
            cursor="hand2",
            padx=12,
            pady=5
        )
        self.pause_music_button.set_colors(T["btn_sec_bg"], T["btn_sec_hover"], T["btn_sec_fg"], border_color=T["card_border"])
        self.pause_music_button.pack(side=tk.LEFT, padx=(0, 8))

        self.clear_music_button = HoverButton(
            self.audio_ctrl_row,
            text="✕",
            command=self.clear_music,
            font=self.font_small,
            bg=T["accent_danger_bg"],
            fg=T["accent_danger"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["accent_danger_border"],
            cursor="hand2",
            padx=12,
            pady=5
        )
        self.clear_music_button.set_colors(T["accent_danger_bg"], T["accent_danger_hover"], T["accent_danger"], border_color=T["accent_danger_border"])
        self.clear_music_button.pack(side=tk.RIGHT)

        # Unified Custom Canvas Volume Slider
        self.volume_row = tk.Frame(audio, bg=T["card_bg"])
        self.volume_row.pack(fill=tk.X)

        self.volume_label = tk.Label(
            self.volume_row,
            text="Vol: 70%",
            font=self.font_small,
            bg=T["card_bg"],
            fg=T["text_secondary"]
        )
        self.volume_label.pack(side=tk.LEFT, padx=(0, 10))

        self.volume_slider = CanvasVolumeSlider(
            self.volume_row,
            from_=0,
            to=100,
            initial=70,
            command=self.on_volume_change,
            height=22,
            width=200,
            bg=T["card_bg"]
        )
        self.volume_slider.set_theme(
            bg=T["card_bg"],
            track_bg=T["track_bg"],
            fill_color=T["accent_primary"],
            thumb_color=T["slider_thumb_bg"],
            thumb_stroke=T["slider_thumb_stroke"]
        )
        self.volume_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # ════════════════════════════════════════════════════════════
        # CARD 3 — INTERVALS & LIFETIME ANALYTICS
        # ════════════════════════════════════════════════════════════
        self.settings_card = tk.Frame(
            self.container,
            bg=T["card_bg"],
            highlightthickness=1,
            highlightbackground=T["card_border"],
            bd=0
        )
        self.settings_card.pack(fill=tk.X)

        cfg = tk.Frame(self.settings_card, bg=T["card_bg"])
        cfg.pack(fill=tk.X, padx=16, pady=16)

        # Durations Input Row (Inherited Dynamic Card Background)
        dur_row = tk.Frame(cfg, bg=T["card_bg"])
        dur_row.pack(fill=tk.X, pady=(0, 10))

        self.work_label = tk.Label(
            dur_row,
            text="Work (min):",
            font=self.font_small,
            bg=T["card_bg"],
            fg=T["text_secondary"]
        )
        self.work_label.pack(side=tk.LEFT, padx=(0, 6))

        self.work_time_entry = tk.Entry(
            dur_row,
            width=4,
            font=self.font_mono,
            bg=T["input_bg"],
            fg=T["text_primary"],
            insertbackground=T["text_primary"],
            justify="center",
            relief="flat",
            highlightthickness=1,
            highlightbackground=T["input_border"]
        )
        self.work_time_entry.insert(0, "25")
        self.work_time_entry.pack(side=tk.LEFT, padx=(0, 16), ipady=4)

        self.break_label = tk.Label(
            dur_row,
            text="Break (min):",
            font=self.font_small,
            bg=T["card_bg"],
            fg=T["text_secondary"]
        )
        self.break_label.pack(side=tk.LEFT, padx=(0, 6))

        self.break_time_entry = tk.Entry(
            dur_row,
            width=4,
            font=self.font_mono,
            bg=T["input_bg"],
            fg=T["text_primary"],
            insertbackground=T["text_primary"],
            justify="center",
            relief="flat",
            highlightthickness=1,
            highlightbackground=T["input_border"]
        )
        self.break_time_entry.insert(0, "5")
        self.break_time_entry.pack(side=tk.LEFT, padx=(0, 8), ipady=4)

        # Subtle 1px Divider
        self.divider = tk.Frame(cfg, bg=T["divider"], height=1)
        self.divider.pack(fill=tk.X, pady=(4, 10))

        # Analytics Row (High Contrast)
        stats_row = tk.Frame(cfg, bg=T["card_bg"])
        stats_row.pack(fill=tk.X)

        self.stats_label = tk.Label(
            stats_row,
            text="0 sessions  •  0m focus  •  0m break",
            font=self.font_small,
            bg=T["card_bg"],
            fg=T["text_primary"]   # High-contrast readable stats
        )
        self.stats_label.pack(side=tk.LEFT)

        self.reset_stats_button = HoverButton(
            stats_row,
            text="Reset stats",
            command=self.reset_stats,
            font=self.font_badge,
            bg=T["btn_sec_bg"],
            fg=T["btn_sec_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=T["card_border"],
            cursor="hand2",
            padx=10,
            pady=4
        )
        self.reset_stats_button.set_colors(
            normal_bg=T["btn_sec_bg"],
            hover_bg=T["btn_sec_hover"],
            normal_fg=T["btn_sec_fg"],
            border_color=T["card_border"]
        )
        self.reset_stats_button.pack(side=tk.RIGHT)

    # ─────────────────────────────────────────────────────────────────────────
    # THEME ENGINE & SEAMLESS REPAINT
    # ─────────────────────────────────────────────────────────────────────────
    def toggle_theme(self):
        """Swaps theme cleanly between Dark and Light mode."""
        self._dark_mode = not self._dark_mode
        self.T = DARK if self._dark_mode else LIGHT
        self.apply_theme()

    def apply_theme(self):
        """Repaints all widgets dynamically to eliminate unthemed elements and contrast flaws."""
        T = self.T

        # Window Canvas & Chrome
        self.root.config(bg=T["canvas_bg"])
        self.chrome.config(bg=T["canvas_bg"])
        self.container.config(bg=T["canvas_bg"])

        # Header Title & Moon/Sun Toggle Pill
        self.app_title.config(bg=T["canvas_bg"], fg=T["text_primary"])
        self.theme_btn.config(text=f"{T['toggle_icon']}  {T['toggle_label']}")
        self.theme_btn.set_colors(
            normal_bg=T["toggle_bg"],
            hover_bg=T["toggle_hover"],
            normal_fg=T["toggle_fg"],
            border_color=T["card_border"]
        )

        # ── Hero Card ───────────────────────────────────────────────
        self._repaint_card(self.hero_card, T)
        self.task_input_frame.config(bg=T["card_bg"])
        self.btn_frame.config(bg=T["card_bg"])

        # Mode Badge Pill (Focus vs Break vs Idle)
        if self.timer_mode == "break":
            self.mode_badge.config(bg=T["accent_break_badge"], fg=T["accent_break_fg"], text="BREAK TIME")
            self.timer_label.config(bg=T["card_bg"], fg=T["accent_break"])
        elif self.running:
            self.mode_badge.config(bg=T["pill_focus_bg"], fg=T["pill_focus_fg"], text="FOCUS SESSION")
            self.timer_label.config(bg=T["card_bg"], fg=T["text_primary"])
        else:
            self.mode_badge.config(bg=T["canvas_bg"], fg=T["text_muted"], text="READY")
            self.timer_label.config(bg=T["card_bg"], fg=T["text_primary"])

        self.current_task_label.config(
            bg=T["card_bg"],
            fg=T["text_primary"] if self.task else T["text_secondary"]
        )

        self.task_entry.config(
            bg=T["input_bg"],
            fg=T["text_primary"],
            insertbackground=T["text_primary"],
            highlightbackground=T["input_border"],
            highlightcolor=T["accent_primary"]
        )
        self.set_task_button.set_colors(T["btn_sec_bg"], T["btn_sec_hover"], T["btn_sec_fg"], border_color=T["card_border"])

        # Progress bar redraw with theme accent
        self.progress_canvas.config(bg=T["card_bg"])
        self.update_progress_bar(self._get_current_progress_fraction())

        # Action Buttons
        self.start_button.set_colors(
            normal_bg=T["accent_primary"],
            hover_bg=T["accent_hover"],
            normal_fg="#FFFFFF",
            active_bg=T["accent_hover"],
            active_fg="#FFFFFF"
        )
        self.pause_button.set_colors(
            normal_bg=T["btn_sec_bg"],
            hover_bg=T["btn_sec_hover"],
            normal_fg=T["btn_sec_fg"],
            border_color=T["card_border"]
        )
        self.reset_button.set_colors(
            normal_bg=T["accent_danger_bg"],
            hover_bg=T["accent_danger_hover"],
            normal_fg=T["accent_danger"],
            border_color=T["accent_danger_border"]
        )

        # ── Audio Station Card ──────────────────────────────────────
        self._repaint_card(self.audio_card, T)
        self.audio_ctrl_row.config(bg=T["card_bg"])
        self.volume_row.config(bg=T["card_bg"])

        self.break_audio_title.config(bg=T["card_bg"], fg=T["text_muted"])
        self.music_label.config(bg=T["card_bg"], fg=T["text_secondary"])
        self.volume_label.config(bg=T["card_bg"], fg=T["text_secondary"])

        self.music_button.set_colors(T["btn_sec_bg"], T["btn_sec_hover"], T["btn_sec_fg"], border_color=T["card_border"])
        self.play_music_button.set_colors(T["btn_sec_bg"], T["btn_sec_hover"], T["accent_primary"], border_color=T["card_border"])
        self.pause_music_button.set_colors(T["btn_sec_bg"], T["btn_sec_hover"], T["btn_sec_fg"], border_color=T["card_border"])
        self.clear_music_button.set_colors(T["accent_danger_bg"], T["accent_danger_hover"], T["accent_danger"], border_color=T["accent_danger_border"])

        self.volume_slider.set_theme(
            bg=T["card_bg"],
            track_bg=T["track_bg"],
            fill_color=T["accent_primary"],
            thumb_color=T["slider_thumb_bg"],
            thumb_stroke=T["slider_thumb_stroke"]
        )

        # ── Settings & Analytics Card ───────────────────────────────
        self._repaint_card(self.settings_card, T)
        self.work_label.config(bg=T["card_bg"], fg=T["text_secondary"])
        self.break_label.config(bg=T["card_bg"], fg=T["text_secondary"])
        self.divider.config(bg=T["divider"])

        for entry in (self.work_time_entry, self.break_time_entry):
            entry.config(
                bg=T["input_bg"],
                fg=T["text_primary"],
                insertbackground=T["text_primary"],
                highlightbackground=T["input_border"]
            )

        self.stats_label.config(bg=T["card_bg"], fg=T["text_primary"])
        self.reset_stats_button.set_colors(
            normal_bg=T["btn_sec_bg"],
            hover_bg=T["btn_sec_hover"],
            normal_fg=T["btn_sec_fg"],
            border_color=T["card_border"]
        )

    def _repaint_card(self, card_frame, T):
        """Recursively updates frame background and 1px border highlight."""
        card_frame.config(bg=T["card_bg"], highlightbackground=T["card_border"])
        for child in card_frame.winfo_children():
            try:
                child.config(bg=T["card_bg"])
            except Exception:
                pass
            if isinstance(child, tk.Frame):
                for sub in child.winfo_children():
                    try:
                        sub.config(bg=T["card_bg"])
                    except Exception:
                        pass

    # ─────────────────────────────────────────────────────────────────────────
    # PROGRESS BAR & TIMER LOGIC
    # ─────────────────────────────────────────────────────────────────────────
    def _get_current_progress_fraction(self):
        total = self.break_duration if self.timer_mode == "break" else self.work_duration
        if total <= 0:
            return 0.0
        elapsed = max(0, total - self.remaining_time)
        return min(1.0, elapsed / total)

    def update_progress_bar(self, fraction):
        """Draws a sleek 6px rounded progress track with primary accent fill."""
        try:
            w = max(self.progress_canvas.winfo_width(), 400)
            h = 6
            y = h // 2
            self.progress_canvas.delete("all")

            # Background 6px rounded track
            self.progress_canvas.create_line(4, y, w - 4, y, fill=self.T["track_bg"], width=6, capstyle="round")

            # Active filled 6px track
            usable_w = w - 8
            filled_x = 4 + int(usable_w * max(0.0, min(1.0, fraction)))
            if filled_x > 4:
                fill_color = self.T["accent_break"] if self.timer_mode == "break" else self.T["accent_primary"]
                self.progress_canvas.create_line(4, y, filled_x, y, fill=fill_color, width=6, capstyle="round")
        except Exception:
            pass

    def toggle_timer_shortcut(self):
        """Handles Spacebar toggle for instant start/pause."""
        if self.running:
            self.pause_timer()
        else:
            self.start_timer()

    def on_task_return(self):
        """Handles Enter key in task input."""
        self.set_task()
        if not self.running:
            self.start_timer()

    def cancel_timer(self):
        """Cancels any pending after() scheduled callback."""
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def tick(self):
        """Precision wall-clock tick driven by time.time() without timer drift."""
        if not self.running:
            return

        remaining = int(round(self.end_time - time.time()))
        remaining = max(0, remaining)
        self.remaining_time = remaining

        mins, secs = divmod(remaining, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

        total = self.break_duration if self.timer_mode == "break" else self.work_duration
        elapsed = max(0, total - remaining)
        fraction = min(1.0, elapsed / max(1, total))
        self.update_progress_bar(fraction)

        if remaining <= 0:
            self.cancel_timer()
            if self.timer_mode == "work":
                self.complete_task()
            else:
                self.end_break()
        else:
            self.after_id = self.root.after(200, self.tick)

    def speak_async(self, text):
        """Speaks announcement asynchronously in a thread-safe worker."""
        if not self.tts_available or not self.engine:
            return

        def _speak():
            with self.tts_lock:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"TTS error: {e}")

        threading.Thread(target=_speak, daemon=True).start()

    def send_notification(self, title, message):
        """Desktop system notification safe on Linux."""
        if not notification:
            return
        try:
            notification.notify(title=title, message=message, timeout=5)
        except Exception as e:
            print(f"Notification error: {e}")

    def set_task(self):
        task_input = self.task_entry.get().strip()
        if not task_input:
            messagebox.showwarning("Warning", "Task name cannot be empty.")
            return
        self.task = task_input
        self.task_entry.config(state="disabled")
        self.set_task_button.config(state="disabled")
        self.current_task_label.config(text=self.task, fg=self.T["text_primary"])

    def start_timer(self):
        T = self.T
        if not self.running and not self.paused:
            task_input = self.task_entry.get().strip()
            if task_input:
                self.task = task_input
                self.task_entry.config(state="disabled")
                self.set_task_button.config(state="disabled")
                self.current_task_label.config(text=self.task, fg=T["text_primary"])
            elif not self.task:
                messagebox.showwarning("Warning", "Please set a task before starting the timer.")
                return
            else:
                self.current_task_label.config(text=self.task, fg=T["text_primary"])
                self.task_entry.config(state="disabled")
                self.set_task_button.config(state="disabled")

            try:
                self.work_duration  = int(self.work_time_entry.get().strip()) * 60
                self.break_duration = int(self.break_time_entry.get().strip()) * 60
                if self.work_duration <= 0 or self.break_duration <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter positive integers for work and break durations.")
                return

            self.running = True
            self.timer_mode = "work"
            self.root.title("Pomodoro — Focus")
            self.mode_badge.config(
                text="FOCUS SESSION",
                bg=T["pill_focus_bg"],
                fg=T["pill_focus_fg"]
            )
            self.timer_label.config(fg=T["text_primary"])
            self.start_button.config(text="Focusing…")
            self.remaining_time = self.work_duration
            self.end_time = time.time() + self.remaining_time
            self.cancel_timer()
            self.tick()

        elif self.paused:
            self.running = True
            self.paused = False
            self.end_time = time.time() + self.remaining_time
            if self.timer_mode == "break":
                if self.music_playing and not self.music_paused:
                    self.unpause_music()
                self.start_button.config(text="Break active")
            else:
                self.start_button.config(text="Focusing…")
            self.cancel_timer()
            self.tick()

    def pause_timer(self):
        if self.running:
            self.cancel_timer()
            self.remaining_time = max(0, int(round(self.end_time - time.time())))
            self.running = False
            self.paused = True
            self.start_button.config(text="Resume")
            if self.timer_mode == "break" and self.music_playing and not self.music_paused:
                self.pause_music()

    def reset_timer(self):
        self.cancel_timer()
        self.running = False
        self.paused = False
        self.timer_mode = "work"
        try:
            work_mins = int(self.work_time_entry.get().strip())
            self.work_duration = work_mins * 60
        except ValueError:
            work_mins = 25
            self.work_duration = 25 * 60

        T = self.T
        self.remaining_time = self.work_duration
        self.root.title("Pomodoro")
        self.mode_badge.config(text="READY", bg=T["canvas_bg"], fg=T["text_muted"])
        self.timer_label.config(text=f"{work_mins:02d}:00", fg=T["text_primary"])
        self.start_button.config(text="Start Focus")
        self.task = ""
        self.task_entry.config(state="normal")
        self.task_entry.delete(0, tk.END)
        self.set_task_button.config(state="normal")
        self.current_task_label.config(text="What are you working on?", fg=T["text_secondary"])
        self.update_progress_bar(0.0)
        self.stop_music()

    def reset_stats(self):
        self.update_stats(reset=True)

    def countdown(self, count):
        self.running = True
        self.paused = False
        self.timer_mode = "work"
        self.remaining_time = count
        self.end_time = time.time() + count
        self.cancel_timer()
        self.tick()

    def countdown_break(self, count):
        self.running = True
        self.paused = False
        self.timer_mode = "break"
        self.remaining_time = count
        self.end_time = time.time() + count
        self.cancel_timer()
        self.tick()

    def complete_task(self):
        self.checkmark += 1
        self.total_work_time += max(1, self.work_duration // 60)
        self.pomodoro_count += 1

        self.speak_async(f"Task {self.task} completed. Take a break.")
        self.send_notification("Pomodoro", "Session done — time for a break!")
        self.update_stats()
        self.task_entry.config(state="normal")
        self.set_task_button.config(state="normal")
        self.start_break()

    def start_break(self):
        T = self.T
        self.timer_mode = "break"
        self.root.title("Pomodoro — Break")
        self.mode_badge.config(
            text="BREAK TIME",
            bg=T["accent_break_badge"],
            fg=T["accent_break_fg"]
        )
        self.timer_label.config(fg=T["accent_break"])
        self.current_task_label.config(
            text=f"Rest up  ·  Finished: {self.task}" if self.task else "Rest up",
            fg=T["text_secondary"]
        )
        self.start_button.config(text="Break active")

        try:
            val = int(self.break_time_entry.get().strip())
            if val > 0:
                self.break_duration = val * 60
        except ValueError:
            pass

        if self.music_file and self.audio_available and pygame:
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops=-1)
                self.music_playing = True
                self.music_paused = False
            except Exception as e:
                print(f"Music play error: {e}")

        self.countdown_break(self.break_duration)

    def end_break(self):
        self.stop_music()
        self.total_break_time += max(1, self.break_duration // 60)

        self.speak_async("Break over. Time to focus.")
        self.send_notification("Pomodoro", "Break over — back to work!")
        self.update_stats()
        self.running = False
        self.timer_mode = "work"
        self.start_timer()

    # ─────────────────────────────────────────────────────────────────────────
    # AUDIO CONTROLS
    # ─────────────────────────────────────────────────────────────────────────
    def load_music(self):
        music_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
        initial_dir = music_dir if os.path.isdir(music_dir) else os.getcwd()
        selected = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Audio Files", "*.mp3 *.wav")]
        )
        if selected:
            self.music_file = selected
            self.music_label.config(text=truncate_filename(os.path.basename(selected)))
            if (self.timer_mode == "break" and self.running
                    and not self.paused and self.audio_available and pygame):
                try:
                    pygame.mixer.music.load(self.music_file)
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(loops=-1)
                    self.music_playing = True
                    self.music_paused = False
                except Exception as e:
                    print(f"Music play error: {e}")

    def clear_music(self):
        self.music_file = None
        self.stop_music()
        self.music_label.config(text="No track")

    def stop_music(self):
        self.music_playing = False
        self.music_paused = False
        if self.audio_available and pygame:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def pause_music(self):
        if self.audio_available and pygame:
            try:
                pygame.mixer.music.pause()
            except Exception:
                pass

    def unpause_music(self):
        if self.audio_available and pygame:
            try:
                pygame.mixer.music.unpause()
            except Exception:
                pass

    def on_volume_change(self, val):
        pct = int(val)
        self.music_volume = pct / 100.0
        self.volume_label.config(text=f"Vol: {pct}%")
        if self.audio_available and pygame:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    def play_music_manual(self):
        if not self.audio_available or not pygame or not self.music_file:
            return
        try:
            if self.music_paused:
                pygame.mixer.music.unpause()
                self.music_paused = False
                self.music_playing = True
            else:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops=-1)
                self.music_playing = True
                self.music_paused = False
        except Exception as e:
            print(f"Music play error: {e}")

    def pause_music_manual(self):
        if not self.audio_available or not pygame:
            return
        if self.music_playing and not self.music_paused:
            try:
                pygame.mixer.music.pause()
                self.music_paused = True
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    # STATS TRACKING
    # ─────────────────────────────────────────────────────────────────────────
    def update_stats(self, work_time=None, break_time=None,
                     pomodoros=None, completed=0, reset=False):
        if reset:
            self.total_work_time = 0
            self.total_break_time = 0
            self.pomodoro_count = 0
            self.checkmark = 0
        else:
            if work_time  is not None: self.total_work_time  = work_time
            if break_time is not None: self.total_break_time = break_time
            if pomodoros  is not None: self.pomodoro_count   = pomodoros

        self.stats_label.config(
            text=(f"{self.pomodoro_count} sessions  "
                  f"•  {self.total_work_time}m focus  "
                  f"•  {self.total_break_time}m break")
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WINDOW CLOSE
    # ─────────────────────────────────────────────────────────────────────────
    def on_close(self):
        self.running = False
        self.cancel_timer()
        self.stop_music()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
