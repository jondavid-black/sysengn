import flet as ft
from sysengn.core.auth import User, update_user_profile


def UserProfileScreen(page: ft.Page, user: User, on_back, on_save=None) -> ft.Container:
    """Screen for editing user profile."""

    first_name_field = ft.TextField(
        label="First Name",
        value=user.first_name or "",
        width=300,
    )
    last_name_field = ft.TextField(
        label="Last Name",
        value=user.last_name or "",
        width=300,
    )

    # Color options
    color_options = [
        ft.Colors.BLUE,
        ft.Colors.RED,
        ft.Colors.GREEN,
        ft.Colors.ORANGE,
        ft.Colors.PURPLE,
        ft.Colors.TEAL,
        ft.Colors.PINK,
        ft.Colors.CYAN,
    ]

    selected_color = user.preferred_color or ft.Colors.BLUE

    # We need a way to select color. A dropdown or a set of clickable containers.
    # Let's use a Dropdown for simplicity first, or a Row of circles. Row of circles is nicer.

    color_selection = ft.Ref[ft.Row]()

    def on_color_click(e):
        nonlocal selected_color
        clicked_color = e.control.data
        selected_color = clicked_color
        # Update UI to show selection
        for control in color_selection.current.controls:
            if isinstance(control, ft.Container):
                if control.data == selected_color:
                    control.border = ft.border.all(2, ft.Colors.WHITE)
                else:
                    control.border = None
        color_selection.current.update()

    color_controls = []
    for color in color_options:
        is_selected = color == selected_color
        color_controls.append(
            ft.Container(
                width=30,
                height=30,
                bgcolor=color,
                border_radius=15,
                border=ft.border.all(2, ft.Colors.WHITE) if is_selected else None,
                on_click=on_color_click,
                data=color,
                tooltip=color,
            )
        )

    def save_profile(e):
        user.first_name = first_name_field.value
        user.last_name = last_name_field.value
        user.preferred_color = selected_color

        # Update Name for display if full name is constructed from parts
        if user.first_name and user.last_name:
            user.name = f"{user.first_name} {user.last_name}"

        update_user_profile(
            user.id, user.first_name, user.last_name, user.preferred_color
        )

        page.snack_bar = ft.SnackBar(ft.Text("Profile updated successfully!"))
        page.snack_bar.open = True
        page.update()
        if on_save:
            on_save()
        on_back()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("User Profile", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                first_name_field,
                last_name_field,
                ft.Text("Preferred Color:", size=16),
                ft.Row(controls=color_controls, ref=color_selection),
                ft.Divider(height=20),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Save", on_click=save_profile),
                        ft.OutlinedButton("Cancel", on_click=lambda _: on_back()),
                    ]
                ),
            ],
            spacing=20,
        ),
        padding=40,
        alignment=ft.alignment.center,
        width=500,  # Constrain width for better look
    )
