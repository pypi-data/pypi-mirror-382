import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, List

from .app import Application
from .core import mount, current_parent
from .themes import theme
from .animation import Animator


class BaseWidget:
    def __init__(self):
        self._tk: Optional[tk.Widget] = None
        self._animator: Optional[Animator] = None

    @property
    def tk(self) -> tk.Widget:
        if self._tk is None:
            raise RuntimeError("Widget not realized yet")
        return self._tk

    def realize(self, parent: Optional[tk.Misc]):
        raise NotImplementedError

    def animate(self, property: str, to, duration: int = 300, easing: str = "linear"):
        if self._animator is None:
            self._animator = Animator(self.tk)
        if property == "bg":
            start = self.tk.cget("bg")
            end = str(to)
            self._animator.animate_color(lambda c: self.tk.configure(bg=c), start, end, duration, easing)
        elif property == "fg":
            start = self.tk.cget("fg") if hasattr(self.tk, "cget") else theme()["text"]
            end = str(to)
            self._animator.animate_color(lambda c: self.tk.configure(fg=c), start, end, duration, easing)
        elif property in ("x", "y"):
            info = self.tk.place_info() if hasattr(self.tk, "place_info") else {}
            start = float(info.get(property, 0) or 0)
            end = float(to)
            def set_pos(v):
                kwargs = {property: int(v)}
                try:
                    self.tk.place_configure(**kwargs)
                except Exception:
                    pass
            self._animator.animate_number(set_pos, start, end, duration, easing)
        else:
            return


class Window(BaseWidget):
    def __init__(self, title: str = "Glowkit Window", width: int = 800, height: int = 600, frosted_glass: bool = False):
        super().__init__()
        self.title = title
        self.width = width
        self.height = height
        self.frosted_glass = frosted_glass
        self._children: List[BaseWidget] = []
        self._app: Optional[Application] = None

    def __enter__(self):
        self._app = Application()
        with mount(self):
            return self

    def __exit__(self, exc_type, exc, tb):
        root = self._app.root
        self._tk = tk.Toplevel(root)
        self._tk.title(self.title)
        self._tk.geometry(f"{self.width}x{self.height}")
        bg = theme()["bg"]
        self._tk.configure(bg=bg)
        if self.frosted_glass:
            try:
                self._tk.attributes("-alpha", 0.95)
            except Exception:
                pass
        for child in self._children:
            child.realize(self._tk)

    def add_child(self, child: "BaseWidget"):
        self._children.append(child)

    def set_frosted_glass(self, enabled: bool, blur_amount: int = 15, tint_color: str = "#ffffff10"):
        self.frosted_glass = enabled
        try:
            self.tk.attributes("-alpha", 0.92 if enabled else 1.0)
        except Exception:
            pass

    def show(self):
        self.tk.deiconify()


class Container(BaseWidget):
    def __init__(self, layout: str = "flex", direction: str = "column", gap: int = 8, padding: int = 0, justify_content: str = "start"):
        super().__init__()
        self.layout = layout
        self.direction = direction
        self.gap = gap
        self.padding = padding
        self.justify_content = justify_content
        self._children: List[BaseWidget] = []
        parent = current_parent()
        if isinstance(parent, Window) or isinstance(parent, Container):
            parent.add_child(self)

    def __enter__(self):
        return mount(self).__enter__()

    def __exit__(self, exc_type, exc, tb):
        return mount(self).__exit__(exc_type, exc, tb)

    def add_child(self, child: "BaseWidget"):
        self._children.append(child)

    def realize(self, parent: tk.Misc):
        frame = tk.Frame(parent, bg=theme()["surface"], padx=self.padding, pady=self.padding)
        self._tk = frame
        # Simple flex emulation using pack
        if self.direction == "row":
            for i, child in enumerate(self._children):
                child.realize(frame)
                child.tk.pack(side=tk.LEFT, padx=(self.gap if i > 0 else 0, 0))
        else:
            for i, child in enumerate(self._children):
                child.realize(frame)
                child.tk.pack(side=tk.TOP, pady=(self.gap if i > 0 else 0, 0), anchor="w")
        frame.pack(fill=tk.BOTH, expand=True)


class Label(BaseWidget):
    def __init__(self, text: str, font_size: int = 14, weight: str = "normal"):
        super().__init__()
        self.text = text
        self.font_size = font_size
        self.weight = weight
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def realize(self, parent: tk.Misc):
        fg = theme()["text"]
        bg = theme()["surface"]
        self._tk = tk.Label(parent, text=self.text, fg=fg, bg=bg, font=("Segoe UI", self.font_size, self.weight))


class Button(BaseWidget):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self._on_click: Optional[Callable[[], None]] = None
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def on_click(self, fn: Callable[[], None]):
        self._on_click = fn
        return fn

    def realize(self, parent: tk.Misc):
        colors = theme()
        style = ttk.Style()
        style.configure("Glow.TButton", foreground=colors["text"], background=colors["accent"], padding=(12, 8))
        btn = ttk.Button(parent, text=self.text, style="Glow.TButton", command=lambda: self._on_click and self._on_click())
        self._tk = btn


class Icon(BaseWidget):
    def __init__(self, name: str, color: str = "#ffffff"):
        super().__init__()
        self.name = name
        self.color = color
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def realize(self, parent: tk.Misc):
        self._tk = tk.Label(parent, text=self.name, fg=self.color, bg=theme()["surface"], font=("Segoe UI", 10))


class TabView(BaseWidget):
    def __init__(self, orientation: str = "top"):
        super().__init__()
        self.orientation = orientation
        self._tabs: List[tuple[str, Container]] = []
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def add_tab(self, title: str, builder: Callable[[], Any]):
        c = Container()
        builder()
        self._tabs.append((title, c))

    def realize(self, parent: tk.Misc):
        nb = ttk.Notebook(parent)
        self._tk = nb
        for title, container in self._tabs:
            frame = tk.Frame(nb, bg=theme()["surface"])
            container.realize(frame)
            nb.add(frame, text=title)


