"""
tips_window.py
Displays cybersecurity awareness tips as colorful animated cards, either
a random tip on demand or the full scrollable list.
"""
import random
import customtkinter as ctk
from ui import styles
import database as db

TIP_ICONS = ["🔐", "📧", "🛡️", "🌐", "💾", "⚠️", "📱", "🔑", "🕵️", "🧯"]
CARD_COLORS = [styles.PRIMARY, styles.ACCENT_BLUE, styles.ACCENT_PINK,
               styles.ACCENT_GREEN, styles.ACCENT_YELLOW]


class TipsFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color=styles.BG_DARK, corner_radius=0)
        self.user = user

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text="💡 Security Tips", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(header, text="🎲 Random Tip", width=150, height=38, corner_radius=10,
                      fg_color=styles.ACCENT_BLUE, hover_color="#0ea5e9",
                      text_color="#0f172a", font=styles.BUTTON_FONT,
                      command=self._show_random_tip).pack(side="right")

        self.spotlight = ctk.CTkFrame(self, fg_color=styles.BG_CARD,
                                       corner_radius=styles.CORNER_RADIUS, height=90)
        self.spotlight.pack(fill="x", padx=25, pady=(10, 15))
        self.spotlight_label = ctk.CTkLabel(
            self.spotlight, text="👉 Click 'Random Tip' for a spotlight tip of the moment!",
            font=styles.BODY_FONT, text_color=styles.TEXT_SECONDARY, wraplength=800)
        self.spotlight_label.pack(pady=25, padx=20)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        self._render_all_tips()

    def _render_all_tips(self):
        tips = db.get_all_tips()
        cols = 2
        for i, tip in enumerate(tips):
            row, col = divmod(i, cols)
            color = CARD_COLORS[i % len(CARD_COLORS)]
            icon = TIP_ICONS[i % len(TIP_ICONS)]

            card = ctk.CTkFrame(self.scroll, fg_color=styles.BG_CARD,
                                 corner_radius=styles.CORNER_RADIUS, border_width=2,
                                 border_color=color)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.scroll.grid_columnconfigure(col, weight=1)

            ctk.CTkLabel(card, text=icon, font=("Segoe UI Emoji", 26)).pack(
                anchor="w", padx=15, pady=(12, 0))
            ctk.CTkLabel(card, text=tip["tip_text"], font=styles.BODY_FONT,
                         text_color=styles.TEXT_PRIMARY, wraplength=340,
                         justify="left").pack(anchor="w", padx=15, pady=(4, 14))

    def _show_random_tip(self):
        tips = db.get_all_tips()
        if not tips:
            return
        tip = random.choice(tips)
        icon = random.choice(TIP_ICONS)
        color = random.choice(CARD_COLORS)
        self.spotlight.configure(border_width=2, border_color=color)
        self.spotlight_label.configure(text=f"{icon}  {tip['tip_text']}")
