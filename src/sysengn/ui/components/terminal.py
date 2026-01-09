import flet as ft
from sysengn.core.shell import ShellManager


class TerminalComponent(ft.Container):
    """A terminal component that displays output and accepts input via a persistent shell."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell: ShellManager | None = None
        self.output_control = ft.ListView(
            expand=True,
            spacing=2,
            auto_scroll=True,
        )
        self.input_control = ft.TextField(
            hint_text="Type command...",
            text_style=ft.TextStyle(font_family="monospace"),
            on_submit=self._on_command_submit,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.GREY_900,
            expand=True,
            height=40,
            content_padding=10,
        )

        self.expand = True
        self.bgcolor = ft.Colors.BLACK
        self.padding = 5
        self.border_radius = 5

        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=self.output_control,
                    expand=True,
                    bgcolor="#1e1e1e",  # Dark background
                    padding=10,
                    border_radius=5,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                ">", font_family="monospace", weight=ft.FontWeight.BOLD
                            ),
                            self.input_control,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor="#2d2d2d",  # Slightly lighter for input area
                    padding=ft.padding.only(left=10, right=10),
                    border_radius=5,
                ),
            ],
            spacing=5,
            expand=True,
        )

    def did_mount(self) -> None:
        """Called when the control is added to the page."""
        self.shell = ShellManager(on_output=self._on_shell_output)

    def will_unmount(self) -> None:
        """Called when the control is removed from the page."""
        if self.shell:
            self.shell.close()

    def _on_shell_output(self, text: str) -> None:
        """Callback for shell output."""
        if not self.page:
            return

        async def update_ui() -> None:
            # Append new text
            self.output_control.controls.append(
                ft.Text(
                    text,
                    font_family="monospace",
                    selectable=True,
                    spans=[ft.TextSpan(text)],
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
