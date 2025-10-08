import os
import time
from typing import Callable, List


def watch_and_reload(paths: List[str], on_change: Callable[[], None], interval: float = 0.5):
    mtimes = {p: os.path.getmtime(p) for p in paths if os.path.exists(p)}
    def tick():
        changed = False
        for p in list(mtimes.keys()):
            try:
                m = os.path.getmtime(p)
            except FileNotFoundError:
                continue
            if m != mtimes[p]:
                mtimes[p] = m
                changed = True
        if changed:
            on_change()
    return tick, interval

