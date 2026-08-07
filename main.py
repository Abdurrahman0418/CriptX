"""
main.py
Entry point for CriptX - AI-Powered Cybersecurity Awareness Chatbot.

Run this file to launch the application:
    python main.py

On first run it will:
  1. Initialize the SQLite database (with seeded quiz questions & tips)
  2. Train the ML intent-classification chatbot model (if not already trained)
  3. Train the ML phishing URL-detection model (if not already trained)
  4. Show an animated splash screen
  5. Launch the Login window, then the main Dashboard
"""
import os
import sys
import customtkinter as ctk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import styles
import database as db


def ensure_models_trained():
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    intent_model = os.path.join(model_dir, "intent_model.pkl")
    url_model = os.path.join(model_dir, "url_model.pkl")

    if not os.path.exists(intent_model):
        from ml.train_intent_model import train_and_save as train_intent
        train_intent()

    if not os.path.exists(url_model):
        from ml.train_url_model import train_and_save as train_url
        train_url()


class SplashScreen(ctk.CTk):
    def __init__(self, on_finish):
        super().__init__()
        self.on_finish = on_finish
        self.overrideredirect(True)
        w, h = 480, 320
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.configure(fg_color=styles.PRIMARY)

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.place(relx=0.5, rely=0.42, anchor="center")

        ctk.CTkLabel(wrap, text="🛡️", font=("Segoe UI Emoji", 60), text_color="white").pack()
        ctk.CTkLabel(wrap, text="CriptX", font=("Segoe UI", 34, "bold"),
                     text_color="white").pack(pady=(4, 0))
        ctk.CTkLabel(wrap, text="AI-Powered Cybersecurity Awareness Chatbot",
                     font=styles.SUBTITLE_FONT, text_color="#ede9fe").pack(pady=(2, 20))

        self.progress = ctk.CTkProgressBar(self, width=360, height=10, corner_radius=6,
                                            progress_color="#ffffff", fg_color="#5b21b6")
        self.progress.place(relx=0.5, rely=0.78, anchor="center")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self, text="Initializing database...",
                                          font=styles.SMALL_FONT, text_color="#ede9fe")
        self.status_label.place(relx=0.5, rely=0.87, anchor="center")

        self.after(200, self._step1)

    def _animate_to(self, target, next_step, delay=25):
        current = self.progress.get()

        def tick(v=current):
            if v < target:
                v += 0.02
                self.progress.set(min(v, target))
                self.after(delay, lambda: tick(v))
            else:
                next_step()
        tick()

    def _step1(self):
        db.init_db()
        self.status_label.configure(text="Initializing database...")
        self._animate_to(0.35, self._step2)

    def _step2(self):
        self.status_label.configure(text="Loading AI chatbot model...")
        self._animate_to(0.7, self._step3)

    def _step3(self):
        ensure_models_trained()
        self.status_label.configure(text="Loading phishing detection model...")
        self._animate_to(1.0, self._finish)

    def _finish(self):
        self.status_label.configure(text="Ready!")
        self.after(300, self._close)

    def _close(self):
        self.destroy()
        self.on_finish()


def launch_login():
    from ui.login_window import LoginWindow

    def on_login_success(user):
        launch_dashboard(user)

    login_win = LoginWindow(on_success=on_login_success)
    login_win.mainloop()


def launch_dashboard(user):
    from ui.main_app import MainApp

    def on_logout():
        launch_login()

    app = MainApp(user, on_logout=on_logout)
    app.mainloop()


def main():
    styles.apply_base_theme()
    splash = SplashScreen(on_finish=launch_login)
    splash.mainloop()


if __name__ == "__main__":
    main()
