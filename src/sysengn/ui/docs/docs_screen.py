import flet as ft
from sysengn.core.auth import User
from typing import Any


class DocsScreen(ft.Container):
    """A screen for displaying documentation with a side rail and drawer."""

    def __init__(self, page: ft.Page, user: User):
        super().__init__()
        self.page_ref = page
        self.user = user
        self.expand = True

        # State for selection and drag-drop
        self.selected_node_id: str | None = None

        # Mock Data for Docs Tree
        self.docs_data = [
            {
                "id": "doc1",
                "title": "Project Specification",
                "type": "document",
                "children": [
                    {
                        "id": "sec1",
                        "title": "1. Introduction",
                        "type": "section",
                        "children": [],
                    },
                    {
                        "id": "sec2",
                        "title": "2. Scope",
                        "type": "section",
                        "children": [
                            {
                                "id": "subsec1",
                                "title": "2.1 In Scope",
                                "type": "section",
                                "children": [],
                            }
                        ],
                    },
                ],
            },
            {"id": "doc2", "title": "User Manual", "type": "document", "children": []},
        ]

        # Initial Drawer Content (Outline)
        self.drawer_content = self._build_outline_view()

        # We need a reference to the drawer content container to update it
        self.drawer_container_ref = ft.Ref[ft.Container]()

        # Side Rail
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.NONE,
            min_width=50,
            min_extended_width=150,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.FORMAT_LIST_BULLETED,
                    selected_icon=ft.Icons.FORMAT_LIST_BULLETED,
                    label="Outline",
                    padding=ft.padding.symmetric(vertical=10),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER,
                    selected_icon=ft.Icons.FOLDER_OPEN,
                    label="File System",
                    padding=ft.padding.symmetric(vertical=10),
                ),
            ],
            on_change=self.on_rail_change,
            bgcolor=ft.Colors.GREY_900,
        )

        # Drawer Container
        drawer = ft.Container(
            ref=self.drawer_container_ref,
            content=self.drawer_content,
            width=300,  # Increased width for tree
            bgcolor=ft.Colors.GREY_800,
            padding=10,
            border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_700)),
        )

        # Main Content Area
        main_content = ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Documentation",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_200,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Divider(color=ft.Colors.GREY_800),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.LIBRARY_BOOKS,
                                    size=64,
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    "Documentation Module",
                                    size=20,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Text(
                                    "Manage and view project documentation here.",
                                    color=ft.Colors.GREY_400,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        padding=50,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ],
                expand=True,
                spacing=20,
            ),
            expand=True,
        )

        # Layout: Rail | Drawer | Main Content
        self.content = ft.Row(
            controls=[
                rail,
                drawer,
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_700),
                main_content,
            ],
            expand=True,
            spacing=0,
        )

    def _build_outline_view(self) -> ft.Control:
        """Builds the outline view with 'New' button and Tree."""

        def create_new(e):
            # Create a new document node
            import uuid

            new_id = f"doc_{uuid.uuid4().hex[:8]}"
            new_node = {
                "id": new_id,
                "title": "New Document",
                "type": "document",
                "children": [],
            }
            self.docs_data.append(new_node)
            self._refresh_tree()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Outline", weight=ft.FontWeight.BOLD, size=16),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            tooltip="New Document",
                            icon_size=20,
                            on_click=create_new,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_700),
                ft.Container(
                    content=ft.Column(
                        controls=self._build_tree_nodes(self.docs_data),
                        scroll=ft.ScrollMode.AUTO,
                        spacing=0,  # Remove spacing to allow separators to sit tight
                    ),
                    expand=True,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def _refresh_tree(self):
        """Rebuilds the outline view and updates the drawer."""
        if self.drawer_container_ref.current:
            self.drawer_container_ref.current.content = self._build_outline_view()
            self.drawer_container_ref.current.update()

    def _build_tree_nodes(
        self,
        nodes: list[dict[str, Any]],
        level: int = 0,
        parent_id: str | None = None,
    ) -> list[ft.Control]:
        """Recursively builds tree nodes with inter-node separators."""
        controls = []

        for i, node in enumerate(nodes):
            # 1. Separator (Drop Target for "Insert Before")
            controls.append(self._build_separator_target(parent_id, i, level))

            # 2. Node Item (Drop Target for "Nest Inside")
            controls.append(self._build_node_item(node, level))

            # 3. Children
            if node.get("children"):
                controls.extend(
                    self._build_tree_nodes(node["children"], level + 1, node["id"])
                )

        # 4. Final Separator (Drop Target for "Append to end")
        controls.append(self._build_separator_target(parent_id, len(nodes), level))

        return controls

    def _build_separator_target(
        self, parent_id: str | None, index: int, level: int
    ) -> ft.Control:
        """Creates a drop target for placing items between nodes with larger hit area."""

        # The visual line (initially hidden/transparent)
        visual_line = ft.Container(
            height=2,
            bgcolor=ft.Colors.TRANSPARENT,
            border_radius=1,
            expand=True,
        )

        # The hit area container (taller)
        hit_area = ft.Container(
            content=ft.Column(
                controls=[visual_line], alignment=ft.MainAxisAlignment.CENTER
            ),
            height=14,  # Larger hit area
            bgcolor=ft.Colors.TRANSPARENT,
            margin=ft.margin.only(left=level * 20),
        )

        def on_will_accept(e):
            # Show the visual line
            visual_line.bgcolor = ft.Colors.BLUE_400
            visual_line.height = 4
            visual_line.update()

        def on_leave(e):
            # Hide the visual line
            visual_line.bgcolor = ft.Colors.TRANSPARENT
            visual_line.height = 2
            visual_line.update()

        def on_accept(e):
            # Retrieve source ID reliably
            # Try e.data first (passed from client)
            src_id = e.data

            # Handle Flet serialization (sometimes adds quotes)
            if src_id and isinstance(src_id, str):
                if len(src_id) > 1 and src_id.startswith('"') and src_id.endswith('"'):
                    src_id = src_id[1:-1]

            # Fallback to control lookup if data is missing
            if not src_id and e.src_id:
                src_control = self.page_ref.get_control(e.src_id)
                if src_control:
                    src_id = src_control.data

            # Clear highlight immediately
            on_leave(None)

            if src_id:
                # print(f"Drag accepted: {src_id} -> Parent {parent_id} index {index}")
                self._handle_reorder(str(src_id), parent_id, index)

        return ft.DragTarget(
            group="doc_node",
            content=hit_area,
            on_will_accept=on_will_accept,
            on_leave=on_leave,
            on_accept=on_accept,
        )

    def _build_node_item(self, node: dict[str, Any], level: int) -> ft.Control:
        """Creates the draggable node item with nesting drop target."""
        is_selected = self.selected_node_id == node["id"]

        # The visual content of the node
        node_content = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.ARTICLE
                        if node["type"] == "document"
                        else ft.Icons.SUBDIRECTORY_ARROW_RIGHT,
                        size=16,
                        color=ft.Colors.BLUE_200
                        if node["type"] == "document"
                        else ft.Colors.GREY_400,
                    ),
                    ft.Text(
                        node["title"],
                        size=14,
                        weight=ft.FontWeight.W_500
                        if node["type"] == "document"
                        else ft.FontWeight.NORMAL,
                        expand=True,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        color=ft.Colors.WHITE if is_selected else None,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Delete",
                        on_click=lambda e, n=node: self._delete_node(n),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=ft.padding.symmetric(horizontal=5, vertical=4),
            bgcolor=ft.Colors.BLUE_900 if is_selected else ft.Colors.TRANSPARENT,
            border_radius=5,
            on_click=lambda e, n=node: self._select_node(n),
            data=node,
        )

        # Drag Feedback (Improved: Smaller, Transparent)
        feedback = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.DRAG_HANDLE, size=14, color=ft.Colors.WHITE70),
                    ft.Text(
                        node["title"],
                        size=12,
                        color=ft.Colors.WHITE,
                        no_wrap=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=5,
            ),
            width=200,
            padding=5,
            bgcolor=ft.Colors.GREY_800,
            border_radius=5,
            border=ft.border.all(1, ft.Colors.BLUE_400),
            opacity=0.7,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK54),
        )

        # Draggable wrapper
        draggable = ft.Draggable(
            group="doc_node",
            content=ft.Container(
                content=node_content,
                padding=ft.padding.only(left=level * 20),
            ),
            content_feedback=feedback,
            data=node["id"],  # Pass ID directly as data for retrieval
        )

        # Drop Target Logic for Nesting
        def on_nest_will_accept(e):
            # Only accept if not dropping onto self
            # e.data is serialized JSON string, but might differ.
            # Safer to rely on manual check in accept, but for highlight we try:
            # Note: e.data comes from Draggable.data.
            if e.data == node["id"] or e.data == f'"{node["id"]}"':
                return False

            # Highlight node background
            node_content.bgcolor = ft.Colors.BLUE_GREY_700
            node_content.update()
            return True

        def on_nest_leave(e):
            # Restore background
            node_content.bgcolor = (
                ft.Colors.BLUE_900 if is_selected else ft.Colors.TRANSPARENT
            )
            node_content.update()

        def on_nest_accept(e):
            # Retrieve source ID reliably
            src_id = e.data

            # Handle Flet serialization
            if src_id and isinstance(src_id, str):
                if len(src_id) > 1 and src_id.startswith('"') and src_id.endswith('"'):
                    src_id = src_id[1:-1]

            # Fallback
            if not src_id and e.src_id:
                src_control = self.page_ref.get_control(e.src_id)
                if src_control:
                    src_id = src_control.data

            # Restore bg immediately
            on_nest_leave(None)

            # Prevent dropping on self
            if src_id and str(src_id) != node["id"]:
                self._handle_nesting(str(src_id), node["id"])

        return ft.DragTarget(
            group="doc_node",
            content=draggable,
            on_will_accept=on_nest_will_accept,
            on_leave=on_nest_leave,
            on_accept=on_nest_accept,
        )

    def _select_node(self, node: dict[str, Any]):
        """Handles node selection."""
        self.selected_node_id = node["id"]
        self._refresh_tree()

    def _find_node_and_parent(
        self,
        target_id: str,
        current_list: list[dict[str, Any]],
        parent_node: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]] | None]:
        """Finds a node and the list containing it."""
        for node in current_list:
            if node["id"] == target_id:
                return node, current_list
            if node.get("children"):
                found, found_list = self._find_node_and_parent(
                    target_id, node["children"], node
                )
                if found:
                    return found, found_list
        return None, None

    def _handle_reorder(
        self, src_id: str, target_parent_id: str | None, target_index: int
    ):
        """Moves src node to a specific index within target_parent's children."""
        # print(f"Reorder: {src_id} -> Parent {target_parent_id} @ {target_index}")

        # Update selection immediately
        self.selected_node_id = src_id

        # 1. Check for circular dependency (cannot move parent into own child)
        if target_parent_id and self._is_descendant(src_id, target_parent_id):
            # print("Cannot move node into its own descendant")
            self._refresh_tree()
            return

        # 2. Find Source Node and remove it
        node_to_move, source_list = self._find_node_and_parent(src_id, self.docs_data)
        if not node_to_move or source_list is None:
            # print("Source node not found")
            self._refresh_tree()
            return

        # 3. Identify Target List
        target_list = None
        if target_parent_id is None:
            target_list = self.docs_data
        else:
            parent_node, _ = self._find_node_and_parent(
                target_parent_id, self.docs_data
            )
            if parent_node:
                target_list = parent_node.get("children")
                if target_list is None:
                    parent_node["children"] = []
                    target_list = parent_node["children"]
            else:
                # print("Target parent not found")
                self._refresh_tree()
                return

        if target_list is None:
            self._refresh_tree()
            return

        # 4. Adjust Index if moving within same list
        # If we remove from an index BEFORE the target index, the target index must decrement
        if source_list is target_list:
            # Find current index
            current_index = -1
            for i, n in enumerate(source_list):
                if n["id"] == src_id:
                    current_index = i
                    break

            if current_index != -1:
                if current_index < target_index:
                    target_index -= 1

                # Check for no-op (moving to same position or next slot which is same visual position)
                if current_index == target_index:
                    self._refresh_tree()
                    return

        # 5. Execute Move
        try:
            source_list.remove(node_to_move)
            target_list.insert(target_index, node_to_move)
        except ValueError:
            pass

        self._refresh_tree()

    def _handle_nesting(self, src_id: str, target_node_id: str):
        """Moves src node to be a child of target_node."""
        # print(f"Nest: {src_id} -> Into {target_node_id}")

        # Update selection
        self.selected_node_id = src_id

        if src_id == target_node_id:
            self._refresh_tree()
            return

        if self._is_descendant(src_id, target_node_id):
            print("Cannot nest node into its own descendant")
            self._refresh_tree()
            return

        # 1. Find and remove source
        node_to_move, source_list = self._find_node_and_parent(src_id, self.docs_data)
        if not node_to_move or source_list is None:
            self._refresh_tree()
            return

        # 2. Find target node
        target_node, _ = self._find_node_and_parent(target_node_id, self.docs_data)
        if not target_node:
            self._refresh_tree()
            return

        # 3. Execute Move
        try:
            source_list.remove(node_to_move)

            if "children" not in target_node:
                target_node["children"] = []
            target_node["children"].append(node_to_move)
        except ValueError:
            pass

        self._refresh_tree()

    def _is_descendant(self, potential_ancestor_id: str, target_id: str) -> bool:
        """Checks if target_id is a descendant of potential_ancestor_id."""
        ancestor, _ = self._find_node_and_parent(potential_ancestor_id, self.docs_data)
        if not ancestor:
            return False

        def check_children(node: dict[str, Any]) -> bool:
            if not node.get("children"):
                return False
            for child in node["children"]:
                if child["id"] == target_id:
                    return True
                if check_children(child):
                    return True
            return False

        return check_children(ancestor)

    def _delete_node(self, node_to_delete: dict[str, Any]):
        """Removes a node from the data structure and updates UI."""
        self._delete_node_from_data(node_to_delete["id"])
        self._refresh_tree()

    def _delete_node_from_data(self, target_id: str):
        """Helper to remove node from data without refreshing UI immediately."""
        _, source_list = self._find_node_and_parent(target_id, self.docs_data)
        if source_list:
            for i, n in enumerate(source_list):
                if n["id"] == target_id:
                    source_list.pop(i)
                    break

    def on_rail_change(self, e):
        selected_index = e.control.selected_index
        new_content = ft.Text("Unknown Selection")

        if selected_index == 0:
            new_content = self._build_outline_view()
        elif selected_index == 1:
            new_content = ft.Text("File System Content", size=14)

        if self.drawer_container_ref.current:
            self.drawer_container_ref.current.content = new_content
            self.drawer_container_ref.current.update()
