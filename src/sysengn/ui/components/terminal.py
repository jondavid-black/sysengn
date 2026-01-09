import flet as ft
import pyte
from sysengn.core.shell import ShellManager


class TerminalComponent(ft.Container):
    """A terminal component that displays output using pyte for VT100 emulation."""

    # Heuristic character dimensions for monospace font
    CHAR_WIDTH = 8.5
    CHAR_HEIGHT = 18

    def __init__(self, cols: int = 80, rows: int = 24, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cols = cols
        self.rows = rows

        # Initialize pyte screen and stream
        self.screen = pyte.Screen(self.cols, self.rows)
        self.stream = pyte.Stream(self.screen)

        self.shell: ShellManager | None = None

        # Create text controls for each row
        self.terminal_lines = []
        for _ in range(self.rows):
            self.terminal_lines.append(
                ft.Text(
                    value="",
                    font_family="monospace",
                    size=14,
                    no_wrap=True,
                    color=ft.Colors.WHITE,
                )
            )

        self.expand = True
        self.bgcolor = "#1e1e1e"
        self.padding = 10
        self.border_radius = 5

        self.content = ft.Column(
            controls=self.terminal_lines,
            spacing=0,
            expand=True,
        )

        # Input handling
        self.focused = False
        self.on_click = self._on_click
        self.border = ft.border.all(2, ft.Colors.TRANSPARENT)

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
        # For now, we mainly resize width via the side panel
        # But we could also calculate rows if we knew the container height
        if height is not None:
            rows = int(height / self.CHAR_HEIGHT)
        else:
            # Fallback or keep current.
            # Ideally we should use the height of the container if possible.
            # But the side panel currently only resizes width.
            # So we'll stick with current rows unless we get a height update.
            rows = self.rows

        # Only update if changed
        if cols != self.cols or rows != self.rows:
            self.cols = max(10, cols)  # Minimum width
            self.rows = max(5, rows)  # Minimum height

            self.screen.resize(self.rows, self.cols)
            self.shell.resize(self.rows, self.cols)

            # Recreate lines if rows changed
            if len(self.terminal_lines) != self.rows:
                self.terminal_lines.clear()
                for _ in range(self.rows):
                    self.terminal_lines.append(
                        ft.Text(
                            value="",
                            font_family="monospace",
                            size=14,
                            no_wrap=True,
                            color=ft.Colors.WHITE,
                        )
                    )
                # Update content column
                if isinstance(self.content, ft.Column):
                    self.content.controls = self.terminal_lines
                    self.content.update()

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
        """Update the UI controls based on the current screen buffer."""
        for y in range(self.rows):
            if y < len(self.terminal_lines):
                spans = self._render_line(y)
                self.terminal_lines[y].spans = spans
                self.terminal_lines[y].value = None  # Clear value when using spans
                self.terminal_lines[y].update()

    def _render_line(self, y: int) -> list[ft.TextSpan]:
        """Render a single line from the pyte buffer into TextSpans."""
        spans = []
        line = self.screen.buffer[y]

        current_text = ""
        current_fg = None

        # Iterate through columns
        for x in range(self.cols):
            char = line.get(x, self.screen.default_char)
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
