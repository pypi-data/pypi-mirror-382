import tkinter as tk
import time
from typing import Optional

from .themes import theme


def show_toast(root: tk.Misc, message: str, duration_ms: int = 2000):
    top = tk.Toplevel(root)
    top.overrideredirect(True)
    top.configure(bg=theme()["surface"]) 
    try:
        top.attributes("-alpha", 0.0)
    except Exception:
        pass
    w = 300
    h = 48
    sw = top.winfo_screenwidth()
    sh = top.winfo_screenheight()
    x = int(sw - w - 24)
    y = int(sh - h - 64)
    top.geometry(f"{w}x{h}+{x}+{y}")
    label = tk.Label(top, text=message, fg=theme()["text"], bg=theme()["surface"], font=("Segoe UI", 10))
    label.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    start = time.time()

    def fade_in():
        try:
            a = top.attributes("-alpha")
        except Exception:
            return
        a = float(a)
        a = min(1.0, a + 0.1)
        try:
            top.attributes("-alpha", a)
        except Exception:
            pass
        if a < 1.0:
            top.after(20, fade_in)
        else:
            top.after(duration_ms, fade_out)

    def fade_out():
        try:
            a = top.attributes("-alpha")
        except Exception:
            top.destroy()
            return
        a = float(a)
        a = max(0.0, a - 0.08)
        try:
            top.attributes("-alpha", a)
        except Exception:
            pass
        if a > 0.0:
            top.after(20, fade_out)
        else:
            top.destroy()

    fade_in()
    return top

