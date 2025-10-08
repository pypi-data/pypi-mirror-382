from typing import Dict, List, Tuple


def parse_gkss(text: str) -> List[Tuple[str, Dict[str, str]]]:
    rules: List[Tuple[str, Dict[str, str]]] = []
    buf = text.split('}')
    for chunk in buf:
        if '{' not in chunk:
            continue
        sel, body = chunk.split('{', 1)
        sel = sel.strip()
        styles: Dict[str, str] = {}
        for line in body.strip().split(';'):
            line = line.strip()
            if not line:
                continue
            if ':' not in line:
                continue
            k, v = line.split(':', 1)
            styles[k.strip()] = v.strip()
        if sel and styles:
            rules.append((sel, styles))
    return rules


def apply_styles(widget, rules: List[Tuple[str, Dict[str, str]]]):
    wid = getattr(widget, "id", None)
    classes = getattr(widget, "classes", [])
    name = widget.__class__.__name__.lower()
    state_hover = getattr(widget, "_hover", False)

    def matches(selector: str) -> bool:
        parts = selector.split(':')
        base = parts[0]
        pseudo = parts[1] if len(parts) > 1 else None
        if pseudo == 'hover' and not state_hover:
            return False
        base = base.strip()
        if base.startswith('#'):
            return wid == base[1:]
        if base.startswith('.'):
            return base[1:] in classes
        return base == name or base == '*'

    for sel, styles in rules:
        if matches(sel):
            for k, v in styles.items():
                if k == 'background':
                    try:
                        widget.tk.configure(bg=v)
                    except Exception:
                        pass
                if k == 'color':
                    try:
                        widget.tk.configure(fg=v)
                    except Exception:
                        pass

