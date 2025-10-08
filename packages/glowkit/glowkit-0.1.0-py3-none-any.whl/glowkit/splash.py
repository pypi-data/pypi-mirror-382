import tkinter as tk
import time
from typing import Callable, Optional

from .app import Application
from .themes import theme


class SplashScreen:
    def __init__(self, image_path: Optional[str] = None, loading_text: str = "", progress_bar: bool = True, min_time: float = 1.5):
        self.image_path = image_path
        self.loading_text = loading_text
        self.progress_bar = progress_bar
        self.min_time = min_time
        self._progress = 0.0
        self._top: Optional[tk.Toplevel] = None

    def show_and_run(self, main_builder: Callable[[], None]):
        app = Application()
        root = app.root
        top = tk.Toplevel(root)
        self._top = top
        top.overrideredirect(True)
        top.geometry("480x300")
        top.configure(bg=theme()["surface"]) 
        try:
            top.attributes("-alpha", 0.98)
        except Exception:
            pass

        canvas = tk.Canvas(top, width=480, height=300, highlightthickness=0, bg=theme()["surface"]) 
        canvas.pack(fill=tk.BOTH, expand=True)

        image_obj = None
        if self.image_path:
            try:
                image_obj = tk.PhotoImage(file=self.image_path)
                canvas.create_image(240, 120, image=image_obj)
                canvas.image = image_obj
            except Exception:
                pass

        if self.loading_text:
            canvas.create_text(240, 220, text=self.loading_text, fill=theme()["text"], font=("Segoe UI", 12))

        progress_rect = None
        if self.progress_bar:
            canvas.create_rectangle(90, 240, 390, 260, outline=theme()["muted"], width=2)
            progress_rect = canvas.create_rectangle(92, 242, 92, 258, fill=theme()["accent"], width=0)

        start_time = time.time()

        def update_progress(value: float):
            self._progress = max(0.0, min(1.0, value))
            if progress_rect is not None:
                width = 296 * self._progress
                canvas.coords(progress_rect, 92, 242, 92 + width, 258)

        def proceed():
            elapsed = time.time() - start_time
            remaining = max(0.0, self.min_time - elapsed)
            top.after(int(remaining * 1000), finish)

        def finish():
            try:
                top.destroy()
            except Exception:
                pass
            main_builder()

        def pulse():
            if self._top is None:
                return
            new_val = (self._progress + 0.03) % 1.0
            update_progress(new_val)
            top.after(50, pulse)

        pulse()
        proceed()


