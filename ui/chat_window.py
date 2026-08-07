"""
chat_window.py
The chatbot conversation UI: scrollable message bubbles, animated typing
indicator, code-block rendering with copy buttons, and integration with
the trained ML intent-classification model.
"""
import re
import customtkinter as ctk
from ui import styles
from ui.animations import typewriter
from ml.nlp_engine import get_engine
import database as db

CODE_BLOCK_PATTERN = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)


class ChatFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color=styles.BG_DARK, corner_radius=0)
        self.user = user
        self.engine = get_engine()

        self._build_header()
        self._build_chat_area()
        self._build_input_bar()
        self._load_history()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=25, pady=(20, 5))

        ctk.CTkLabel(header, text="💬 Chat with CriptX", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(side="left")

        ctk.CTkLabel(header, text="ML Intent Classifier • TF-IDF + SVM",
                     font=styles.SMALL_FONT, text_color=styles.TEXT_MUTED).pack(side="right")

    def _build_chat_area(self):
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color=styles.BG_CARD, corner_radius=styles.CORNER_RADIUS)
        self.scroll_frame.pack(fill="both", expand=True, padx=25, pady=10)

        self._add_bot_bubble(
            "👋 Hi! I'm CriptX, your AI cybersecurity assistant. Ask me about phishing, "
            "malware, passwords, VPNs, or anything cybersecurity-related!",
            animate=False
        )

    def _build_input_bar(self):
        input_bar = ctk.CTkFrame(self, fg_color="transparent")
        input_bar.pack(fill="x", padx=25, pady=(0, 20))

        self.entry = ctk.CTkEntry(
            input_bar, placeholder_text="Type your cybersecurity question here...",
            height=46, corner_radius=12, font=styles.BODY_FONT)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self._send_message())

        ctk.CTkButton(
            input_bar, text="Send 🚀", width=110, height=46, corner_radius=12,
            fg_color=styles.PRIMARY, hover_color=styles.PRIMARY_HOVER,
            font=styles.BUTTON_FONT, command=self._send_message
        ).pack(side="right")

    def _load_history(self):
        history = db.get_chat_history(self.user["id"], limit=10)
        for row in history:
            self._add_user_bubble(row["message"])
            self._add_bot_bubble(row["response"], animate=False)

    def _send_message(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._add_user_bubble(text)
        self._show_typing_indicator(text)

    def _show_typing_indicator(self, user_text):
        typing_label = ctk.CTkLabel(
            self.scroll_frame, text="CriptX is typing...", font=styles.SMALL_FONT,
            text_color=styles.TEXT_MUTED, anchor="w")
        typing_label.pack(anchor="w", padx=10, pady=(2, 8))
        self.after(600, lambda: self._respond(user_text, typing_label))

    def _respond(self, user_text, typing_label):
        typing_label.destroy()
        response, intent, confidence = self.engine.get_response(user_text)
        db.save_chat(self.user["id"], user_text, response, intent)
        self._add_bot_bubble(response, animate=True)

    def _add_user_bubble(self, text):
        bubble_wrap = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        bubble_wrap.pack(anchor="e", fill="x", padx=10, pady=6)

        bubble = ctk.CTkLabel(
            bubble_wrap, text=text, font=styles.BODY_FONT, text_color="white",
            fg_color=styles.PRIMARY, corner_radius=14, justify="left",
            wraplength=420, anchor="e", padx=14, pady=10)
        bubble.pack(anchor="e")

    def _add_bot_bubble(self, text, animate=True):
        has_code = bool(CODE_BLOCK_PATTERN.search(text))

        bubble_wrap = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        bubble_wrap.pack(anchor="w", fill="x", padx=10, pady=6)

        header_row = ctk.CTkFrame(bubble_wrap, fg_color="transparent")
        header_row.pack(anchor="w")
        ctk.CTkLabel(header_row, text="🛡️ CriptX", font=("Segoe UI Emoji", 13),
                     text_color=styles.TEXT_MUTED).pack(anchor="w", padx=(0, 6))

        container = ctk.CTkFrame(bubble_wrap, fg_color=styles.BG_CARD_LIGHT,
                                  corner_radius=14)
        container.pack(anchor="w", pady=(2, 0))

        if not has_code:
            bubble = ctk.CTkLabel(
                container, text="" if animate else text, font=styles.BODY_FONT,
                text_color=styles.TEXT_PRIMARY, fg_color="transparent",
                justify="left", wraplength=460, anchor="w", padx=16, pady=12)
            bubble.pack()
            if animate:
                typewriter(bubble, text, delay=10,
                           on_done=lambda: self.after(50, self._scroll_to_bottom))
            self.after(50, self._scroll_to_bottom)
        else:
            self._render_mixed_content(container, text)
            self.after(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self.scroll_frame._parent_canvas.yview_moveto(1.0)

    def _render_mixed_content(self, container, text):
        """Split text into normal prose and ```code``` segments, rendering
        prose as a wrapped label and code as a monospace box with a copy
        button — used for the chatbot's educational code-snippet answers."""
        last_end = 0
        for match in CODE_BLOCK_PATTERN.finditer(text):
            prose = text[last_end:match.start()].strip()
            if prose:
                ctk.CTkLabel(container, text=prose, font=styles.BODY_FONT,
                             text_color=styles.TEXT_PRIMARY, justify="left",
                             wraplength=500, anchor="w"
                             ).pack(fill="x", padx=16, pady=(12, 6))

            code = match.group(1).strip("\n")
            self._render_code_block(container, code)
            last_end = match.end()

        trailing = text[last_end:].strip()
        if trailing:
            ctk.CTkLabel(container, text=trailing, font=styles.BODY_FONT,
                         text_color=styles.TEXT_PRIMARY, justify="left",
                         wraplength=500, anchor="w"
                         ).pack(fill="x", padx=16, pady=(6, 12))

    def _render_code_block(self, container, code):
        code_wrap = ctk.CTkFrame(container, fg_color="#0d1117", corner_radius=10)
        code_wrap.pack(fill="x", padx=14, pady=8)

        top_bar = ctk.CTkFrame(code_wrap, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(top_bar, text="🐍 python", font=("Consolas", 11),
                     text_color=styles.TEXT_MUTED).pack(side="left")

        copy_btn = ctk.CTkButton(top_bar, text="📋 Copy", width=70, height=24,
                                  font=("Segoe UI", 10), fg_color=styles.BG_CARD_LIGHT,
                                  hover_color=styles.PRIMARY,
                                  command=lambda: self._copy_to_clipboard(code, copy_btn))
        copy_btn.pack(side="right")

        n_lines = code.count("\n") + 1
        box_height = min(max(n_lines * 19 + 10, 40), 320)
        code_box = ctk.CTkTextbox(code_wrap, height=box_height, corner_radius=6,
                                   font=("Consolas", 12), fg_color="#0d1117",
                                   text_color="#7ee787", wrap="none")
        code_box.pack(fill="x", padx=10, pady=(4, 10))
        code_box.insert("1.0", code)
        code_box.configure(state="disabled")

    def _copy_to_clipboard(self, code, btn):
        self.clipboard_clear()
        self.clipboard_append(code)
        original_text = btn.cget("text")
        btn.configure(text="✅ Copied")
        self.after(1500, lambda: btn.configure(text=original_text))
