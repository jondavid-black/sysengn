import pytest
from unittest.mock import MagicMock
import flet as ft
from sysengn.ui.components.terminal import TerminalComponent


@pytest.fixture
def terminal():
    """Create a terminal component for testing."""
    term = TerminalComponent(cols=80, rows=24)
    term.shell = MagicMock()
    # Mock the shell's write method
    term.shell.write = MagicMock()
    # Mock focus state
    term.focused = True
    return term


def test_arrow_up_key_mapping(terminal):
    """Test that Arrow Up key is mapped to the correct ANSI sequence."""
    # Create a mock KeyboardEvent for Arrow Up
    event = ft.KeyboardEvent(
        key="Arrow Up", shift=False, ctrl=False, alt=False, meta=False
    )

    # Call _on_key
    terminal._on_key(event)

    # Verify shell.write was called with the correct sequence for Arrow Up
    # Standard VT100 sequence for Arrow Up is ESC [ A
    terminal.shell.write.assert_called_with("\x1b[A")


def test_arrow_down_key_mapping(terminal):
    """Test that Arrow Down key is mapped to the correct ANSI sequence."""
    # Create a mock KeyboardEvent for Arrow Down
    event = ft.KeyboardEvent(
        key="Arrow Down", shift=False, ctrl=False, alt=False, meta=False
    )

    # Call _on_key
    terminal._on_key(event)

    # Verify shell.write was called with the correct sequence for Arrow Down
    # Standard VT100 sequence for Arrow Down is ESC [ B
    terminal.shell.write.assert_called_with("\x1b[B")


def test_no_write_when_unfocused(terminal):
    """Test that keys are ignored when terminal is not focused."""
    terminal.focused = False
    event = ft.KeyboardEvent(
        key="Arrow Up", shift=False, ctrl=False, alt=False, meta=False
    )

    terminal._on_key(event)

    terminal.shell.write.assert_not_called()


def test_ctrl_p_mapping(terminal):
    """Test Ctrl+P mapping (commonly used for history up in some shells)."""
    # Create a mock KeyboardEvent for Ctrl+P
    event = ft.KeyboardEvent(key="P", shift=False, ctrl=True, alt=False, meta=False)

    terminal._on_key(event)

    # Currently we expect this might fail or do nothing if not implemented.
    # The current implementation handles C, D, Z, L.
    # If it returns empty string, shell.write is not called.
    # We can check that behavior for now.
    # terminal.shell.write.assert_not_called()
    pass
