"""
styles.py
Centralized color palette, fonts and style constants for the CriptX UI.
Gives the whole app a consistent, colorful, modern cybersecurity look.
"""
import customtkinter as ctk

# ---- Color Palette (Cyber / Neon inspired) ----
BG_DARK = "#0f172a"          # deep navy background
BG_SIDEBAR = "#111827"       # near-black sidebar
BG_CARD = "#1e293b"          # card / panel background
BG_CARD_LIGHT = "#273449"

PRIMARY = "#7c3aed"          # violet accent (brand)
PRIMARY_HOVER = "#6d28d9"
ACCENT_BLUE = "#38bdf8"      # cyan/blue accent
ACCENT_GREEN = "#22c55e"     # success / safe
ACCENT_RED = "#ef4444"       # danger / suspicious
ACCENT_YELLOW = "#facc15"    # warning
ACCENT_PINK = "#ec4899"

TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"

BORDER_COLOR = "#334155"

FONT_FAMILY = "Segoe UI"
FONT_FAMILY_HEADER = "Segoe UI Semibold"

TITLE_FONT = (FONT_FAMILY_HEADER, 26, "bold")
SUBTITLE_FONT = (FONT_FAMILY, 14)
HEADER_FONT = (FONT_FAMILY_HEADER, 20, "bold")
BODY_FONT = (FONT_FAMILY, 13)
SMALL_FONT = (FONT_FAMILY, 11)
BUTTON_FONT = (FONT_FAMILY, 14, "bold")

CORNER_RADIUS = 14

GRADIENT_STOPS = [PRIMARY, ACCENT_BLUE, ACCENT_PINK]


def apply_base_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def gradient_color(step, total, start_hex=PRIMARY, end_hex=ACCENT_BLUE):
    """Linearly interpolate between two hex colors."""
    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % rgb

    r1, g1, b1 = hex_to_rgb(start_hex)
    r2, g2, b2 = hex_to_rgb(end_hex)
    t = step / max(total - 1, 1)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return rgb_to_hex((r, g, b))
