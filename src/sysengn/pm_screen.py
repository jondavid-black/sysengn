import flet as ft
from sysengn.project_manager import ProjectManager
from sysengn.auth import User


def PMScreen(page: ft.Page, user: User) -> ft.Control:
    """The Project Management Screen component."""

    pm = ProjectManager()

    projects_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    def load_projects():
        projects_column.controls.clear()
        projects = pm.get_all_projects()

        if not projects:
            projects_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.FOLDER_OPEN, size=64, color=ft.Colors.GREY_400
                            ),
                            ft.Text(
                                "No projects yet", size=16, color=ft.Colors.GREY_600
                            ),
                            ft.Text(
                                "Create your first project to get started",
                                size=12,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=40,
                )
            )
        else:
            for project in projects:
                # Format date safely
                date_str = (
                    project.updated_at.strftime("%Y-%m-%d")
                    if project.updated_at
                    else ""
                )

                projects_column.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                project.name,
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    project.status,
                                                    size=10,
                                                    color=ft.Colors.WHITE,
                                                ),
                                                bgcolor=ft.Colors.GREEN
                                                if project.status == "Active"
                                                else ft.Colors.GREY,
                                                padding=ft.padding.symmetric(
                                                    horizontal=8, vertical=2
                                                ),
                                                border_radius=10,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Text(
                                        project.description or "No description",
                                        size=14,
                                        color=ft.Colors.GREY_700,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Container(height=5),
                                    ft.Row(
                                        [
                                            ft.Row(
                                                [
                                                    ft.Icon(
                                                        ft.Icons.ACCESS_TIME,
                                                        size=14,
                                                        color=ft.Colors.GREY_500,
                                                    ),
                                                    ft.Text(
                                                        f"Updated: {date_str}",
                                                        size=12,
                                                        color=ft.Colors.GREY_500,
                                                    ),
                                                ],
                                                spacing=5,
                                            ),
                                            ft.TextButton(
                                                "View Details",
                                                style=ft.ButtonStyle(padding=5),
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                ]
                            ),
                        ),
                        elevation=2,
                    )
                )
        projects_column.update()

    # --- Create Project Dialog ---
    name_field = ft.TextField(label="Project Name", autofocus=True)
    desc_field = ft.TextField(
        label="Description", multiline=True, min_lines=2, max_lines=4
    )

    # We need to define create_dialog first so close_dialog can reference it
    # But create_dialog needs buttons which call functions that might reference create_dialog
    # To break the cycle, we define functions first, then update dialog content/actions if needed,
    # or just use variable reference (which works in python closure).

    create_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Project"),
        content=ft.Column([name_field, desc_field], tight=True, width=400),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dialog(e):
        create_dialog.open = False
        page.update()

    def create_project(e):
        if not name_field.value:
            name_field.error_text = "Name is required"
            name_field.update()
            return

        try:
            pm.create_project(
                name=name_field.value,
                description=desc_field.value or "",
                owner_id=user.id,
            )
            create_dialog.open = False
            page.update()

            # Reset and reload
            name_field.value = ""
            desc_field.value = ""
            name_field.error_text = None

            load_projects()

            page.overlay.append(
                ft.SnackBar(ft.Text("Project created successfully!"), open=True)
            )
            page.update()

        except Exception as ex:
            page.overlay.append(ft.SnackBar(ft.Text(f"Error: {ex}"), open=True))
            page.update()

    # Now set actions
    create_dialog.actions = [
        ft.TextButton("Cancel", on_click=close_dialog),
        ft.ElevatedButton(content=ft.Text("Create"), on_click=create_project),
    ]

    def open_dialog(e):
        page.dialog = create_dialog
        create_dialog.open = True
        page.update()

    # Initial Load
    try:
        load_projects()
    except AssertionError:
        pass  # Expected during test/init if not added to page yet.

    return ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Projects", size=28, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.ADD), ft.Text("New Project")]
                            ),
                            on_click=open_dialog,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                projects_column,
            ],
            expand=True,
        ),
        expand=True,
    )
