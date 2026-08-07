"""
threatfeed_window.py
A live 'Threat Intel Feed' tab that automatically fetches the latest
real-world cybersecurity news headlines in the background (no user
action needed), giving CriptX a real-time personal-assistant feel.

Runs the network fetch on a background thread so the UI never freezes,
and auto-refreshes every few minutes. Falls back gracefully to a
friendly offline message if there's no internet connection.
"""
import threading
import xml.etree.ElementTree as ET
import customtkinter as ctk
import requests

from ui import styles

RSS_FEEDS = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
]

AUTO_REFRESH_MS = 5 * 60 * 1000  # auto-refresh every 5 minutes
REQUEST_TIMEOUT = 6


class ThreatFeedFrame(ctk.CTkFrame):
    def __init__(self, parent, user):
        super().__init__(parent, fg_color=styles.BG_DARK, corner_radius=0)
        self.user = user
        self._destroyed = False
        self.bind("<Destroy>", self._on_destroy)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text="🌐 Live Threat Intel Feed", font=styles.HEADER_FONT,
                     text_color=styles.TEXT_PRIMARY).pack(side="left")

        self.status_label = ctk.CTkLabel(header, text="Fetching latest headlines...",
                                          font=styles.SMALL_FONT, text_color=styles.TEXT_MUTED)
        self.status_label.pack(side="right", padx=(0, 10))

        ctk.CTkButton(header, text="🔄 Refresh Now", width=130, height=32, corner_radius=8,
                      fg_color=styles.PRIMARY, hover_color=styles.PRIMARY_HOVER,
                      font=("Segoe UI", 12, "bold"),
                      command=self.refresh_feed).pack(side="right", padx=8)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=25, pady=(10, 20))

        self.refresh_feed()

    def refresh_feed(self):
        self.status_label.configure(text="Fetching latest headlines...")
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        articles = []
        error_msg = None
        for source_name, url in RSS_FEEDS:
            try:
                resp = requests.get(url, timeout=REQUEST_TIMEOUT,
                                     headers={"User-Agent": "Mozilla/5.0 (CriptX Assistant)"})
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:6]:
                    title_el = item.find("title")
                    link_el = item.find("link")
                    title = title_el.text.strip() if title_el is not None and title_el.text else "Untitled"
                    link = link_el.text.strip() if link_el is not None and link_el.text else ""
                    articles.append({"source": source_name, "title": title, "link": link})
            except Exception as e:
                error_msg = str(e)
                continue

        if self._destroyed:
            return

        if articles:
            self.after(0, lambda: self._render_articles(articles))
        else:
            self.after(0, lambda: self._render_offline(error_msg))

    def _render_articles(self, articles):
        if self._destroyed:
            return
        for w in self.scroll.winfo_children():
            w.destroy()

        self.status_label.configure(
            text=f"✅ Live • {len(articles)} headlines • auto-refreshes every 5 min")

        colors = [styles.ACCENT_BLUE, styles.PRIMARY, styles.ACCENT_PINK, styles.ACCENT_GREEN]
        for i, art in enumerate(articles):
            color = colors[i % len(colors)]
            card = ctk.CTkFrame(self.scroll, fg_color=styles.BG_CARD, corner_radius=12,
                                 border_width=2, border_color=color)
            card.pack(fill="x", pady=6)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=16, pady=(12, 2))
            ctk.CTkLabel(top, text=f"📰 {art['source']}", font=styles.SMALL_FONT,
                         text_color=color).pack(side="left")

            ctk.CTkLabel(card, text=art["title"], font=styles.BODY_FONT,
                         text_color=styles.TEXT_PRIMARY, wraplength=800, justify="left",
                         anchor="w").pack(anchor="w", padx=16, pady=(0, 6))

            if art["link"]:
                link_label = ctk.CTkLabel(card, text="🔗 Open article", font=styles.SMALL_FONT,
                                           text_color=styles.ACCENT_BLUE, cursor="hand2")
                link_label.pack(anchor="w", padx=16, pady=(0, 12))
                link_label.bind("<Button-1>", lambda e, url=art["link"]: self._open_link(url))

        if not self._destroyed:
            self.after(AUTO_REFRESH_MS, self.refresh_feed)

    def _render_offline(self, error_msg):
        if self._destroyed:
            return
        for w in self.scroll.winfo_children():
            w.destroy()

        self.status_label.configure(text="⚠ Offline / no connection")

        card = ctk.CTkFrame(self.scroll, fg_color=styles.BG_CARD, corner_radius=12,
                             border_width=2, border_color=styles.ACCENT_YELLOW)
        card.pack(fill="x", pady=10)
        ctk.CTkLabel(card, text="📡 Couldn't reach the live news feed right now.",
                     font=styles.BODY_FONT, text_color=styles.TEXT_PRIMARY
                     ).pack(padx=20, pady=(20, 6))
        ctk.CTkLabel(card, text="Check your internet connection and click 'Refresh Now'. "
                                "(This tab pulls real-time headlines from public cybersecurity "
                                "news RSS feeds — it needs an active internet connection on this "
                                "computer to work.)",
                     font=styles.SMALL_FONT, text_color=styles.TEXT_SECONDARY,
                     wraplength=700, justify="left").pack(padx=20, pady=(0, 20))

        if not self._destroyed:
            self.after(AUTO_REFRESH_MS, self.refresh_feed)

    def _open_link(self, url):
        import webbrowser
        webbrowser.open(url)

    def _on_destroy(self, event=None):
        self._destroyed = True
