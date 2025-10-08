import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, List

from .app import Application
from .core import mount, current_parent
from .themes import theme
from .animation import Animator
from .crash import safe_call, show_crash_overlay


class BaseWidget:
    def __init__(self):
        self._tk: Optional[Any] = None
        self._animator: Optional[Animator] = None
        self.id: Optional[str] = None
        self.classes: List[str] = []
        self._hover = False
        self._realized_callbacks: List[Callable[["BaseWidget"], None]] = []

    @property
    def tk(self) -> Any:
        if self._tk is None:
            raise RuntimeError("Widget not realized yet")
        return self._tk

    def realize(self, parent: Any):
        raise NotImplementedError

    def on_realized(self, fn: Callable[["BaseWidget"], None]):
        if self._tk is not None:
            fn(self)
        else:
            self._realized_callbacks.append(fn)

    def _fire_realized(self):
        if self._realized_callbacks:
            cbs = list(self._realized_callbacks)
            self._realized_callbacks.clear()
            for cb in cbs:
                try:
                    cb(self)
                except Exception:
                    pass

    def animate(self, property: str, to, duration: int = 300, easing: str = "linear"):
        if self._animator is None:
            self._animator = Animator(self.tk)
        if property == "bg":
            try:
                start = self.tk.cget("bg")
            except Exception:
                start = theme()["surface"]
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
        self._cm = None

    def __enter__(self):
        self._app = Application()
        self._cm = mount(self)
        self._cm.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._cm is not None:
            self._cm.__exit__(exc_type, exc, tb)
            self._cm = None
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
            try:
                child.realize(self._tk)
            except Exception as e:
                show_crash_overlay(self._tk, e)

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
        self._cm = None
        parent = current_parent()
        if isinstance(parent, Window) or isinstance(parent, Container):
            parent.add_child(self)

    def __enter__(self):
        self._cm = mount(self)
        return self._cm.__enter__()

    def __exit__(self, exc_type, exc, tb):
        if self._cm is not None:
            result = self._cm.__exit__(exc_type, exc, tb)
            self._cm = None
            return result
        return False

    def add_child(self, child: "BaseWidget"):
        self._children.append(child)

    def realize(self, parent: Any):
        frame = tk.Frame(parent, bg=theme()["surface"], padx=self.padding, pady=self.padding)
        self._tk = frame
        if self.direction == "row":
            for i, child in enumerate(self._children):
                child.realize(frame)
                child.tk.pack(side=tk.LEFT, padx=(self.gap if i > 0 else 0, 0))
        else:
            for i, child in enumerate(self._children):
                child.realize(frame)
                child.tk.pack(side=tk.TOP, pady=(self.gap if i > 0 else 0, 0), anchor="w")
        frame.pack(fill=tk.BOTH, expand=True)
        self._fire_realized()


class Label(BaseWidget):
    def __init__(self, text: str, font_size: int = 14, weight: str = "normal"):
        super().__init__()
        self.text = text
        self.font_size = font_size
        self.weight = weight
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def realize(self, parent: Any):
        fg = theme()["text"]
        bg = theme()["surface"]
        self._tk = tk.Label(parent, text=self.text, fg=fg, bg=bg, font=("Segoe UI", self.font_size, self.weight))
        self._fire_realized()


class TextBox(BaseWidget):
    def __init__(self, text: str = "", id: Optional[str] = None, classes: Optional[List[str]] = None):
        super().__init__()
        self.text = text
        self.id = id
        self.classes = classes or []
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def realize(self, parent: Any):
        e = tk.Entry(parent, relief=tk.FLAT, bg=theme()["surface"], fg=theme()["text"], insertbackground=theme()["text"]) 
        e.insert(0, self.text)
        self._tk = e
        self._fire_realized()


