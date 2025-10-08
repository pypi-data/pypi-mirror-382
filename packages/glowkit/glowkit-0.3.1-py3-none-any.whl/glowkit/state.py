from typing import Any, Callable, Dict, List


class State:
    def __init__(self, **values):
        self._values: Dict[str, Any] = dict(values)
        self._subs: List[Callable[[str, Any], None]] = []

    def get(self, key: str) -> Any:
        return self._values.get(key)

    def set(self, key: str, value: Any):
        self._values[key] = value
        for sub in list(self._subs):
            sub(key, value)

    def subscribe(self, fn: Callable[[str, Any], None]):
        self._subs.append(fn)
        return lambda: self._subs.remove(fn)

    def bind_text(self, widget, key: str, fmt: str = "{value}"):
        def _apply(w):
            w.tk.configure(text=fmt.format(value=self.get(key)))
        try:
            _apply(widget)
        except Exception:
            pass
        if hasattr(widget, "on_realized"):
            widget.on_realized(lambda w: _apply(w))
        def _on_change(k, v):
            if k == key:
                try:
                    widget.tk.configure(text=fmt.format(value=v))
                except Exception:
                    pass
        return self.subscribe(_on_change)

