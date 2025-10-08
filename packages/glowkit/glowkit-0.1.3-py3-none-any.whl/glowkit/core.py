from contextlib import contextmanager
from typing import List, Optional, Any


class BuildContext:
    def __init__(self):
        self.stack: List[Any] = []

    def push(self, item: Any):
        self.stack.append(item)

    def pop(self) -> Any:
        return self.stack.pop()

    @property
    def parent(self) -> Optional[Any]:
        if not self.stack:
            return None
        return self.stack[-1]


build_context = BuildContext()


@contextmanager
def mount(node):
    build_context.push(node)
    try:
        yield node
    finally:
        build_context.pop()


def current_parent():
    return build_context.parent


