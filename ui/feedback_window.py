"""
feedback_window.py
Feedback submission UI with an animated 5-star rating selector.
"""
import customtkinter as ctk
from ui import styles
import database as db


class FeedbackFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color=styles.BG_DARK, corner_radius=0)
        self.user = user
        self.rating = 0
        self.star_buttons = []

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text="📝 Share Your Feedback", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(side="left")

        card = ctk.CTkFrame(self, fg_color=styles.BG_CARD, corner_radius=styles.CORNER_RADIUS)
        card.pack(fill="both", expand=True, padx=25, pady=15)

        ctk.CTkLabel(card, text="How was your experience with CriptX?",
                     font=styles.SUBTITLE_FONT, text_color=styles.TEXT_SECONDARY
                     ).pack(pady=(30, 10))

        star_row = ctk.CTkFrame(card, fg_color="transparent")
        star_row.pack(pady=10)
        for i in range(1, 6):
            btn = ctk.CTkButton(star_row, text="☆", width=50, height=50,
                                 font=("Segoe UI Emoji", 26), fg_color="transparent",
                                 hover_color=styles.BG_CARD_LIGHT, text_color=styles.TEXT_MUTED,
                                 command=lambda i=i: self._set_rating(i))
            btn.grid(row=0, column=i - 1, padx=4)
            self.star_buttons.append(btn)

        self.rating_label = ctk.CTkLabel(card, text="", font=styles.BODY_FONT,
                                          text_color=styles.ACCENT_YELLOW)
        self.rating_label.pack(pady=(4, 15))

        self.textbox = ctk.CTkTextbox(card, height=140, corner_radius=10,
                                       fg_color=styles.BG_CARD_LIGHT, font=styles.BODY_FONT)
        self.textbox.pack(fill="x", padx=40, pady=(0, 10))
        self.textbox.insert("1.0", "")

        self.msg_label = ctk.CTkLabel(card, text="", font=styles.SMALL_FONT)
        self.msg_label.pack(pady=(0, 5))

        ctk.CTkButton(card, text="Submit Feedback 💌", width=220, height=46, corner_radius=10,
                      fg_color=styles.PRIMARY, hover_color=styles.PRIMARY_HOVER,
                      font=styles.BUTTON_FONT, command=self._submit).pack(pady=(5, 30))

    def _set_rating(self, value):
        self.rating = value
        labels = {0: "", 1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent"}
        for i, btn in enumerate(self.star_buttons, start=1):
            btn.configure(text="★" if i <= value else "☆",
                          text_color=styles.ACCENT_YELLOW if i <= value else styles.TEXT_MUTED)
        self.rating_label.configure(text=f"{'★' * value}  {labels[value]}".strip() if value else "")

    def _submit(self):
        message = self.textbox.get("1.0", "end").strip()
        if self.rating == 0 or not message:
            self.msg_label.configure(text="Please provide a rating and feedback message.",
                                      text_color=styles.ACCENT_RED)
            return
        db.save_feedback(self.user["id"], message, self.rating)
        self.msg_label.configure(text="✅ Thank you! Your feedback has been recorded.",
                                  text_color=styles.ACCENT_GREEN)
        self.textbox.delete("1.0", "end")
        self._set_rating(0)
