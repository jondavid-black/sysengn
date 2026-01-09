import flet as ft
import pyte
from sysengn.core.shell import ShellManager


class TerminalComponent(ft.Container):
    """A terminal component that displays output using pyte for VT100 emulation."""

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
            return e.key

        return ""

    def _on_shell_output(self, text: str) -> None:
        """Callback for shell output."""
        if not self.page:
            return

        async def update_ui() -> None:
            # Feed data to pyte
            self.stream.feed(text)

            # Update the display
            # We use screen.display for plain text rendering for now,
            # as it's significantly faster and simpler for the first pass.
            display_lines = self.screen.display

            for i, line_content in enumerate(display_lines):
                if i < len(self.terminal_lines):
                    # Replace spaces with non-breaking spaces to preserve formatting if needed,
                    # but monospace font usually handles standard spaces fine.
                    # However, Flet/Flutter sometimes trims trailing spaces or collapses them?
                    # Let's trust monospace for now.
                    self.terminal_lines[i].value = line_content
                    self.terminal_lines[i].update()

        self.page.run_task(update_ui)
