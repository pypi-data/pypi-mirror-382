import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class Terminal:
    """The Terminal class is the main entry point for creating a TUI application.
    It manages the terminal size, input handling, rendering of sections and color palette.
    It handles application lifecycle events such as start, resize, update and end."""
    def __init__(self):
        self.h: int = 0
        self.w: int = 0
        self.key: int = -1
        self.root: pr.Section
        self.palette: pr.Palette

        self._no_delay: bool = False
        self._nap_ms: int = 0
        self._wait = lambda: None
        self._running: bool = False


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def run(self, fps: int = 0) -> None:
        """Main loop of the terminal application.
        The fps parameter controls the frame rate of the application.
        If fps is 0, the application runs in no-delay mode, meaning it will not wait between frames.
        If fps is greater than 0, the application will wait for the required number of milliseconds
        between frames to reach the indicated frame rate."""
        self.set_fps(fps)
        try:
            pr._CURRENT_BACKEND._start()
            self._on_start()
            while self._running:
                self._on_resize()
                self._on_update()
            self._on_end()
        finally:
            pr._CURRENT_BACKEND._end()

    # --------------------------------------------------------------------------
    def stop(self) -> None:
        """Stop the terminal application."""
        self._running = False

    # --------------------------------------------------------------------------
    def fetch_key(self) -> int:
        """Fetch the next key from the terminal input.
        This method will block until a key is pressed, unless the terminal is in no-delay mode."""
        self.key = pr._CURRENT_BACKEND._get_key()
        return self.key

    # --------------------------------------------------------------------------
    def exhaust_keys(self) -> None:
        """Exhaust all keys from the terminal input buffer.
        Attention: calling to fetch_key()->prisma._CURRENT_BACKEND._get_key() internally rellies on stdscr.getch(),
        so this method will block the terminal when fps=0 (i.e. outside no-delay mode)."""
        while self.fetch_key() != -1:
            pass


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_fps(self, fps: int) -> None:
        """Set the frames per second (fps) for the terminal application.
        If fps is 0, the application will run in no-delay mode, meaning it will not wait between frames.
        If fps is greater than 0, the application will wait for the required number of milliseconds
        between frames to reach the indicated frame rate."""
        if not fps:
            self._no_delay = False
            self._nap_ms = 0
            self._wait = lambda: None
        else:
            self._no_delay = True
            self._nap_ms = int(1000 / fps)
            self._wait = lambda: pr._CURRENT_BACKEND.sleep(self._nap_ms)

    # --------------------------------------------------------------------------
    def get_size(self) -> tuple[int, int]:
        """Get the current size of the terminal."""
        return self.h, self.w

    # --------------------------------------------------------------------------
    def resize_terminal(self, h: int, w: int) -> None:
        """Resize the terminal to the specified height and width. Might not work in some terminals."""
        print(f"\x1b[8;{h};{w}t")

    # --------------------------------------------------------------------------
    def draw_layer(self, y: int | str, x: int | str, layer: "pr.Layer") -> None:
        """Draw another layer onto the top layer of the root section, at the specified coordinates."""
        self.root.draw_layer(y, x, layer)

    # --------------------------------------------------------------------------
    def draw_text(self,
        y: int | str, x: int | str, string,
        attr: int = None, blend = pr.BlendMode.OVERLAY,
        cut: dict[str, str] = {}
    ) -> None:
        """Draw a string on the top layer of the root section, at the specified coordinates with optional attributes and blending mode."""
        self.root.draw_text(y, x, string, attr, blend, cut)


    # --------------------------------------------------------------------------
    def draw_border(self,
        ls = '│', rs = '│', ts = '─', bs = '─',
        tl = '┌', tr = '┐', bl = '└', br = '┘',
        attr = None, blend = pr.BlendMode.OVERLAY
    ) -> None:
        """Draw a border around the top layer of the root section with specified characters and attribute."""
        self.root.draw_border(ls, rs, ts, bs, tl, tr, bl, br, attr, blend)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def on_start(self) -> None:
        """Called when the terminal application starts.
        This method can be overridden by the user to perform custom initialization."""
        return # overridden by user

    # --------------------------------------------------------------------------
    def on_resize(self) -> None:
        """Called when the terminal is resized.
        This method can be overridden by the user to perform custom actions on resize."""
        return # overridden by user

    # --------------------------------------------------------------------------
    def on_update(self) -> None:
        """Called on each frame update.
        This method can be overridden by the user to perform custom actions on each frame."""
        return # overridden by user

    # --------------------------------------------------------------------------
    def on_end(self) -> None:
        """Called when the terminal application ends.
        This method can be overridden by the user to perform custom cleanup actions."""
        return # overridden by user

    # --------------------------------------------------------------------------
    def should_stop(self) -> bool:
        """Determine whether the terminal application should stop.
        This method can be overridden by the user to implement custom stop conditions.
        By default, it returns False, meaning the application will continue running."""
        return False # overridden by user


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _on_start(self) -> None:
        """Internal method called when the terminal application starts.
        It initializes the terminal size, root section, palette
        and sets the backend to no-delay mode or not, according to the provided fps."""
        self.root = pr.Section()
        self.palette = pr.Palette()
        pr._CURRENT_BACKEND.set_nodelay(self._no_delay)

        self._running = True
        self.on_start()

    # --------------------------------------------------------------------------
    def _on_resize(self) -> None:
        """Internal method called when the terminal is resized."""
        h,w = pr._CURRENT_BACKEND.get_size(update = True)

        if (self.h == h) and (self.w == w): return

        self.h = h; self.w = w
        self.root.update_size()
        pr._CURRENT_BACKEND._resize(self.h, self.w)
        self.on_resize()

    # --------------------------------------------------------------------------
    def _on_update(self) -> None:
        """Internal method called on each frame update.
        It clears the root section, calls the on_update method,
        and renders the current state of the terminal."""
        self.root.clear()
        self.on_update()
        self._render()

        self.key = pr._CURRENT_BACKEND._get_key()
        if self.should_stop(): self.stop()
        self._wait()

    # --------------------------------------------------------------------------
    def _on_end(self) -> None:
        """Internal method called when the terminal application ends."""
        self.on_end()


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _render(self) -> None:
        """Render the current state of the terminal by aggregating all layers
        and writing the rendered data to the terminal backend."""
        master_layer = pr.Layer(self.h, self.w)
        self.root.aggregate_layers(master_layer)

        idx = 0
        for chars,attr in master_layer.yield_render_data():
            y,x = divmod(idx, self.w)
            pr._CURRENT_BACKEND.write_text(y, x, chars, attr)
            idx += len(chars)

        pr._CURRENT_BACKEND._refresh()


# //////////////////////////////////////////////////////////////////////////////
