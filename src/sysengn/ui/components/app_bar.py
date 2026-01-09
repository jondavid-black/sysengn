from typing import Callable
import flet as ft

from sysengn.core.auth import (
    User,
    Role,
    update_user_theme_preference,
)
from sysengn.core.project_manager import ProjectManager
from sysengn.ui.components.terminal import TerminalComponent


class SysEngnAppBar(ft.Container):
    """The main application bar component for SysEngn.

    This component provides navigation tabs, user profile access, project selection,
    and global actions like theme toggling and search.

    Attributes:
        page_ref (ft.Page): Reference to the main Flet page.
        user (User): The currently logged-in user.
        on_tab_change (Callable[[int], None]): Callback triggered when switching tabs.
        tabs_list (list[str]): List of tab names to display.
        on_logout (Callable[[], None]): Callback triggered on logout.
        on_profile (Callable[[], None]): Callback triggered to view profile.
        on_admin (Callable[[], None] | None): Callback triggered to view admin panel.
        logo_path (str): Path to the application logo image.
    """

    def __init__(
        self,
        page: ft.Page,
        user: User,
        logo_path: str,
        on_tab_change: Callable[[int], None],
        tabs: list[str],
        on_logout: Callable[[], None],
        on_profile: Callable[[], None],
        on_admin: Callable[[], None] | None = None,
    ):
        """Initialize the application bar.

        Args:
            page: Reference to the main Flet page.
            user: The currently logged-in user model.
            logo_path: Path to the logo image asset.
            on_tab_change: Function to call when a tab is clicked.
            tabs: List of strings representing tab labels.
            on_logout: Function to call when logout is requested.
            on_profile: Function to call when profile is requested.
            on_admin: Optional function to call when admin panel is requested.
        """
        super().__init__()
        self.page_ref = page
        self.user = user
        self.on_tab_change = on_tab_change
        self.tabs_list = tabs
        self.on_logout = on_logout
        self.on_profile = on_profile
        self.on_admin = on_admin
        self.logo_path = logo_path

        # Exposed controls
        self.tabs_control = self._build_tabs()
        self.avatar_control = self._build_avatar()

        # Build the UI
        self._build_content()

    def _build_tabs(self) -> ft.Tabs:
        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            indicator_color=ft.Colors.BLUE_200,
            label_color=ft.Colors.BLUE_200,
            unselected_label_color=ft.Colors.GREY_400,
            divider_color="transparent",
            tabs=[ft.Tab(text=name) for name in self.tabs_list],
            on_change=lambda e: self.on_tab_change(e.control.selected_index),
        )

    def _build_avatar(self) -> ft.CircleAvatar:
        user_initials = (
            self.user.name[0].upper() if self.user.name else self.user.email[0].upper()
        )

        # If user has first and last name, show those initials
        if self.user.first_name and self.user.last_name:
            user_initials = (
                f"{self.user.first_name[0].upper()}{self.user.last_name[0].upper()}"
            )

        return ft.CircleAvatar(
            content=ft.Text(user_initials, color=ft.Colors.WHITE),
            bgcolor=self.user.preferred_color
            if self.user.preferred_color
            else ft.Colors.BLUE,
            tooltip=f"{self.user.name or self.user.email}",
        )

    def _build_project_dropdown(self) -> ft.Dropdown:
        pm = ProjectManager()
        projects = pm.get_all_projects()

        project_options = [ft.dropdown.Option(key=p.id, text=p.name) for p in projects]

        # Set default active project to first available, or empty if none
        initial_project_id = projects[0].id if projects else None

        # Only override session if not already set or invalid
        current_session_project = self.page_ref.session.get("current_project_id")
        if not current_session_project and initial_project_id:
            self.page_ref.session.set("current_project_id", initial_project_id)
        elif current_session_project:
            # Validate it still exists
            if not any(p.id == current_session_project for p in projects):
                self.page_ref.session.set("current_project_id", initial_project_id)

        # Get final effective project ID
        active_project_id = self.page_ref.session.get("current_project_id")

        def on_project_change(e):
            selected_id = e.control.value
            if selected_id:
                self.page_ref.session.set("current_project_id", selected_id)
                # Refresh current view if it depends on project
                # We can trigger tab change to reload current tab or just notify
                # For now, let's just update the banner dropdown
                project_dropdown.update()

                # If currently on MBSE screen (index 1), we might want to refresh content area
                # A simple way is to re-trigger on_tab_change with current index
                # We assume MBSE is index 1 based on default tabs, but we should be careful.
                # Ideally the parent handles this via on_project_changed callback, but for now we follow existing logic.
                current_tab_idx = self.tabs_control.selected_index
                # Assuming standard tabs: Home, MBSE, UX, Docs
                # If "MBSE" is in tabs list and selected
                if (
                    current_tab_idx < len(self.tabs_list)
                    and self.tabs_list[current_tab_idx] == "MBSE"
                ):
                    self.on_tab_change(current_tab_idx)

        project_dropdown = ft.Dropdown(
            width=200,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
            # Default to active project
            value=active_project_id,
            options=project_options,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            border_radius=5,
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Select Active Project",
            on_change=on_project_change,
        )
        return project_dropdown

    def _toggle_theme(self, e):
        new_mode = (
            ft.ThemeMode.LIGHT
            if self.page_ref.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        self.page_ref.theme_mode = new_mode
        e.control.icon = (
            ft.Icons.DARK_MODE
            if self.page_ref.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE
        )
        self.page_ref.update()

        # Update preference in DB and session
        self.user.theme_preference = (
            "LIGHT" if new_mode == ft.ThemeMode.LIGHT else "DARK"
        )
        update_user_theme_preference(self.user.id, self.user.theme_preference)

    def _open_terminal(self, e):
        # Create Terminal Component
        # We don't set height so it can expand to fill the drawer
        term = TerminalComponent()

        # Use NavigationDrawer for the terminal (Left Drawer)
        drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(
                    content=term,
                    expand=True,
                    padding=0,
                    bgcolor=ft.Colors.BLACK,
                )
            ],
            bgcolor=ft.Colors.BLACK,
            surface_tint_color=ft.Colors.BLACK,
        )

        # Assign drawer to page and open it
        self.page_ref.drawer = drawer
        self.page_ref.drawer.open = True
        self.page_ref.update()

    def _build_content(self):
        # Left: Icon, Name, Project Dropdown, Workspace Dropdown
        project_dropdown = self._build_project_dropdown()

        workspace_dropdown = ft.Dropdown(
            width=200,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
            value="main",
            options=[
                ft.dropdown.Option("main"),
                ft.dropdown.Option("dev"),
                ft.dropdown.Option("test"),
                ft.dropdown.Option("+ Add New Workspace"),
            ],
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            border_radius=5,
        )

        left_section = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Image(
                        src=self.logo_path,
                        width=55,
                        height=45,
                        tooltip="Go to Home",
                    ),
                    on_click=lambda _: self.on_tab_change(0),
                ),
                ft.Container(width=10),
                project_dropdown,
                ft.Container(width=10),
                workspace_dropdown,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Right: Search, Theme Toggle, Avatar
        search_box = ft.TextField(
            hint_text="Search...",
            height=40,
            text_size=14,
            content_padding=ft.padding.only(left=10, bottom=10),
            width=200,
            border_radius=20,
            prefix_icon=ft.Icons.SEARCH,
            bgcolor=ft.Colors.GREY_800,
            border_color=ft.Colors.TRANSPARENT,
            color=ft.Colors.WHITE,
            hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
        )

        theme_icon = ft.IconButton(
            ft.Icons.DARK_MODE
            if self.page_ref.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE,
            on_click=self._toggle_theme,
            tooltip="Toggle Dark Mode",
            icon_color=ft.Colors.GREY_400,
        )

        # Avatar Menu (Logout, Admin)
        menu_items = [
            ft.PopupMenuItem(
                text="Profile",
                icon=ft.Icons.PERSON,
                on_click=lambda e: self.on_profile(),
            )
        ]

        if self.user.has_role(Role.ADMIN) and self.on_admin:
            menu_items.append(
                ft.PopupMenuItem(
                    text="Admin Panel",
                    icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                    on_click=lambda e: self.on_admin(),  # type: ignore
                )
            )

        menu_items.append(
            ft.PopupMenuItem(
                text="Logout",
                icon=ft.Icons.LOGOUT,
                on_click=lambda e: self.on_logout(),
            )
        )

        terminal_icon = ft.IconButton(
            ft.Icons.TERMINAL,
            on_click=self._open_terminal,
            tooltip="Open Terminal",
            icon_color=ft.Colors.GREY_400,
        )

        avatar_menu = ft.PopupMenuButton(
            content=self.avatar_control,
            items=menu_items,
        )

        right_section = ft.Row(
            controls=[
                search_box,
                ft.Container(width=10),
                terminal_icon,
                ft.Container(width=5),
                theme_icon,
                ft.Container(width=10),
                avatar_menu,
            ],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        banner_row = ft.Row(
            controls=[left_section, self.tabs_control, right_section],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

        self.content = banner_row
        self.padding = ft.padding.symmetric(horizontal=20, vertical=10)
        self.bgcolor = "#36454F"  # Charcoal
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 2),
        )
