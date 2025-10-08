from typing import Dict


_current_theme: Dict[str, str] = {}


PALETTES: Dict[str, Dict[str, str]] = {
    # Simplified palettes
    "catppuccin_mocha": {
        "bg": "#1e1e2e",
        "surface": "#181825",
        "text": "#cdd6f4",
        "accent": "#89b4fa",
        "muted": "#6c7086",
        "danger": "#f38ba8",
        "success": "#a6e3a1",
    },
    "nord": {
        "bg": "#2e3440",
        "surface": "#3b4252",
        "text": "#eceff4",
        "accent": "#88c0d0",
        "muted": "#616e88",
        "danger": "#bf616a",
        "success": "#a3be8c",
    },
    "dracula": {
        "bg": "#282a36",
        "surface": "#21222c",
        "text": "#f8f8f2",
        "accent": "#bd93f9",
        "muted": "#6272a4",
        "danger": "#ff5555",
        "success": "#50fa7b",
    },
    "tokyo_night": {
        "bg": "#1a1b26",
        "surface": "#16161e",
        "text": "#c0caf5",
        "accent": "#7aa2f7",
        "muted": "#565f89",
        "danger": "#f7768e",
        "success": "#9ece6a",
    },
}


def apply_theme(name: str):
    theme = PALETTES.get(name)
    if not theme:
        raise ValueError(f"Unknown theme '{name}'")
    _current_theme.clear()
    _current_theme.update(theme)


def theme() -> Dict[str, str]:
    if not _current_theme:
        apply_theme("catppuccin_mocha")
    return _current_theme


