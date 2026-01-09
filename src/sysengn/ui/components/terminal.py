import flet as ft
import pyte
from sysengn.core.shell import ShellManager


class TerminalComponent(ft.Container):
    """A terminal component that displays output using pyte for VT100 emulation."""

    # Heuristic character dimensions for monospace font
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 18

    def __init__(self, cols: int = 80, rows: int = 24, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cols = cols
        self.rows = rows

        # Initialize pyte screen and stream
        self.screen = pyte.HistoryScreen(self.cols, self.rows, history=1000)
        self.stream = pyte.Stream(self.screen)

        self.shell: ShellManager | None = None

        # Create columns for history and buffer
        self.history_lines: list[ft.Text] = []
        self.buffer_lines: list[ft.Text] = []

        self.history_column = ft.Column(spacing=0)
        self.buffer_column = ft.Column(spacing=0)

        # Pre-populate buffer lines
        for _ in range(self.rows):
            self.buffer_lines.append(self._create_empty_line())

        self.buffer_column.controls = self.buffer_lines

        self.expand = True
        self.bgcolor = "#1e1e1e"
        self.padding = 5
        self.border_radius = 5

        self.content = ft.Column(
            controls=[self.history_column, self.buffer_column],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # Input handling
        self.focused = False
        self.on_click = self._on_click
        self.border = ft.border.all(2, ft.Colors.TRANSPARENT)

    def _create_empty_line(self) -> ft.Text:
        return ft.Text(
            value="",
            font_family="monospace",
            size=14,
            no_wrap=True,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.TRANSPARENT,
        )

    def did_mount(self) -> None:
        """Called when the control is added to the page."""
        self.shell = ShellManager(on_output=self._on_shell_output)
        if self.page:
            self.page.on_keyboard_event = self._on_key  # type: ignore

    def will_unmount(self) -> None:
        """Called when the control is removed from the page."""
        if self.shell:
            self.shell.close()
        if self.page:
            self.page.on_keyboard_event = None  # type: ignore

    def _on_click(self, e: ft.ControlEvent) -> None:
        """Handle click to focus/unfocus."""
        self.set_focus(not self.focused)

    def set_focus(self, focused: bool) -> None:
        """Set the focus state of the terminal."""
        self.focused = focused
        self.border = ft.border.all(
            2, ft.Colors.BLUE if self.focused else ft.Colors.TRANSPARENT
        )
        self.update()

    def handle_resize(self, width: float, height: float | None = None) -> None:
        """Handle resize events to update terminal dimensions."""
        if not self.shell:
            return

        cols = int(width / self.CHAR_WIDTH)

        # If height is provided, calculate rows, otherwise keep current rows
        if height is not None:
            # Subtract padding (top+bottom) from height before calculating rows
            padding_val: float = 10.0
            if isinstance(self.padding, (int, float)):
                padding_val = float(self.padding) * 2

            available_height = height - padding_val
            rows = int(available_height / self.CHAR_HEIGHT)
        else:
            rows = self.rows

        # Only update if changed
        if cols != self.cols or rows != self.rows:
            self.cols = max(10, cols)  # Minimum width
            self.rows = max(5, rows)  # Minimum height

            self.screen.resize(self.rows, self.cols)
            self.shell.resize(self.rows, self.cols)

            # Rebuild buffer lines
            self.buffer_lines = []
            for _ in range(self.rows):
                self.buffer_lines.append(self._create_empty_line())
            self.buffer_column.controls = self.buffer_lines
            self.buffer_column.update()

            # Clear history lines on resize as it might invalidate line wrapping
            self.history_lines = []
            self.history_column.controls = []
            self.history_column.update()

            # The next update_display will repopulate from screen.history

            self._update_display()

    def _on_key(self, e: ft.KeyboardEvent) -> None:
        """Handle keyboard events."""
        if not self.focused or not self.shell:
            return

        data = self._map_key(e)
        if data:
            self.shell.write(data)

    def _map_key(self, e: ft.KeyboardEvent) -> str:
        """Map Flet key events to ANSI sequences."""
        if e.key == "Enter":
            return "\r"
        elif e.key == "Backspace":
            return "\x7f"
        elif e.key == "Tab":
            return "\t"
        elif e.key == "Escape":
            return "\x1b"
        elif e.key == "Arrow Up":
            return "\x1b[A"
        elif e.key == "Arrow Down":
            return "\x1b[B"
        elif e.key == "Arrow Right":
            return "\x1b[C"
        elif e.key == "Arrow Left":
            return "\x1b[D"
        elif e.key == "Home":
            return "\x1b[H"
        elif e.key == "End":
            return "\x1b[F"
        elif e.key == "Page Up":
            return "\x1b[5~"
        elif e.key == "Page Down":
            return "\x1b[6~"
        elif e.key == "Space" or e.key == " ":
            return " "
        elif e.key == "Delete":
            return "\x1b[3~"

        # Ctrl shortcuts
        if e.ctrl:
            if e.key.upper() == "C":
                return "\x03"
            if e.key.upper() == "D":
                return "\x04"
            if e.key.upper() == "Z":
                return "\x1a"
            if e.key.upper() == "L":
                return "\x0c"
            return ""

        # Normal characters
        if len(e.key) == 1:
            if not e.shift and e.key.isalpha():
                return e.key.lower()
            return e.key

        return ""

    def _on_shell_output(self, text: str) -> None:
        """Callback for shell output."""
        if not self.page:
            return

        async def update_ui() -> None:
            # Feed data to pyte
            self.stream.feed(text)
            self._update_display()

        self.page.run_task(update_ui)

    def _update_display(self) -> None:
        """Update the UI controls based on the current screen buffer and history."""
        # 1. Update History
        # screen.history is a named tuple (top, bottom, ...). top contains scrolled-off lines.
        current_history = list(self.screen.history.top)

        # If history grew, add new lines
        if len(current_history) > len(self.history_lines):
            # Identify new lines
            new_history_data = current_history[len(self.history_lines) :]

            for line_data in new_history_data:
                spans = self._render_line_data(line_data)

                new_line = self._create_empty_line()
                new_line.spans = spans
                new_line.value = None

                self.history_lines.append(new_line)
                self.history_column.controls.append(new_line)

            self.history_column.update()

        # 2. Update Buffer (Active Screen)
        # Iterate over the active buffer rows
        for i in range(self.rows):
            # Get line data from pyte screen buffer
            line_data = self.screen.buffer[i]

            # Render spans
            spans = self._render_line_data(line_data)

            current_line = self.buffer_lines[i]
            old_spans = current_line.spans

            # Optimization: Compare spans to determine if update is needed
            has_changed = False
            if old_spans is None or len(spans) != len(old_spans):
                has_changed = True
            else:
                for s1, s2 in zip(spans, old_spans):
                    c1 = s1.style.color if s1.style else None
                    c2 = s2.style.color if s2.style else None
                    if s1.text != s2.text or c1 != c2:
                        has_changed = True
                        break

            if has_changed:
                current_line.spans = spans
                current_line.value = None

                # Only update individual lines if the line is actually mounted
                if current_line.page:
                    current_line.update()

        # 3. Auto-scroll to bottom
        if isinstance(self.content, ft.Column):
            self.content.scroll_to(offset=float("inf"), duration=0)

    def _render_line_data(self, line) -> list[ft.TextSpan]:
        """Render a single line object (from history or buffer) into TextSpans."""
        spans = []
        # line can be from history (pyte.screens.Line) or buffer (pyte.screens.Line usually)
        # pyte buffer is indexable by column, history lines are also indexable or iterable char objects

        current_text = ""
        current_fg = None

        # We iterate up to self.cols.
        # Note: History lines might have different length if resized, but usually match at creation.
        # Safest to iterate up to the line's length or self.cols

        # pyte Line acts like a dict {col: Char}.
        # But history lines are often stored as specific objects.
        # Let's handle both dictionary-like buffer and potentially different history objects.

        for x in range(self.cols):
            # Direct access to check key existence
            # pyte Line is a dict of {column_index: Char}
            if x in line:
                char = line[x]
            else:
                char = self.screen.default_char

            fg = self._map_color(char.fg)

            # Check if style changed
            if fg != current_fg:
                if current_text:
                    spans.append(
                        ft.TextSpan(
                            text=current_text, style=ft.TextStyle(color=current_fg)
                        )
                    )
                current_text = char.data
                current_fg = fg
            else:
                current_text += char.data

        # Add remaining text
        if current_text:
            spans.append(
                ft.TextSpan(text=current_text, style=ft.TextStyle(color=current_fg))
            )

        return spans

    def _render_line(self, y: int) -> list[ft.TextSpan]:
        """Legacy wrapper - shouldn't be called directly now but keeping for safety."""
        return self._render_line_data(self.screen.buffer[y])

    def _map_color(self, color: str) -> str:
        """Map pyte color names to Flet colors."""
        if color == "default":
            return ft.Colors.WHITE

        color_map = {
            "black": ft.Colors.WHITE,  # Map black to white for visibility on dark bg
            "red": ft.Colors.RED,
            "green": ft.Colors.GREEN,
            "brown": ft.Colors.YELLOW,
            "blue": ft.Colors.BLUE,
            "magenta": ft.Colors.PURPLE,
            "cyan": ft.Colors.CYAN,
            "white": ft.Colors.WHITE,
        }
        return color_map.get(color, ft.Colors.WHITE)
