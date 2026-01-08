import flet as ft
from unittest.mock import MagicMock
from sysengn.ui.docs.docs_screen import DocsScreen
from sysengn.core.auth import User


def test_docs_screen_structure():
    """Verify DocsScreen structure and content."""
    mock_page = MagicMock(spec=ft.Page)
    mock_user = MagicMock(spec=User)
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"

    docs_screen = DocsScreen(mock_page, mock_user)

    assert isinstance(docs_screen, ft.Container)
    # Now it's a Row because of the side rail layout
    assert isinstance(docs_screen.content, ft.Row)

    row = docs_screen.content
    assert len(row.controls) == 4

    # Check Rail
    rail = row.controls[0]
    assert isinstance(rail, ft.NavigationRail)
    assert rail.destinations is not None
    assert len(rail.destinations) == 2

    # Check Drawer
    drawer = row.controls[1]
    assert isinstance(drawer, ft.Container)

    # Check Main Content
    main_content_container = row.controls[3]
    assert isinstance(main_content_container, ft.Container)

    column = main_content_container.content
    assert isinstance(column, ft.Column)
    controls = column.controls

    # Check Title
    title_row = controls[0]
    assert isinstance(title_row, ft.Row)
    title_text = title_row.controls[0]
    assert isinstance(title_text, ft.Text)
    assert str(title_text.value) == "Documentation"

    # Check Placeholder Content
    placeholder_container = controls[2]  # Index 2 is the main content container
    assert isinstance(placeholder_container, ft.Container)

    placeholder_col = placeholder_container.content
    assert isinstance(placeholder_col, ft.Column)

    # Check for icon
    icon = placeholder_col.controls[0]
    assert isinstance(icon, ft.Icon)
    assert icon.name == ft.Icons.LIBRARY_BOOKS

    # Check for module text
    module_text = placeholder_col.controls[1]
    assert isinstance(module_text, ft.Text)
    assert str(module_text.value) == "Documentation Module"


class MockDocsScreenLogic:
    """Helper class to test DocsScreen logic methods in isolation."""

    def __init__(self):
        self.selected_node_id = None
        # Mock Data similar to DocsScreen
        self.docs_data = [
            {
                "id": "doc1",
                "title": "Doc 1",
                "children": [
                    {"id": "sec1", "title": "Section 1", "children": []},
                    {"id": "sec2", "title": "Section 2", "children": []},
                ],
            },
            {"id": "doc2", "title": "Doc 2", "children": []},
        ]

    def _refresh_tree(self):
        pass

    # Injecting the actual methods from DocsScreen (unbound)
    # This allows us to test the exact logic without Flet UI overhead
    _find_node_and_parent = DocsScreen._find_node_and_parent
    _is_descendant = DocsScreen._is_descendant
    _handle_reorder = DocsScreen._handle_reorder
    _handle_nesting = DocsScreen._handle_nesting


def test_docs_reorder_logic():
    """Test the tree reordering logic."""
    screen = MockDocsScreenLogic()

    # Case 1: Move doc1 (index 0) to after doc2 (index 2)
    # Initial: [doc1, doc2] -> Target: [doc2, doc1]
    screen._handle_reorder("doc1", None, 2)
    assert screen.docs_data[0]["id"] == "doc2"
    assert screen.docs_data[1]["id"] == "doc1"

    # Reset data for next case
    screen.docs_data = [
        {"id": "doc1", "children": [{"id": "sec1"}, {"id": "sec2"}]},
        {"id": "doc2", "children": []},
    ]

    # Case 2: Move sec2 (index 1) to before sec1 (index 0) within same parent
    screen._handle_reorder("sec2", "doc1", 0)
    children = screen.docs_data[0]["children"]
    assert children[0]["id"] == "sec2"
    assert children[1]["id"] == "sec1"

    # Case 3: No-op move (moving to same position)
    original_order = [c["id"] for c in screen.docs_data[0]["children"]]
    screen._handle_reorder("sec2", "doc1", 0)  # sec2 is already at 0 now
    current_order = [c["id"] for c in screen.docs_data[0]["children"]]
    assert original_order == current_order


def test_docs_reorder_failures():
    """Test failure cases for reordering."""
    screen = MockDocsScreenLogic()

    # Case 1: Target parent not found
    screen._handle_reorder("doc1", "non_existent_parent", 0)
    # Data should be unchanged
    assert len(screen.docs_data) == 2

    # Case 2: Source node not found
    screen._handle_reorder("non_existent_node", None, 0)
    assert len(screen.docs_data) == 2


def test_docs_nesting_logic():
    """Test the nesting logic."""
    screen = MockDocsScreenLogic()

    # Move sec1 (from doc1) into doc2
    screen._handle_nesting("sec1", "doc2")

    # Check doc1 children (sec1 should be gone)
    doc1_children = screen.docs_data[0]["children"]
    assert len(doc1_children) == 1
    assert doc1_children[0]["id"] == "sec2"

    # Check doc2 children (sec1 should be added)
    doc2_children = screen.docs_data[1]["children"]
    assert len(doc2_children) == 1
    assert doc2_children[0]["id"] == "sec1"


def test_docs_nesting_failures():
    """Test failure cases for nesting."""
    screen = MockDocsScreenLogic()

    # Case 1: Nesting into self (should do nothing)
    screen._handle_nesting("doc1", "doc1")
    assert len(screen.docs_data) == 2

    # Case 2: Source node not found
    screen._handle_nesting("missing_node", "doc2")
    assert len(screen.docs_data[1]["children"]) == 0

    # Case 3: Target node not found
    screen._handle_nesting("doc1", "missing_target")
    assert len(screen.docs_data) == 2


def test_circular_dependency_prevention():
    """Ensure we cannot nest a parent into its own child."""
    screen = MockDocsScreenLogic()
    original_state = str(screen.docs_data)

    # Try to move doc1 into sec1 (which is inside doc1)
    screen._handle_nesting("doc1", "sec1")

    # Should be unchanged
    assert str(screen.docs_data) == original_state
