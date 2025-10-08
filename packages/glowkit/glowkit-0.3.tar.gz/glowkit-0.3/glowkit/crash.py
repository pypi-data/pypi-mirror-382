import traceback
import tkinter as tk
from typing import Callable

from .themes import theme


def safe_call(fn: Callable, on_error: Callable[[Exception], None]):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            on_error(e)
    return wrapper


def show_crash_overlay(parent: tk.Misc, error: Exception):
    msg = ''.join(traceback.format_exception_only(type(error), error)).strip()
    overlay = tk.Toplevel(parent)
    overlay.overrideredirect(True)
    overlay.configure(bg=theme()["surface"])
    try:
        overlay.attributes("-alpha", 0.97)
    except Exception:
        pass
    x = parent.winfo_rootx()
    y = parent.winfo_rooty()
    w = parent.winfo_width() or 400
    h = parent.winfo_height() or 200
    overlay.geometry(f"{w}x{h}+{x}+{y}")
    frame = tk.Frame(overlay, bg=theme()["surface"], padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    title = tk.Label(frame, text="Glowkit crashed", fg=theme()["danger"], bg=theme()["surface"], font=("Segoe UI", 16, "bold"))
    title.pack(anchor="w")
    body = tk.Label(frame, text=msg, fg=theme()["text"], bg=theme()["surface"], justify="left")
    body.pack(anchor="w")
    return overlay

