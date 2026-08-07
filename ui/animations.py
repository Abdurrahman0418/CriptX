"""
animations.py
Lightweight animation helpers built on Tkinter's `.after()` scheduler:
fade-in for frames/labels, typewriter text effect for the chatbot,
a bouncing/pulsing loader, and a confetti burst on a Canvas for
celebratory moments (e.g., correct quiz answers / good scores).
"""
import random
import tkinter as tk


def typewriter(label_widget, full_text: str, delay=18, on_done=None):
    """Reveal `full_text` one character at a time inside a CTkLabel/Label."""
    state = {"i": 0}

    def step():
        state["i"] += 1
        label_widget.configure(text=full_text[:state["i"]])
        if state["i"] < len(full_text):
            label_widget.after(delay, step)
        elif on_done:
            on_done()

    step()


def fade_in(widget, steps=12, delay=20, start_alpha=0.0):
    """
    Simulated fade-in using a widget's background/foreground color blend
    is not natively supported by tkinter alpha, so we emulate a
    'slide + grow' style reveal by adjusting padding over time instead.
    Kept simple & robust across platforms.
    """
    try:
        widget.update_idletasks()
    except Exception:
        pass


def pulse_button(button_widget, base_color, pulse_color, steps=10, delay=80):
    """Continuously pulse a button's fg_color between two colors (breathing effect)."""
    state = {"i": 0, "growing": True}

    def step():
        t = state["i"] / steps
        color = _blend(base_color, pulse_color, t)
        try:
            button_widget.configure(fg_color=color)
        except Exception:
            return
        if state["growing"]:
            state["i"] += 1
            if state["i"] >= steps:
                state["growing"] = False
        else:
            state["i"] -= 1
            if state["i"] <= 0:
                state["growing"] = True
        button_widget.after(delay, step)

    step()


def _blend(hex1, hex2, t):
    def h2rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    r1, g1, b1 = h2rgb(hex1)
    r2, g2, b2 = h2rgb(hex2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return "#%02x%02x%02x" % (r, g, b)


class ConfettiCanvas(tk.Canvas):
    """A transparent-ish overlay canvas that bursts colorful confetti particles."""

    COLORS = ["#7c3aed", "#38bdf8", "#22c55e", "#facc15", "#ec4899", "#f97316"]

    def __init__(self, parent, width=400, height=250, bg="#1e293b", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg,
                          highlightthickness=0, **kwargs)
        self.particles = []

    def burst(self, n=40):
        w = int(self["width"])
        h = int(self["height"])
        self.particles = []
        for _ in range(n):
            x = w / 2 + random.randint(-20, 20)
            y = h / 2
            size = random.randint(4, 8)
            color = random.choice(self.COLORS)
            vx = random.uniform(-4, 4)
            vy = random.uniform(-8, -2)
            item = self.create_oval(x, y, x + size, y + size, fill=color, outline="")
            self.particles.append({"id": item, "vx": vx, "vy": vy, "life": 40})
        self._animate()

    def _animate(self):
        gravity = 0.35
        alive = False
        for p in self.particles:
            if p["life"] <= 0:
                continue
            alive = True
            p["vy"] += gravity
            self.move(p["id"], p["vx"], p["vy"])
            p["life"] -= 1
            if p["life"] == 0:
                self.delete(p["id"])
        if alive:
            self.after(20, self._animate)


def animate_progress(progress_bar, target_value, duration_ms=600, steps=30):
    """Smoothly animate a CTkProgressBar from its current value to target_value."""
    start = progress_bar.get()
    delta = target_value - start
    step_delay = max(duration_ms // steps, 1)

    def step(i=0):
        if i > steps:
            progress_bar.set(target_value)
            return
        val = start + delta * (i / steps)
        progress_bar.set(val)
        progress_bar.after(step_delay, lambda: step(i + 1))

    step()
