import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from sysengn.ui.components.terminal import TerminalComponent


@pytest.fixture
def terminal_component():
    return TerminalComponent()


def test_terminal_initialization(terminal_component):
    """Test that the terminal component initializes with correct controls."""
    # Updated expectations for VT100 terminal
    assert isinstance(terminal_component.content, ft.Column)
    assert len(terminal_component.terminal_lines) == terminal_component.rows
    assert terminal_component.shell is None  # Should be None before mount


def test_terminal_mount_unmount(terminal_component):
    """Test that did_mount initializes shell and will_unmount closes it."""
    with patch("sysengn.ui.components.terminal.ShellManager") as MockShellManager:
        mock_shell_instance = MockShellManager.return_value

        # Mock page
        terminal_component.page = MagicMock()

        terminal_component.did_mount()

        assert terminal_component.shell is not None
        MockShellManager.assert_called_once()
        # Verify event listener attached
        assert terminal_component.page.on_keyboard_event is not None

        terminal_component.will_unmount()
        mock_shell_instance.close.assert_called_once()
        # Verify event listener removed
        assert terminal_component.page.on_keyboard_event is None


def test_key_handling(terminal_component):
    """Test keyboard event handling."""
    mock_shell = MagicMock()
    terminal_component.shell = mock_shell
    terminal_component.focused = True

    # Test simple key
    e = MagicMock(key="a", ctrl=False)
    terminal_component._on_key(e)
    mock_shell.write.assert_called_with("a")

    # Test Enter
    e = MagicMock(key="Enter", ctrl=False)
    terminal_component._on_key(e)
    mock_shell.write.assert_called_with("\r")

    # Test Ctrl+C
    e = MagicMock(key="C", ctrl=True)
    terminal_component._on_key(e)
    mock_shell.write.assert_called_with("\x03")

    # Test ignored when not focused
    terminal_component.focused = False
    mock_shell.reset_mock()
    terminal_component._on_key(e)
    mock_shell.write.assert_not_called()


def test_key_mapping_comprehensive(terminal_component):
    """Test comprehensive key mapping."""
    mock_shell = MagicMock()
    terminal_component.shell = mock_shell
    terminal_component.focused = True

    # Define test cases: (flet_key, expected_ansi)
    test_cases = [
        ("Backspace", "\x7f"),
        ("Tab", "\t"),
        ("Escape", "\x1b"),
        ("Arrow Up", "\x1b[A"),
        ("Arrow Down", "\x1b[B"),
        ("Arrow Right", "\x1b[C"),
        ("Arrow Left", "\x1b[D"),
        ("Home", "\x1b[H"),
        ("End", "\x1b[F"),
        ("Page Up", "\x1b[5~"),
        ("Page Down", "\x1b[6~"),
        ("Space", " "),
        (" ", " "),
        ("A", "A"),  # Single char
    ]

    for key, expected in test_cases:
        e = MagicMock(key=key, ctrl=False)
        terminal_component._on_key(e)
        mock_shell.write.assert_called_with(expected)

    # Test Ctrl combinations
    ctrl_cases = [
        ("C", "\x03"),
        ("D", "\x04"),
        ("Z", "\x1a"),
        ("L", "\x0c"),
    ]

    for key, expected in ctrl_cases:
        e = MagicMock(key=key, ctrl=True)
        terminal_component._on_key(e)
        mock_shell.write.assert_called_with(expected)

    # Test unknown key ignored
    e = MagicMock(key="UnknownKey", ctrl=False)
    mock_shell.reset_mock()
    terminal_component._on_key(e)
    mock_shell.write.assert_not_called()


