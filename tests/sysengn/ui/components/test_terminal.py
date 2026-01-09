import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from sysengn.ui.components.terminal import TerminalComponent
from typing import Any


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
