import re
import flet as ft
from sysengn.core.shell import ShellManager


# Basic ANSI color map
ANSI_COLORS = {
    # Standard
    "30": ft.Colors.BLACK,
    "31": ft.Colors.RED,
    "32": ft.Colors.GREEN,
    "33": ft.Colors.YELLOW,
    "34": ft.Colors.BLUE,
    "35": ft.Colors.PURPLE,
    "36": ft.Colors.CYAN,
    "37": ft.Colors.WHITE,
    # Bright
    "90": ft.Colors.GREY_700,
    "91": ft.Colors.RED_ACCENT,
    "92": ft.Colors.GREEN_ACCENT,
    "93": ft.Colors.YELLOW_ACCENT,
    "94": ft.Colors.BLUE_ACCENT,
    "95": ft.Colors.PURPLE_ACCENT,
    "96": ft.Colors.CYAN_ACCENT,
    "97": ft.Colors.WHITE,
}


class TerminalComponent(ft.Container):
    """A terminal component that displays output and accepts input via a persistent shell."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell: ShellManager | None = None
        self.output_control = ft.ListView(
            expand=True,
            spacing=0,  # Tight spacing
            auto_scroll=True,
        )
        self.input_control = ft.TextField(
            text_style=ft.TextStyle(font_family="monospace", size=14),
            on_submit=self._on_command_submit,
            border=ft.InputBorder.NONE,
            bgcolor=ft.Colors.TRANSPARENT,
            cursor_color=ft.Colors.GREEN,
            expand=True,
            height=20,
            content_padding=0,
            autofocus=True,
            show_cursor=True,
        )

        self.expand = True
        self.bgcolor = "#1e1e1e"  # Unified dark background
        self.padding = 0
        self.border_radius = 5

        self.content = ft.Container(
            padding=10,
            on_click=lambda _: self.input_control.focus(),  # Click anywhere to focus
            content=ft.Column(
                controls=[
                    self.output_control,
                    ft.Row(
                        controls=[
                            # Minimal prompt indicator or just input
                            # We'll rely on shell prompt in output, but provide a
                            # visual cue for where typing happens
                            ft.Text(
                                "$",
                                font_family="monospace",
                                color=ft.Colors.GREEN,
                                size=14,
                            ),
                            ft.Container(width=5),  # Spacer
                            self.input_control,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
        )

    def did_mount(self) -> None:
        """Called when the control is added to the page."""
        self.shell = ShellManager(on_output=self._on_shell_output)
        self.input_control.focus()

    def will_unmount(self) -> None:
        """Called when the control is removed from the page."""
        if self.shell:
            self.shell.close()

    def _parse_ansi(self, text: str) -> list[ft.TextSpan]:
        """Parses ANSI escape codes and returns a list of TextSpans."""
        spans = []
        # Split by ANSI escape codes
        parts = re.split(r"(\x1b\[[0-9;]*m)", text)

        current_color = None
        current_weight = None  # For bold (1)

        for part in parts:
            if not part:
                continue

            if part.startswith("\x1b["):
                # Parse code
                code_content = part[2:-1]  # Remove \x1b[ and m
                codes = code_content.split(";")

                for code in codes:
                    if code == "0" or code == "":  # Reset
                        current_color = None
                        current_weight = None
                    elif code == "1":  # Bold
                        current_weight = ft.FontWeight.BOLD
                    elif code in ANSI_COLORS:
                        current_color = ANSI_COLORS[code]
                    elif code == "39":  # Default
                        current_color = None
            else:
                # Regular text
                spans.append(
                    ft.TextSpan(
                        text=part,
                        style=ft.TextStyle(
                            color=current_color,
                            weight=current_weight,
                            font_family="monospace",
                        ),
                    )
                )

        return spans

    def _on_shell_output(self, text: str) -> None:
        """Callback for shell output."""
        if not self.page:
            return

        async def update_ui() -> None:
            # Parse text into spans
            spans = self._parse_ansi(text)

            # Append new text
            self.output_control.controls.append(
                ft.Text(
                    spans=spans,
                    font_family="monospace",
                    selectable=True,
                )
            )
            # Prune old lines
            if len(self.output_control.controls) > 1000:
                self.output_control.controls = self.output_control.controls[-1000:]

            self.output_control.update()

        self.page.run_task(update_ui)

    def _on_command_submit(self, e: ft.ControlEvent) -> None:
        """Handles command submission."""
        command = self.input_control.value
        if not command:
            return

        if self.shell:
            self.shell.write(command)

        self.input_control.value = ""
        self.input_control.focus()
        self.input_control.update()