def test_vt100_rendering_colors(terminal_component):
    """Test that VT100 color codes are rendered correctly."""
    # Mock page and shell
    terminal_component.page = MagicMock()

    # Mock the update method on terminal lines to avoid "must be added to page" error
    # We need to mock it on the actual objects in the list
    for line in terminal_component.terminal_lines:
        line.update = MagicMock()

    # Capture the task passed to run_task
    captured_tasks = []
    terminal_component.page.run_task = lambda x: captured_tasks.append(x)

    # Simulate shell output with Red color
    # \x1b[31m is Red in ANSI
    red_hello = "\x1b[31mHello"

    # Trigger output
    terminal_component._on_shell_output(red_hello)

    # Execute the captured task (it's a coroutine)
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    loop.run_until_complete(captured_tasks[0]())

    # Verify pyte screen content
    char = terminal_component.screen.buffer[0][0]
    assert char.data == "H"
    assert char.fg == "red"

    # Verify UI rendering (TextSpans)
    first_line = terminal_component.terminal_lines[0]

    # It should use spans
    assert len(first_line.spans) > 0

    # First span: "Hello" in red
    span1 = first_line.spans[0]
    assert span1.text == "Hello"
    assert span1.style.color == ft.Colors.RED


def test_vt100_rendering_integration(terminal_component):
    """Test full pipeline from shell output to TextSpans."""
    # Mock page
    mock_page = MagicMock()
    terminal_component.page = mock_page

    # Mock the update method on terminal lines to avoid "must be added to page" error
    for line in terminal_component.terminal_lines:
        line.update = MagicMock()

    # Capture the task passed to run_task
    captured_tasks = []
    mock_page.run_task = lambda x: captured_tasks.append(x)

    # Feed input: Red "Hello" then reset then " World"
    terminal_component._on_shell_output("\x1b[31mHello\x1b[0m World")

    # Execute the captured task
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    loop.run_until_complete(captured_tasks[0]())

    # Verify first line content
    first_line = terminal_component.terminal_lines[0]

    # It should use spans now
    assert len(first_line.spans) > 0

    # First span: "Hello" in red
    span1 = first_line.spans[0]
    assert span1.text == "Hello"
    # Check for both Flet constant and raw string if map_color implementation varies
    assert span1.style.color == ft.Colors.RED

    # Second span: " World" in default (white)
    span2 = first_line.spans[1]
    # The terminal fills the rest of the line with spaces, so we check startswith or strip
    assert span2.text.startswith(" World")
    assert span2.style.color == ft.Colors.WHITE


def test_click_focus(terminal_component):
    """Test clicking focuses/unfocuses terminal."""
    # Mock update since component isn't attached to page
    terminal_component.update = MagicMock()

    # Initial state
    assert not terminal_component.focused

    # Click to focus
    e = MagicMock()
    terminal_component._on_click(e)
    assert terminal_component.focused
    assert terminal_component.border.top.color == ft.Colors.BLUE
    terminal_component.update.assert_called()

    # Click again to unfocus (toggle behavior)
    terminal_component._on_click(e)
    assert not terminal_component.focused
    assert terminal_component.border.top.color == ft.Colors.TRANSPARENT


def test_terminal_resize(terminal_component):
    """Test that resizing the terminal updates the shell and screen dimensions."""
    # Mock shell
    mock_shell = MagicMock()
    terminal_component.shell = mock_shell

    # Mock page and update to avoid "not added to page" error
    terminal_component.page = MagicMock()

    # Mock content column update
    if isinstance(terminal_component.content, ft.Column):
        terminal_component.content.update = MagicMock()

    # Mock _update_display to avoid rendering issues with new unattached controls
    # We are testing resize logic here, not rendering
    terminal_component._update_display = MagicMock()

    # Initial size (default 80x24)
    assert terminal_component.cols == 80
    assert terminal_component.rows == 24

    # Resize width only (calculating cols from width / CHAR_WIDTH)
    # CHAR_WIDTH = 8.5. So 900 width -> ~105 cols
    terminal_component.handle_resize(900)

    assert terminal_component.cols == 105
    # Rows shouldn't change if height not provided
    assert terminal_component.rows == 24

    # Verify shell.resize called
    mock_shell.resize.assert_called_with(24, 105)
    terminal_component._update_display.assert_called()

    # Resize both
    # CHAR_HEIGHT = 18. So 540 height -> 30 rows
    terminal_component.handle_resize(450, 540)

    # 450 / 8.5 = 52.94 -> 52
    assert terminal_component.cols == 52
    assert terminal_component.rows == 30  # 540/18 = 30

    # Verify shell.resize called with new values
    mock_shell.resize.assert_called_with(30, 52)
