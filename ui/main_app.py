"""
main_app.py
The main dashboard window shown after login: a colorful animated sidebar
with navigation icons, a top user-info bar, and a dynamic content area
that swaps between Chat / Quiz / Tips / Link Checker / Feedback / Admin.
"""
import customtkinter as ctk
from ui import styles
from ui.chat_window import ChatFrame
from ui.quiz_window import QuizFrame
from ui.tips_window import TipsFrame
from ui.link_window import LinkCheckerFrame
from ui.feedback_window import FeedbackFrame
from ui.admin_window import AdminFrame
from ui.threatfeed_window import ThreatFeedFrame


class MainApp(ctk.CTk):
    def __init__(self, user, on_logout):
        super().__init__()
        self.user = user
        self.on_logout = on_logout

        self.title(f"CriptX - Cybersecurity Awareness Chatbot | {user['full_name']}")
        self.geometry("1200x720")
        self.minsize(1050, 650)
        self.configure(fg_color=styles.BG_DARK)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}
        self.current_frame = None

        self._build_sidebar()
        self._build_content_area()

        self.show_page("Chat")

    # ---------------- SIDEBAR ----------------
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=styles.BG_SIDEBAR, width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(25, 10), padx=20)
        ctk.CTkLabel(logo_frame, text="🛡️ CriptX", font=("Segoe UI", 22, "bold"),
                     text_color=styles.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(logo_frame, text="Cyber Awareness Assistant", font=styles.SMALL_FONT,
                     text_color=styles.TEXT_MUTED).pack(anchor="w")

        user_card = ctk.CTkFrame(self.sidebar, fg_color=styles.BG_CARD, corner_radius=12)
        user_card.pack(fill="x", padx=15, pady=15)
        initials = "".join([p[0].upper() for p in self.user["full_name"].split()[:2]])
        ctk.CTkLabel(user_card, text=initials, width=40, height=40, corner_radius=20,
                     fg_color=styles.PRIMARY, text_color="white",
                     font=("Segoe UI", 14, "bold")).pack(side="left", padx=10, pady=10)
        info_col = ctk.CTkFrame(user_card, fg_color="transparent")
        info_col.pack(side="left", pady=10)
        ctk.CTkLabel(info_col, text=self.user["full_name"], font=styles.SMALL_FONT,
                     text_color=styles.TEXT_PRIMARY, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info_col, text=self.user["role"].capitalize(), font=("Segoe UI", 10),
                     text_color=styles.ACCENT_GREEN, anchor="w").pack(anchor="w")

        nav_items = [
            ("Chat", "💬", "Chat Assistant"),
            ("Quiz", "🧩", "Quiz"),
            ("Tips", "💡", "Security Tips"),
            ("LinkChecker", "🔗", "Link Checker"),
            ("ThreatFeed", "🌐", "Live Threat Feed"),
            ("Feedback", "📝", "Feedback"),
        ]
        if self.user.get("role") == "admin":
            nav_items.append(("Admin", "🛠️", "Admin Panel"))

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=12, pady=10)

        for key, icon, label in nav_items:
            btn = ctk.CTkButton(
                nav_frame, text=f"  {icon}  {label}", anchor="w", height=44,
                corner_radius=10, fg_color="transparent", hover_color=styles.BG_CARD_LIGHT,
                font=styles.BODY_FONT, text_color=styles.TEXT_SECONDARY,
                command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", pady=4)
            self.nav_buttons[key] = btn

        ctk.CTkButton(self.sidebar, text="🚪 Logout", height=42, corner_radius=10,
                      fg_color=styles.ACCENT_RED, hover_color="#dc2626",
                      font=styles.BUTTON_FONT, command=self._logout
                      ).pack(side="bottom", fill="x", padx=15, pady=20)

    def _highlight_nav(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color=styles.PRIMARY, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=styles.TEXT_SECONDARY)

    # ---------------- CONTENT AREA ----------------
    def _build_content_area(self):
        self.content_area = ctk.CTkFrame(self, fg_color=styles.BG_DARK, corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

    def show_page(self, key):
        self._highlight_nav(key)
        if self.current_frame is not None:
            self.current_frame.destroy()

        page_map = {
            "Chat": ChatFrame,
            "Quiz": QuizFrame,
            "Tips": TipsFrame,
            "LinkChecker": LinkCheckerFrame,
            "ThreatFeed": ThreatFeedFrame,
            "Feedback": FeedbackFrame,
            "Admin": AdminFrame,
        }
        frame_cls = page_map.get(key, ChatFrame)
        self.current_frame = frame_cls(self.content_area, self.user)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _logout(self):
        self.destroy()
        self.on_logout()
