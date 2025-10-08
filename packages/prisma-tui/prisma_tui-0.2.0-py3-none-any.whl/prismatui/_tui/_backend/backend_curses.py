import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class BackendCurses(pr.Backend):
    def __init__(self):
        self.curses = __import__("curses")

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_nodelay(self, boolean: bool) -> None:
        self.stdscr.nodelay(boolean)

    # --------------------------------------------------------------------------
    def sleep(self, ms: int) -> None:
        self.curses.napms(ms)

    # --------------------------------------------------------------------------
    def write_text(self, y: int, x: int, chars: str, attr: int = 0) -> None:
        try: self.stdscr.addstr(y, x, chars, attr)
        except self.curses.error: pass # ignore out of bounds error

    # --------------------------------------------------------------------------
    def get_size(self, update = False) -> tuple[int,int]:
        if update: self.curses.update_lines_cols()
        return self.curses.LINES, self.curses.COLS


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def supports_color(self) -> bool:
        try: return self.curses.can_change_color()
        except self.curses.error: return False

    # --------------------------------------------------------------------------
    def init_color(self, i: int, r: int, g: int, b: int) -> None:
        try: self.curses.init_color(i, r, g, b)
        except self.curses.error: pass

    # --------------------------------------------------------------------------
    def init_pair(self, i: int, fg: int, bg: int) -> None:
        try: self.curses.init_pair(i, fg, bg)
        except self.curses.error: pass

    # --------------------------------------------------------------------------
    def get_color_pair(self, i: int) -> int:
        try: return self.curses.color_pair(i)
        except self.curses.error: return 0


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _start(self) -> None:
        self.stdscr = self.curses.initscr()
        self.curses.noecho()
        self.curses.cbreak()
        self.stdscr.keypad(1)
        self.curses.curs_set(False)

        try: self.curses.start_color()
        except: pass

    # --------------------------------------------------------------------------
    def _end(self) -> None:
        if "stdscr" not in self.__dict__: return
        self.stdscr.keypad(0)
        self.curses.echo()
        self.curses.nocbreak()
        self.curses.endwin()


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _refresh(self) -> None:
        return # unnecessary, as stdscr.refresh() gets implicitly called by stdscr.getkey()

    # --------------------------------------------------------------------------
    def _get_key(self) -> int:
        return self.stdscr.getch()

    # --------------------------------------------------------------------------
    def _resize(self, h: int, w: int) -> None:
        try: self.stdscr.resize(h, w)
        except self.curses.error: pass


# //////////////////////////////////////////////////////////////////////////////
