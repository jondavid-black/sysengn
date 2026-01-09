from collections.abc import Callable

import flet as ft


class ResizeableSidePanel(ft.Row):
    """
    A generic side panel that sits on the right side of the screen
    and can be resized by dragging its left edge.
    """

    def __init__(
        self,
        content: ft.Control,
        initial_width: float = 400,
        min_width: float = 200,
        max_width: float = 800,
        visible: bool = False,
        on_resize: Callable[[float], None] | None = None,
    ):
        super().__init__()
        self.content_control = content
        self.current_width = initial_width
        self.min_width = min_width
        self.max_width = max_width
        self.visible = visible
        self.on_resize = on_resize

        # Layout configuration
        self.spacing = 0
        self.vertical_alignment = ft.CrossAxisAlignment.STRETCH
        self.alignment = ft.MainAxisAlignment.END

        # The drag handle
        self.resize_handle = ft.GestureDetector(
            content=ft.Container(
                width=5,
                bgcolor=ft.Colors.GREY_800,
                tooltip="Drag to resize",
            ),
            mouse_cursor=ft.MouseCursor.RESIZE_COLUMN,
            on_pan_update=self._on_pan_update,
        )

        # The content container
        # Header with close button
        close_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=20,
            tooltip="Close Panel",
            on_click=lambda _: self.toggle(),
            icon_color=ft.Colors.WHITE,
        )

        header_row = ft.Row(
            controls=[ft.Container(expand=True), close_button],
            alignment=ft.MainAxisAlignment.END,
        )

        self.inner_column = ft.Column(
            controls=[
                header_row,
                ft.Container(content=self.content_control, expand=True),
            ],
            spacing=0,
            expand=True,
        )

        self.content_container = ft.Container(
            content=self.inner_column,
            width=self.current_width,
            bgcolor="#1e1e1e",  # Matches TerminalComponent background
            expand=True,  # Allow vertical expansion
        )

        self.controls = [self.resize_handle, self.content_container]

    def _on_pan_update(self, e: ft.DragUpdateEvent) -> None:
        """Handle drag events to resize the panel."""
        # Since panel is on the right, dragging left (negative dx) increases width
        self.current_width -= e.delta_x

        # Clamp values
        if self.current_width < self.min_width:
            self.current_width = self.min_width
        elif self.current_width > self.max_width:
            self.current_width = self.max_width

        self.content_container.width = self.current_width
        self.content_container.update()

        if self.on_resize:
            self.on_resize(self.current_width)

    def toggle(self) -> None:
        """Toggle the visibility of the panel."""
        self.visible = not self.visible
        self.update()
