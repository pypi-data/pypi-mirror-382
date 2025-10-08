# PRISMA TUI
**Prisma TUI** (Python teRminal graphIcS with Multilayered trAnsparency) is a Python framework for building composable Terminal User Interfaces (TUIs). The `Terminal` class serves as a wrapper for terminal backends (e.g. curses) while providing a customizable application loop. Flexible layouts can be arranged by creating a hierarchy of `Section` class instances. Complex displays can be composed by

**Prisma** is built around the idea of *multilayered transparency*, which consists in overlaying different "layers" of text on top of each other and merging them together to compose more complex displays (think of stacking together images with transparency). This can be achieved by using the `Layer` class. **Prisma** also provides advanced color management, allowing to write and read multi-colored layers from its own custom **PAL** (*PALette*, JSON with color pair values) and **PRI** (*PRisma Image*, binary with the chars and the respective color pairs to form an image) formats.

<p align="center">
  <img src="logo.png" alt="Prisma TUI Logo" width="200"/><br>
  Rendition of <i>Prisma, the cat</i>.
</p>


<!-- ----------------------------------------------------------------------- -->
## QuickStart
### Run Demo
```
pip install prisma-tui
python3 demos/layouts.py
```

## Code Example
```python
import prismatui as pr

class MyTUI(pr.Terminal):
    def on_start(self):
        pr.init_pair(1, pr.COLOR_BLACK, pr.COLOR_CYAN)

    def on_update(self):
        self.draw_text('c', 'c', "Hello, pr!", pr.A_BOLD)
        self.draw_text("c+1", 'c', f"Key pressed: {self.key}", pr.A_BOLD)
        self.draw_text('b', 'l', "Press F1 to exit", pr.get_color_pair(1))

    def should_stop(self):
        return self.key == pr.KEY_F1

if __name__ == "__main__":
    MyTUI().run()
```


<!-- ----------------------------------------------------------------------- -->
## Core Concepts
- **Terminal:** Main application class; manages input, rendering, and lifecycle.
- **Section:** Container for layers and child sections, enabling complex layouts.
- **Layer:** 2D grid of [`prisma.Pixel`](prisma/pixel.py) objects. Layers can be combined by overwritting, blending or merging their attributes.
- **Palette:** Handles palette loading for easy setup of colors.


<!-- ----------------------------------------------------------------------- -->
## Demos
See the [`demos/`](demos/) folder for example applications:
- [`images.py`](demos/images.py): Image rendered from a pair of PRI and PAL files.
- [`layouts.py`](demos/layouts.py): Example of a complex layout built using different Section techniques.
- [`movement.py`](demos/movement.py): Example of an application in no-delay mode.
- [`keys.py`](demos/keys.py): Simple "hello world" example.


<!-- ----------------------------------------------------------------------- -->
## License
MIT License. See [LICENSE](LICENSE).


<!-- ----------------------------------------------------------------------- -->
# TODO
- Make `utilities/image_formatter.py` into an actual utility.


<!-- ----------------------------------------------------------------------- -->
