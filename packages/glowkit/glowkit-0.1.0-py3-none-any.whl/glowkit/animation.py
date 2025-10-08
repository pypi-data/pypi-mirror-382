import time
from typing import Callable, Optional, Tuple


EASING = {
    "linear": lambda t: t,
    "ease-in": lambda t: t * t,
    "ease-out": lambda t: 1 - (1 - t) * (1 - t),
    "ease-in-out": lambda t: 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2,
}


def _hex_to_rgb(color: str) -> Tuple[int, int, int]:
    color = color.lstrip('#')
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


class Animator:
    def __init__(self, tk_widget):
        self.tk_widget = tk_widget

    def animate_number(self, setter: Callable[[float], None], start: float, end: float, duration_ms: int, easing: str = "linear", on_done: Optional[Callable[[], None]] = None):
        ease = EASING.get(easing, EASING["linear"]) if isinstance(easing, str) else easing
        start_time = time.time()
        duration_s = duration_ms / 1000.0

        def step():
            now = time.time()
            t = (now - start_time) / duration_s
            if t >= 1:
                setter(end)
                if on_done:
                    on_done()
                return
            v = start + (end - start) * ease(max(0.0, min(1.0, t)))
            setter(v)
            self.tk_widget.after(16, step)

        step()

    def animate_color(self, setter: Callable[[str], None], start_color: str, end_color: str, duration_ms: int, easing: str = "linear", on_done: Optional[Callable[[], None]] = None):
        ease = EASING.get(easing, EASING["linear"]) if isinstance(easing, str) else easing
        start_time = time.time()
        duration_s = duration_ms / 1000.0
        sr, sg, sb = _hex_to_rgb(start_color)
        er, eg, eb = _hex_to_rgb(end_color)

        def step():
            now = time.time()
            t = (now - start_time) / duration_s
            if t >= 1:
                setter(end_color)
                if on_done:
                    on_done()
                return
            tt = ease(max(0.0, min(1.0, t)))
            r = int(sr + (er - sr) * tt)
            g = int(sg + (eg - sg) * tt)
            b = int(sb + (eb - sb) * tt)
            setter(_rgb_to_hex((r, g, b)))
            self.tk_widget.after(16, step)

        step()


