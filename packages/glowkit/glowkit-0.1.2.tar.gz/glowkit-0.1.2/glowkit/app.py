import tkinter as tk
import sys


class Application:
    def __init__(self):
        self._root = None

    @property
    def root(self) -> tk.Tk:
        if self._root is None:
            self._root = tk.Tk()
            self._root.withdraw()
        return self._root

    def exec(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            sys.exit(0)


