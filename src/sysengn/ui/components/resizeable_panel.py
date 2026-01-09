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
    ):
        super().__init__()
        self.content_control = content
        self.current_width = initial_width
        self.min_width = min_width
        self.max_width = max_width
        self.visible = visible

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
        self.content_container = ft.Container(
            content=self.content_control,
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

    def toggle(self) -> None:
        """Toggle the visibility of the panel."""
        self.visible = not self.visible
        self.update()