class Button(BaseWidget):
    def __init__(self, text: str, id: Optional[str] = None, classes: Optional[List[str]] = None):
        super().__init__()
        self.text = text
        self._on_click: Optional[Callable[[], None]] = None
        self._normal_bg = None
        self._hover_bg = None
        self.id = id
        self.classes = classes or []
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def on_click(self, fn: Callable[[], None]):
        self._on_click = fn
        return fn

    def realize(self, parent: Any):
        colors = theme()
        self._normal_bg = colors["accent"]
        self._hover_bg = colors["success"]
        btn = tk.Button(
            parent,
            text=self.text,
            fg=colors["text"],
            bg=self._normal_bg,
            activebackground=colors["muted"],
            activeforeground=colors["text"],
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=10,
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
            highlightthickness=0,
        )
        def _click():
            try:
                if self._on_click:
                    self._on_click()
            except Exception as e:
                show_crash_overlay(parent, e)
        btn.configure(command=_click)
        def on_enter(_):
            self._hover = True
            btn.configure(bg=self._hover_bg)
        def on_leave(_):
            self._hover = False
            btn.configure(bg=self._normal_bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        self._tk = btn
        self._fire_realized()


class Icon(BaseWidget):
    def __init__(self, name: str, color: str = "#ffffff"):
        super().__init__()
        self.name = name
        self.color = color
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def realize(self, parent: Any):
        self._tk = tk.Label(parent, text=self.name, fg=self.color, bg=theme()["surface"], font=("Segoe UI", 10))
        self._fire_realized()


class CheckBox(BaseWidget):
    def __init__(self, label: str = "", checked: bool = False):
        super().__init__()
        self.label = label
        self.var = tk.BooleanVar(value=checked)
        self._on_change: Optional[Callable[[bool], None]] = None
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def on_change(self, fn: Callable[[bool], None]):
        self._on_change = fn
        return fn

    def realize(self, parent: Any):
        cb = tk.Checkbutton(parent, text=self.label, variable=self.var, onvalue=True, offvalue=False, bg=theme()["surface"], fg=theme()["text"], selectcolor=theme()["surface"], activebackground=theme()["surface"]) 
        def _changed():
            try:
                if self._on_change:
                    self._on_change(bool(self.var.get()))
            except Exception as e:
                show_crash_overlay(parent, e)
        cb.configure(command=_changed)
        self._tk = cb
        self._fire_realized()


class Toggle(BaseWidget):
    def __init__(self, value: bool = False):
        super().__init__()
        self.value = value
        self._on_change: Optional[Callable[[bool], None]] = None
        self._knob_t = 1.0 if value else 0.0
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def on_change(self, fn: Callable[[bool], None]):
        self._on_change = fn
        return fn

    def _redraw(self):
        c: tk.Canvas = self._tk
        c.delete("all")
        w = 48
        h = 28
        r = h // 2
        bg_on = theme()["success"]
        bg_off = theme()["muted"]
        def lerp(a, b, t):
            return a + (b - a) * t
        c.create_oval(2, 2, 2 + 2*r, 2 + 2*r, fill='', outline='')
        c.create_oval(w - 2*r - 2, 2, w - 2, 2 + 2*r, fill='', outline='')
        t = self._knob_t
        bg = bg_off if t < 0.5 else bg_on
        c.create_rectangle(r, 2, w - r, 2 + 2*r, outline='', fill=bg)
        c.create_oval(2, 2, 2 + 2*r, 2 + 2*r, outline='', fill=bg)
        c.create_oval(w - 2*r - 2, 2, w - 2, 2 + 2*r, outline='', fill=bg)
        x0 = 2 + t * (w - 2*r - 4)
        c.create_oval(x0, 2, x0 + 2*r, 2 + 2*r, outline='', fill=theme()["surface"]) 

    def realize(self, parent: Any):
        c = tk.Canvas(parent, width=48, height=28, bg=theme()["surface"], highlightthickness=0)
        self._tk = c
        self._animator = Animator(c)
        self._redraw()
        def toggle(_=None):
            new_val = not self.value
            self.value = new_val
            start = self._knob_t
            end = 1.0 if new_val else 0.0
            def set_t(v):
                self._knob_t = v
                self._redraw()
            self._animator.animate_number(set_t, start, end, 180, "ease-in-out")
            try:
                if self._on_change:
                    self._on_change(self.value)
            except Exception as e:
                show_crash_overlay(parent, e)
        c.bind("<Button-1>", toggle)
        self._fire_realized()

    def bind_state(self, state, key: str):
        def apply_from_state(_k=None, _v=None):
            v = bool(state.get(key))
            if v != self.value:
                self.value = v
                self._knob_t = 1.0 if v else 0.0
                self._redraw()
        state.subscribe(lambda k, v: k == key and apply_from_state(k, v))
        self.on_realized(lambda _: apply_from_state())
        self.on_change(lambda v: state.set(key, v))

    
def _bind_checkbox_state(cb: CheckBox, state, key: str):
    def apply_from_state(_k=None, _v=None):
        try:
            val = bool(state.get(key))
            cb.var.set(val)
        except Exception:
            pass
    state.subscribe(lambda k, v: k == key and apply_from_state(k, v))
    cb.on_realized(lambda _: apply_from_state())
    cb.on_change(lambda v: state.set(key, v))


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

    def realize(self, parent: Any):
        nb = ttk.Notebook(parent)
        self._tk = nb
        for title, container in self._tabs:
            frame = tk.Frame(nb, bg=theme()["surface"])
            container.realize(frame)
            nb.add(frame, text=title)
        self._fire_realized()


class ListView(BaseWidget):
    def __init__(self, items: Optional[List[str]] = None):
        super().__init__()
        self.items = items or []
        parent = current_parent()
        if isinstance(parent, (Window, Container)):
            parent.add_child(self)

    def realize(self, parent: Any):
        lb = tk.Listbox(parent, bg=theme()["surface"], fg=theme()["text"], selectbackground=theme()["muted"], activestyle="none") 
        for it in self.items:
            lb.insert(tk.END, it)
        self._tk = lb
        self._fire_realized()


class ScrollContainer(Container):
    def realize(self, parent: Any):
        canvas = tk.Canvas(parent, bg=theme()["surface"], highlightthickness=0)
        frame = tk.Frame(canvas, bg=theme()["surface"]) 
        vsb = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        self._tk = frame
        inner_parent = frame
        for i, child in enumerate(self._children):
            child.realize(inner_parent)
            child.tk.pack(side=tk.TOP, pady=(self.gap if i > 0 else 0, 0), anchor="w")
        canvas.create_window((0, 0), window=frame, anchor="nw")
        def on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        frame.bind("<Configure>", on_config)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._fire_realized()


class ProgressBar(BaseWidget):
    def __init__(self, value: float = 0.0):
        super().__init__()
        self.value = max(0.0, min(1.0, float(value)))
        self._animator = None

    def realize(self, parent: Any):
        c = tk.Canvas(parent, height=12, bg=theme()["surface"], highlightthickness=0)
        self._tk = c
        self._animator = Animator(c)
        self._redraw()
        self._fire_realized()

    def _redraw(self):
        c: tk.Canvas = self._tk
        c.delete("all")
        w = max(100, int(c.winfo_width() or 200))
        h = 12
        c.configure(height=h)
        c.create_rectangle(0, 0, w, h, outline=theme()["muted"], width=1)
        fill_w = int(w * self.value)
        c.create_rectangle(0, 0, fill_w, h, outline="", fill=theme()["accent"]) 

    def set(self, value: float, animate_ms: int = 300):
        value = max(0.0, min(1.0, float(value)))
        start = self.value
        end = value
        def set_v(v):
            self.value = v
            self._redraw()
        self._animator.animate_number(set_v, start, end, animate_ms, "ease-in-out")


class Modal(BaseWidget):
    def __init__(self, title: str = "", content: Optional[str] = None):
        super().__init__()
        self.title = title
        self.content = content or ""
        self._on_confirm: Optional[Callable[[], None]] = None
        self._on_cancel: Optional[Callable[[], None]] = None

    def on_confirm(self, fn: Callable[[], None]):
        self._on_confirm = fn
        return fn

    def on_cancel(self, fn: Callable[[], None]):
        self._on_cancel = fn
        return fn

    def realize(self, parent: Any):
        root = parent.winfo_toplevel()
        overlay = tk.Toplevel(root)
        overlay.overrideredirect(True)
        try:
            overlay.attributes("-alpha", 0.0)
        except Exception:
            pass
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = max(480, root.winfo_width())
        h = max(320, root.winfo_height())
        overlay.geometry(f"{w}x{h}+{x}+{y}")
        overlay.configure(bg=theme()["surface"])
        canvas = tk.Canvas(overlay, bg=theme()["surface"], highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        box = tk.Frame(canvas, bg=theme()["surface"], padx=16, pady=16)
        box.place(relx=0.5, rely=0.5, anchor="center")
        title = tk.Label(box, text=self.title, fg=theme()["text"], bg=theme()["surface"], font=("Segoe UI", 14, "bold"))
        body = tk.Label(box, text=self.content, fg=theme()["text"], bg=theme()["surface"], justify="left")
        title.pack(anchor="w")
        body.pack(anchor="w", pady=(8, 12))
        row = tk.Frame(box, bg=theme()["surface"])
        row.pack(anchor="e")
        btn_ok = tk.Button(row, text="Confirm", bg=theme()["success"], fg=theme()["text"], relief=tk.FLAT, bd=0, padx=12, pady=8)
        btn_cancel = tk.Button(row, text="Cancel", bg=theme()["muted"], fg=theme()["text"], relief=tk.FLAT, bd=0, padx=12, pady=8)
        btn_ok.pack(side=tk.LEFT, padx=6)
        btn_cancel.pack(side=tk.LEFT, padx=6)

        def fade_in():
            try:
                a = float(overlay.attributes("-alpha"))
                a = min(0.95, a + 0.08)
                overlay.attributes("-alpha", a)
            except Exception:
                pass
            if a < 0.95:
                overlay.after(16, fade_in)

        def close(with_confirm: bool):
            def fade_out():
                try:
                    a = float(overlay.attributes("-alpha"))
                    a = max(0.0, a - 0.08)
                    overlay.attributes("-alpha", a)
                except Exception:
                    overlay.destroy()
                    return
                if a > 0.0:
                    overlay.after(16, fade_out)
                else:
                    try:
                        overlay.destroy()
                    finally:
                        try:
                            if with_confirm and self._on_confirm:
                                self._on_confirm()
                            if not with_confirm and self._on_cancel:
                                self._on_cancel()
                        except Exception as e:
                            show_crash_overlay(root, e)
            fade_out()

        btn_ok.configure(command=lambda: close(True))
        btn_cancel.configure(command=lambda: close(False))
        overlay.bind("<Button-1>", lambda e: close(False) if e.widget is overlay else None)
        fade_in()
        self._tk = overlay
        self._fire_realized()


