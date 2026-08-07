"""
quiz_window.py
Interactive cybersecurity quiz with animated progress bar, instant
feedback per question, and a confetti celebration on completion.
"""
import random
import customtkinter as ctk
from ui import styles
from ui.animations import ConfettiCanvas, animate_progress
import database as db


class QuizFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color=styles.BG_DARK, corner_radius=0)
        self.user = user
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.selected_var = None

        self._build_header()
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=25, pady=10)

        self._show_start_screen()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text="🧩 Cybersecurity Quiz", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(side="left")

    def _clear_content(self):
        for w in self.content_area.winfo_children():
            w.destroy()

    def _show_start_screen(self):
        self._clear_content()
        card = ctk.CTkFrame(self.content_area, fg_color=styles.BG_CARD,
                             corner_radius=styles.CORNER_RADIUS)
        card.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(card, text="🎯", font=("Segoe UI Emoji", 48)).pack(pady=(30, 10))
        ctk.CTkLabel(card, text="Test Your Cybersecurity Knowledge",
                     font=styles.HEADER_FONT, text_color=styles.TEXT_PRIMARY).pack(padx=40)
        ctk.CTkLabel(card, text="Answer questions about phishing, malware, passwords & more.",
                     font=styles.BODY_FONT, text_color=styles.TEXT_SECONDARY).pack(pady=(6, 20), padx=40)

        ctk.CTkButton(card, text="Start Quiz ▶", width=220, height=46, corner_radius=12,
                      fg_color=styles.ACCENT_GREEN, hover_color="#16a34a",
                      font=styles.BUTTON_FONT, text_color="#0f172a",
                      command=self._start_quiz).pack(pady=(0, 30))

        history = db.get_quiz_scores(self.user["id"])
        if history:
            best = max(h["score"] / h["total"] for h in history) * 100
            ctk.CTkLabel(self.content_area,
                         text=f"📊 Your best score so far: {best:.0f}%  |  Attempts: {len(history)}",
                         font=styles.SMALL_FONT, text_color=styles.TEXT_MUTED
                         ).place(relx=0.5, rely=0.85, anchor="center")

    def _start_quiz(self):
        all_q = db.get_all_quiz_questions()
        random.shuffle(all_q)
        self.questions = all_q[:10] if len(all_q) > 10 else all_q
        self.current_index = 0
        self.score = 0
        self._show_question()

    def _show_question(self):
        self._clear_content()
        if self.current_index >= len(self.questions):
            self._show_results()
            return

        q = self.questions[self.current_index]

        top_row = ctk.CTkFrame(self.content_area, fg_color="transparent")
        top_row.pack(fill="x", pady=(10, 20))

        ctk.CTkLabel(top_row, text=f"Question {self.current_index + 1} of {len(self.questions)}",
                     font=styles.BODY_FONT, text_color=styles.TEXT_SECONDARY).pack(side="left")

        self.progress = ctk.CTkProgressBar(self.content_area, height=14, corner_radius=8,
                                            progress_color=styles.ACCENT_BLUE)
        self.progress.pack(fill="x", pady=(0, 25))
        self.progress.set(self.current_index / len(self.questions))
        animate_progress(self.progress, (self.current_index + 1) / len(self.questions))

        card = ctk.CTkFrame(self.content_area, fg_color=styles.BG_CARD,
                             corner_radius=styles.CORNER_RADIUS)
        card.pack(fill="both", expand=True)

        ctk.CTkLabel(card, text=q["question"], font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY, wraplength=650, justify="left"
                     ).pack(pady=(30, 20), padx=40, anchor="w")

        self.selected_var = ctk.StringVar(value="")
        options = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
        colors = [styles.ACCENT_BLUE, styles.PRIMARY, styles.ACCENT_PINK, styles.ACCENT_YELLOW]

        self.option_buttons = []
        for i, opt in enumerate(options):
            btn = ctk.CTkButton(
                card, text=f"{chr(65 + i)}.  {opt}", anchor="w", height=48,
                corner_radius=10, fg_color=styles.BG_CARD_LIGHT,
                hover_color=colors[i], font=styles.BODY_FONT,
                command=lambda idx=i: self._select_option(idx, q["correct_index"], colors))
            btn.pack(fill="x", padx=40, pady=6)
            self.option_buttons.append(btn)

        self.feedback_label = ctk.CTkLabel(card, text="", font=styles.BODY_FONT)
        self.feedback_label.pack(pady=(10, 20))

    def _select_option(self, chosen_idx, correct_idx, colors):
        for i, btn in enumerate(self.option_buttons):
            btn.configure(state="disabled")
            if i == correct_idx:
                btn.configure(fg_color=styles.ACCENT_GREEN)
            elif i == chosen_idx:
                btn.configure(fg_color=styles.ACCENT_RED)

        if chosen_idx == correct_idx:
            self.score += 1
            self.feedback_label.configure(text="✅ Correct! Great job.",
                                           text_color=styles.ACCENT_GREEN)
        else:
            self.feedback_label.configure(text="❌ Not quite — check the highlighted answer.",
                                           text_color=styles.ACCENT_RED)

        self.after(1100, self._next_question)

    def _next_question(self):
        self.current_index += 1
        self._show_question()

    def _show_results(self):
        self._clear_content()
        db.save_quiz_score(self.user["id"], self.score, len(self.questions))
        percentage = (self.score / len(self.questions)) * 100 if self.questions else 0

        wrap = ctk.CTkFrame(self.content_area, fg_color="transparent")
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        canvas = ConfettiCanvas(wrap, width=500, height=100, bg=styles.BG_DARK)
        canvas.pack()
        if percentage >= 50:
            canvas.burst(50)

        emoji = "🏆" if percentage >= 80 else ("👍" if percentage >= 50 else "📘")
        ctk.CTkLabel(wrap, text=emoji, font=("Segoe UI Emoji", 56)).pack(pady=(10, 5))
        ctk.CTkLabel(wrap, text=f"You scored {self.score} / {len(self.questions)}",
                     font=styles.HEADER_FONT, text_color=styles.TEXT_PRIMARY).pack()
        ctk.CTkLabel(wrap, text=f"{percentage:.0f}% Accuracy",
                     font=styles.SUBTITLE_FONT, text_color=styles.ACCENT_BLUE).pack(pady=(4, 20))

        btn_row = ctk.CTkFrame(wrap, fg_color="transparent")
        btn_row.pack()
        ctk.CTkButton(btn_row, text="Retake Quiz 🔁", width=180, height=42, corner_radius=10,
                      fg_color=styles.PRIMARY, hover_color=styles.PRIMARY_HOVER,
                      font=styles.BUTTON_FONT, command=self._start_quiz).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Back to Menu", width=160, height=42, corner_radius=10,
                      fg_color=styles.BG_CARD_LIGHT, hover_color=styles.BORDER_COLOR,
                      font=styles.BUTTON_FONT, command=self._show_start_screen
                      ).pack(side="left", padx=6)
