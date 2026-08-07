"""
login_window.py
Animated Login / Register screen for CriptX with a soft glowing gradient
side panel, tab switching between Login and Register, and inline
validation messages.
"""
import customtkinter as ctk
from ui import styles
import database as db


class LoginWindow(ctk.CTkToplevel if False else ctk.CTk):
    """Standalone window shown before the main dashboard loads."""

    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("CriptX - Cybersecurity Awareness Chatbot | Login")
        self.geometry("980x600")
        self.minsize(900, 560)
        self.configure(fg_color=styles.BG_DARK)

        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

        self._glow_step = 0
        self._animate_glow()

    # ---------------- LEFT BRAND PANEL ----------------
    def _build_left_panel(self):
        self.left_panel = ctk.CTkFrame(self, fg_color=styles.PRIMARY, corner_radius=0)
        self.left_panel.grid(row=0, column=0, sticky="nsew")

        wrapper = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        logo = ctk.CTkLabel(wrapper, text="🛡️", font=("Segoe UI Emoji", 64),
                             text_color="white")
        logo.pack(pady=(0, 10))

        title = ctk.CTkLabel(wrapper, text="CriptX", font=("Segoe UI", 40, "bold"),
                              text_color="white")
        title.pack()

        subtitle = ctk.CTkLabel(
            wrapper,
            text="AI-Powered Cybersecurity\nAwareness Chatbot",
            font=styles.SUBTITLE_FONT,
            text_color="#ede9fe",
            justify="center",
        )
        subtitle.pack(pady=(8, 20))

        features = [
            "💬  Ask cybersecurity questions",
            "🧠  ML-powered smart chatbot",
            "🔗  AI phishing link detector",
            "🧩  Interactive security quizzes",
            "💡  Daily safety tips",
        ]
        for feat in features:
            ctk.CTkLabel(wrapper, text=feat, font=styles.BODY_FONT,
                         text_color="white", anchor="w").pack(anchor="w", pady=3)

    def _animate_glow(self):
        # gently pulses the left panel color between two brand hues
        colors = [styles.PRIMARY, "#8b5cf6", styles.PRIMARY, "#6d28d9"]
        color = colors[self._glow_step % len(colors)]
        try:
            self.left_panel.configure(fg_color=color)
        except Exception:
            return
        self._glow_step += 1
        self.after(900, self._animate_glow)

    # ---------------- RIGHT FORM PANEL ----------------
    def _build_right_panel(self):
        self.right_panel = ctk.CTkFrame(self, fg_color=styles.BG_DARK, corner_radius=0)
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        self.form_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.form_container.place(relx=0.5, rely=0.5, anchor="center")

        # Tabs
        self.tab_frame = ctk.CTkFrame(self.form_container, fg_color=styles.BG_CARD,
                                       corner_radius=20)
        self.tab_frame.pack(pady=(0, 25))

        self.login_tab_btn = ctk.CTkButton(
            self.tab_frame, text="Login", width=140, corner_radius=18,
            fg_color=styles.PRIMARY, hover_color=styles.PRIMARY_HOVER,
            font=styles.BUTTON_FONT, command=self.show_login)
        self.login_tab_btn.grid(row=0, column=0, padx=4, pady=4)

        self.register_tab_btn = ctk.CTkButton(
            self.tab_frame, text="Register", width=140, corner_radius=18,
            fg_color="transparent", hover_color=styles.BG_CARD_LIGHT,
            font=styles.BUTTON_FONT, command=self.show_register)
        self.register_tab_btn.grid(row=0, column=1, padx=4, pady=4)

        self.card = ctk.CTkFrame(self.form_container, fg_color=styles.BG_CARD,
                                  corner_radius=styles.CORNER_RADIUS, width=380)
        self.card.pack(fill="both", expand=True)

        self.login_frame = None
        self.register_frame = None
        self.show_login()

    def _clear_card(self):
        for widget in self.card.winfo_children():
            widget.destroy()

    def show_login(self):
        self.login_tab_btn.configure(fg_color=styles.PRIMARY)
        self.register_tab_btn.configure(fg_color="transparent")
        self._clear_card()

        ctk.CTkLabel(self.card, text="Welcome Back 👋", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(pady=(30, 5), padx=30)
        ctk.CTkLabel(self.card, text="Login to continue learning cybersecurity",
                     font=styles.SMALL_FONT, text_color=styles.TEXT_SECONDARY).pack(pady=(0, 20))

        self.login_email = ctk.CTkEntry(self.card, placeholder_text="Email",
                                          width=300, height=42, corner_radius=10)
        self.login_email.pack(pady=8, padx=30)

        self.login_password = ctk.CTkEntry(self.card, placeholder_text="Password",
                                             show="•", width=300, height=42, corner_radius=10)
        self.login_password.pack(pady=8, padx=30)

        self.login_msg = ctk.CTkLabel(self.card, text="", font=styles.SMALL_FONT,
                                       text_color=styles.ACCENT_RED)
        self.login_msg.pack(pady=(4, 0))

        ctk.CTkButton(self.card, text="Login", width=300, height=44, corner_radius=10,
                      fg_color=styles.ACCENT_BLUE, hover_color="#0ea5e9",
                      font=styles.BUTTON_FONT, text_color="#0f172a",
                      command=self._handle_login).pack(pady=(16, 6), padx=30)

        self.bind("<Return>", lambda e: self._handle_login())

    def show_register(self):
        self.register_tab_btn.configure(fg_color=styles.PRIMARY)
        self.login_tab_btn.configure(fg_color="transparent")
        self._clear_card()

        ctk.CTkLabel(self.card, text="Create Account ✨", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(pady=(30, 5), padx=30)
        ctk.CTkLabel(self.card, text="Join CriptX and boost your cyber awareness",
                     font=styles.SMALL_FONT, text_color=styles.TEXT_SECONDARY).pack(pady=(0, 20))

        self.reg_name = ctk.CTkEntry(self.card, placeholder_text="Full Name",
                                       width=300, height=42, corner_radius=10)
        self.reg_name.pack(pady=6, padx=30)

        self.reg_email = ctk.CTkEntry(self.card, placeholder_text="Email",
                                        width=300, height=42, corner_radius=10)
        self.reg_email.pack(pady=6, padx=30)

        self.reg_password = ctk.CTkEntry(self.card, placeholder_text="Password",
                                           show="•", width=300, height=42, corner_radius=10)
        self.reg_password.pack(pady=6, padx=30)

        self.reg_confirm = ctk.CTkEntry(self.card, placeholder_text="Confirm Password",
                                          show="•", width=300, height=42, corner_radius=10)
        self.reg_confirm.pack(pady=6, padx=30)

        self.reg_msg = ctk.CTkLabel(self.card, text="", font=styles.SMALL_FONT,
                                     text_color=styles.ACCENT_RED)
        self.reg_msg.pack(pady=(4, 0))

        ctk.CTkButton(self.card, text="Register", width=300, height=44, corner_radius=10,
                      fg_color=styles.ACCENT_GREEN, hover_color="#16a34a",
                      font=styles.BUTTON_FONT, text_color="#0f172a",
                      command=self._handle_register).pack(pady=(14, 20), padx=30)

        self.bind("<Return>", lambda e: self._handle_register())

    def _handle_login(self):
        email = self.login_email.get().strip()
        password = self.login_password.get()
        if not email or not password:
            self.login_msg.configure(text="Please fill in all fields.")
            return
        success, msg, user = db.login_user(email, password)
        if success:
            self.destroy()
            self.on_success(user)
        else:
            self.login_msg.configure(text=msg)

    def _handle_register(self):
        name = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        pwd = self.reg_password.get()
        confirm = self.reg_confirm.get()

        if not all([name, email, pwd, confirm]):
            self.reg_msg.configure(text="Please fill in all fields.")
            return
        if len(pwd) < 6:
            self.reg_msg.configure(text="Password must be at least 6 characters.")
            return
        if pwd != confirm:
            self.reg_msg.configure(text="Passwords do not match.")
            return

        success, msg = db.register_user(name, email, pwd)
        if success:
            self.reg_msg.configure(text_color=styles.ACCENT_GREEN, text=msg + " Please login.")
            self.after(1200, self.show_login)
        else:
            self.reg_msg.configure(text_color=styles.ACCENT_RED, text=msg)
