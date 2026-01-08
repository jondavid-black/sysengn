import flet as ft
from sysengn.core.auth import User


def UXScreen(page: ft.Page, user: User) -> ft.Control:
    """The User Experience (UX) Screen component."""

    # Placeholder data for Wireframes
    wireframes = [
        {"name": "Dashboard_v1", "updated": "2 hours ago"},
        {"name": "Login_Flow", "updated": "1 day ago"},
        {"name": "Project_Settings", "updated": "3 days ago"},
    ]

    return ft.Container(
        content=ft.Row(
            controls=[
                # Side Rail
                ft.NavigationRail(
                    selected_index=0,
                    label_type=ft.NavigationRailLabelType.NONE,
                    min_width=50,
                    min_extended_width=150,
                    group_alignment=-0.9,
                    destinations=[
                        ft.NavigationRailDestination(
                            icon=ft.Icons.DASHBOARD_CUSTOMIZE,
                            selected_icon=ft.Icons.DASHBOARD,
                            label="Wireframes",
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.Icons.PALETTE_OUTLINED,
                            selected_icon=ft.Icons.PALETTE,
                            label="Design System",
                        ),
                        ft.NavigationRailDestination(
                            icon=ft.Icons.PERSON_SEARCH,
                            selected_icon=ft.Icons.PERSON_SEARCH,
                            label="User Research",
                        ),
                    ],
                    bgcolor=ft.Colors.GREY_900,
                ),
                # Main Content
                ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "UX Design",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.PURPLE_200,
                            ),
                            ft.Divider(),
                            ft.Text(
                                "Recent Wireframes", size=20, weight=ft.FontWeight.W_500
                            ),
                            ft.GridView(
                                expand=True,
                                runs_count=5,
                                max_extent=200,
                                child_aspect_ratio=1.0,
                                spacing=10,
                                run_spacing=10,
                                controls=[
                                    ft.Container(
                                        bgcolor=ft.Colors.GREY_800,
                                        padding=10,
                                        border_radius=10,
                                        content=ft.Column(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.IMAGE,
                                                    size=40,
                                                    color=ft.Colors.GREY_500,
                                                ),
                                                ft.Text(
                                                    w["name"], weight=ft.FontWeight.BOLD
                                                ),
                                                ft.Text(
                                                    w["updated"],
                                                    size=12,
                                                    color=ft.Colors.GREY_500,
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    )
                                    for w in wireframes
                                ]
                                + [
                                    ft.Container(
                                        bgcolor=ft.Colors.GREY_800,
                                        padding=10,
                                        border_radius=10,
                                        border=ft.border.all(1, ft.Colors.GREY_700),
                                        content=ft.Column(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.ADD,
                                                    size=40,
                                                    color=ft.Colors.PURPLE_300,
                                                ),
                                                ft.Text(
                                                    "New Wireframe",
                                                    color=ft.Colors.PURPLE_300,
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    )
                                ],
                            ),
                        ],
                        expand=True,
                    ),
                ),
            ],
            expand=True,
        ),
        expand=True,
    )
