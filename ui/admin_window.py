"""
admin_window.py
Admin dashboard: view usage statistics, manage quiz questions & tips,
and review user feedback.
"""
import customtkinter as ctk
from ui import styles
import database as db


class AdminFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color=styles.BG_DARK, corner_radius=0)
        self.user = user

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text="🛠️ Admin Dashboard", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(side="left")

        self.tabs = ctk.CTkTabview(self, fg_color=styles.BG_CARD,
                                    segmented_button_selected_color=styles.PRIMARY,
                                    segmented_button_selected_hover_color=styles.PRIMARY_HOVER)
        self.tabs.pack(fill="both", expand=True, padx=25, pady=15)

        self.tabs.add("📊 Overview")
        self.tabs.add("🧩 Quiz Questions")
        self.tabs.add("💡 Tips")
        self.tabs.add("📝 Feedback")

        self._build_overview(self.tabs.tab("📊 Overview"))
        self._build_quiz_manager(self.tabs.tab("🧩 Quiz Questions"))
        self._build_tips_manager(self.tabs.tab("💡 Tips"))
        self._build_feedback_viewer(self.tabs.tab("📝 Feedback"))

    # ---------------- OVERVIEW ----------------
    def _build_overview(self, tab):
        stats = db.get_stats()
        cards_info = [
            ("👥 Users", stats["total_users"], styles.ACCENT_BLUE),
            ("💬 Chat Messages", stats["total_chats"], styles.PRIMARY),
            ("🧩 Quiz Attempts", stats["total_quiz_attempts"], styles.ACCENT_GREEN),
            ("🔗 URL Scans", stats["total_url_scans"], styles.ACCENT_PINK),
            ("📝 Feedback Entries", stats["total_feedback"], styles.ACCENT_YELLOW),
        ]

        grid = ctk.CTkFrame(tab, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=20)

        for i, (label, value, color) in enumerate(cards_info):
            card = ctk.CTkFrame(grid, fg_color=styles.BG_CARD_LIGHT,
                                 corner_radius=styles.CORNER_RADIUS,
                                 border_width=2, border_color=color, width=200, height=120)
            card.grid(row=i // 3, column=i % 3, padx=12, pady=12, sticky="nsew")
            grid.grid_columnconfigure(i % 3, weight=1)
            ctk.CTkLabel(card, text=str(value), font=("Segoe UI", 32, "bold"),
                         text_color=color).pack(pady=(20, 0))
            ctk.CTkLabel(card, text=label, font=styles.BODY_FONT,
                         text_color=styles.TEXT_SECONDARY).pack(pady=(0, 15))

    # ---------------- QUIZ MANAGER ----------------
    def _build_quiz_manager(self, tab):
        add_card = ctk.CTkFrame(tab, fg_color=styles.BG_CARD_LIGHT, corner_radius=12)
        add_card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(add_card, text="Add New Quiz Question", font=styles.BODY_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(anchor="w", padx=15, pady=(12, 6))

        self.q_entry = ctk.CTkEntry(add_card, placeholder_text="Question text", height=36)
        self.q_entry.pack(fill="x", padx=15, pady=4)

        opt_row = ctk.CTkFrame(add_card, fg_color="transparent")
        opt_row.pack(fill="x", padx=15, pady=4)
        self.opt_entries = []
        for i in range(4):
            e = ctk.CTkEntry(opt_row, placeholder_text=f"Option {chr(65+i)}", height=36)
            e.grid(row=0, column=i, padx=4, sticky="ew")
            opt_row.grid_columnconfigure(i, weight=1)
            self.opt_entries.append(e)

        bottom_row = ctk.CTkFrame(add_card, fg_color="transparent")
        bottom_row.pack(fill="x", padx=15, pady=(4, 12))
        self.correct_var = ctk.StringVar(value="A")
        ctk.CTkOptionMenu(bottom_row, values=["A", "B", "C", "D"],
                          variable=self.correct_var, width=80).pack(side="left")
        ctk.CTkButton(bottom_row, text="Add Question", fg_color=styles.ACCENT_GREEN,
                      text_color="#0f172a", command=self._add_question).pack(side="right")

        ctk.CTkLabel(tab, text="Existing Questions", font=styles.BODY_FONT,
                     text_color=styles.TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(10, 5))

        self.quiz_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.quiz_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._render_quiz_list()

    def _render_quiz_list(self):
        for w in self.quiz_scroll.winfo_children():
            w.destroy()
        for q in db.get_all_quiz_questions():
            row = ctk.CTkFrame(self.quiz_scroll, fg_color=styles.BG_CARD, corner_radius=8)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=q["question"], font=styles.SMALL_FONT,
                         text_color=styles.TEXT_PRIMARY, anchor="w", wraplength=600
                         ).pack(side="left", fill="x", expand=True, padx=10, pady=8)
            ctk.CTkButton(row, text="Delete", width=70, fg_color=styles.ACCENT_RED,
                          hover_color="#dc2626",
                          command=lambda qid=q["id"]: self._delete_question(qid)
                          ).pack(side="right", padx=10)

    def _add_question(self):
        question = self.q_entry.get().strip()
        options = [e.get().strip() for e in self.opt_entries]
        if not question or not all(options):
            return
        correct_idx = {"A": 0, "B": 1, "C": 2, "D": 3}[self.correct_var.get()]
        db.add_quiz_question(question, options, correct_idx)
        self.q_entry.delete(0, "end")
        for e in self.opt_entries:
            e.delete(0, "end")
        self._render_quiz_list()

    def _delete_question(self, qid):
        db.delete_quiz_question(qid)
        self._render_quiz_list()

    # ---------------- TIPS MANAGER ----------------
    def _build_tips_manager(self, tab):
        add_row = ctk.CTkFrame(tab, fg_color="transparent")
        add_row.pack(fill="x", padx=10, pady=10)
        self.tip_entry = ctk.CTkEntry(add_row, placeholder_text="New security tip...", height=38)
        self.tip_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(add_row, text="Add Tip", fg_color=styles.ACCENT_GREEN,
                      text_color="#0f172a", command=self._add_tip).pack(side="right")

        self.tips_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.tips_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._render_tips_list()

    def _render_tips_list(self):
        for w in self.tips_scroll.winfo_children():
            w.destroy()
        for t in db.get_all_tips():
            row = ctk.CTkFrame(self.tips_scroll, fg_color=styles.BG_CARD, corner_radius=8)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=t["tip_text"], font=styles.SMALL_FONT,
                         text_color=styles.TEXT_PRIMARY, anchor="w", wraplength=600
                         ).pack(side="left", fill="x", expand=True, padx=10, pady=8)
            ctk.CTkButton(row, text="Delete", width=70, fg_color=styles.ACCENT_RED,
                          hover_color="#dc2626",
                          command=lambda tid=t["id"]: self._delete_tip(tid)
                          ).pack(side="right", padx=10)

    def _add_tip(self):
        text = self.tip_entry.get().strip()
        if not text:
            return
        db.add_tip(text)
        self.tip_entry.delete(0, "end")
        self._render_tips_list()

    def _delete_tip(self, tid):
        db.delete_tip(tid)
        self._render_tips_list()

    # ---------------- FEEDBACK VIEWER ----------------
    def _build_feedback_viewer(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        feedback_rows = db.get_all_feedback()
        if not feedback_rows:
            ctk.CTkLabel(scroll, text="No feedback submitted yet.",
                         font=styles.BODY_FONT, text_color=styles.TEXT_MUTED).pack(pady=20)
            return

        for f in feedback_rows:
            card = ctk.CTkFrame(scroll, fg_color=styles.BG_CARD, corner_radius=10)
            card.pack(fill="x", pady=6)
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 0))
            ctk.CTkLabel(top, text=f["full_name"] or "Anonymous", font=styles.BODY_FONT,
                         text_color=styles.TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(top, text="★" * f["rating"] + "☆" * (5 - f["rating"]),
                         font=styles.BODY_FONT, text_color=styles.ACCENT_YELLOW).pack(side="right")
            ctk.CTkLabel(card, text=f["message"], font=styles.SMALL_FONT,
                         text_color=styles.TEXT_SECONDARY, anchor="w", wraplength=650,
                         justify="left").pack(anchor="w", padx=15, pady=(4, 12))
