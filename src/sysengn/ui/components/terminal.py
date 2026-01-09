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

    def did_mount(self) -> None:
        """Called when the control is added to the page."""
        self.shell = ShellManager(on_output=self._on_shell_output)
        # Note: Input handling is deferred to a future task.

    def will_unmount(self) -> None:
        """Called when the control is removed from the page."""
        if self.shell:
            self.shell.close()

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
