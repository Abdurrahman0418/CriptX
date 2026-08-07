"""
link_window.py
URL / link safety checker UI, backed by the trained RandomForest phishing
detection ML model. Shows an animated verdict card (green = safe,
red = suspicious) with a confidence meter and scan history.
"""
import customtkinter as ctk
from ui import styles
from ui.animations import animate_progress
from ml.url_checker import get_checker
import database as db


class LinkCheckerFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color=styles.BG_DARK, corner_radius=0)
        self.user = user
        self.checker = get_checker()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text="🔗 AI Link / URL Checker", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(header, text="ML Model: Random Forest • Lexical URL Features",
                     font=styles.SMALL_FONT, text_color=styles.TEXT_MUTED).pack(side="right")

        input_card = ctk.CTkFrame(self, fg_color=styles.BG_CARD,
                                   corner_radius=styles.CORNER_RADIUS)
        input_card.pack(fill="x", padx=25, pady=15)

        ctk.CTkLabel(input_card, text="Paste a URL to analyze for phishing indicators:",
                     font=styles.BODY_FONT, text_color=styles.TEXT_SECONDARY
                     ).pack(anchor="w", padx=25, pady=(20, 8))

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=25, pady=(0, 20))

        self.url_entry = ctk.CTkEntry(row, placeholder_text="https://example.com/login",
                                        height=46, corner_radius=10, font=styles.BODY_FONT)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self._check_url())

        ctk.CTkButton(row, text="Scan 🔍", width=120, height=46, corner_radius=10,
                      fg_color=styles.PRIMARY, hover_color=styles.PRIMARY_HOVER,
                      font=styles.BUTTON_FONT, command=self._check_url).pack(side="right")

        self.result_area = ctk.CTkFrame(self, fg_color="transparent")
        self.result_area.pack(fill="x", padx=25, pady=(0, 10))

        self.history_label = ctk.CTkLabel(self, text="🕓 Recent Scans",
                                            font=styles.BODY_FONT,
                                            text_color=styles.TEXT_SECONDARY)
        self.history_label.pack(anchor="w", padx=25, pady=(10, 0))

        self.history_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True, padx=25, pady=(5, 20))

        self._render_history()

    def _check_url(self):
        url = self.url_entry.get().strip()
        if not url:
            return
        result = self.checker.check(url)
        if result is None:
            return
        db.save_url_scan(self.user["id"], url, result["verdict"], result["confidence"])
        self._render_result(result)
        self._render_history()

    def _render_result(self, result):
        for w in self.result_area.winfo_children():
            w.destroy()

        is_bad = result["is_suspicious"]
        color = styles.ACCENT_RED if is_bad else styles.ACCENT_GREEN
        icon = "🚨" if is_bad else "✅"

        card = ctk.CTkFrame(self.result_area, fg_color=styles.BG_CARD,
                             corner_radius=styles.CORNER_RADIUS, border_width=2,
                             border_color=color)
        card.pack(fill="x", pady=5)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 5))
        ctk.CTkLabel(top, text=f"{icon}  {result['verdict']}", font=styles.HEADER_FONT,
                     text_color=color).pack(side="left")

        ctk.CTkLabel(card, text=result["url"], font=styles.SMALL_FONT,
                     text_color=styles.TEXT_MUTED, wraplength=700, justify="left"
                     ).pack(anchor="w", padx=20, pady=(0, 10))

        bar = ctk.CTkProgressBar(card, height=14, corner_radius=8, progress_color=color)
        bar.pack(fill="x", padx=20, pady=(0, 8))
        bar.set(0)
        animate_progress(bar, result["confidence"] / 100)

        ctk.CTkLabel(card, text=f"Model confidence: {result['confidence']}%",
                     font=styles.SMALL_FONT, text_color=styles.TEXT_SECONDARY
                     ).pack(anchor="w", padx=20, pady=(0, 18))

    def _render_history(self):
        for w in self.history_scroll.winfo_children():
            w.destroy()

        rows = db.get_url_scan_history(self.user["id"], limit=15)
        if not rows:
            ctk.CTkLabel(self.history_scroll, text="No scans yet.",
                         font=styles.SMALL_FONT, text_color=styles.TEXT_MUTED).pack(pady=10)
            return

        for row in rows:
            is_bad = "Suspicious" in row["verdict"]
            color = styles.ACCENT_RED if is_bad else styles.ACCENT_GREEN
            item = ctk.CTkFrame(self.history_scroll, fg_color=styles.BG_CARD, corner_radius=10)
            item.pack(fill="x", pady=4)
            ctk.CTkLabel(item, text=("🚨" if is_bad else "✅"), font=("Segoe UI Emoji", 14)
                         ).pack(side="left", padx=(12, 8), pady=8)
            ctk.CTkLabel(item, text=row["url"], font=styles.SMALL_FONT,
                         text_color=styles.TEXT_PRIMARY, anchor="w"
                         ).pack(side="left", fill="x", expand=True, pady=8)
            ctk.CTkLabel(item, text=f"{row['confidence']}%", font=styles.SMALL_FONT,
                         text_color=color).pack(side="right", padx=12)
