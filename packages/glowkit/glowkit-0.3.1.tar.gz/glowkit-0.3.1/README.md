Glowkit

Install

```bash
pip install glowkit
```

Quickstart

```python
import glowkit as gk

def main_window():
    with gk.Window(title="Glowkit", width=800, height=600, frosted_glass=True) as window:
        with gk.Container(layout='flex', direction='column', gap=10, padding=20):
            gk.Label("Hello", font_size=24, weight='bold')
            with gk.Container(layout='flex', direction='row', gap=8):
                btn = gk.Button("Click me")
                @btn.on_click
                def _():
                    btn.animate(property='bg', to='#50fa7b', duration=400, easing='ease-in-out')
    window.show()

if __name__ == "__main__":
    app = gk.Application()
    gk.apply_theme('catppuccin_mocha')
    splash = gk.SplashScreen(min_time=1.5)
    splash.show_and_run(main_window)
    app.exec()
```

License

MIT

