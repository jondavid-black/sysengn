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
    assert isinstance(terminal_component.output_control, ft.ListView)
    assert isinstance(terminal_component.input_control, ft.TextField)
    assert terminal_component.shell is None  # Should be None before mount
    assert terminal_component.content is not None


def test_terminal_mount_unmount(terminal_component):
    """Test that did_mount initializes shell and will_unmount closes it."""
    with patch("sysengn.ui.components.terminal.ShellManager") as MockShellManager:
        mock_shell_instance = MockShellManager.return_value

        terminal_component.did_mount()

        assert terminal_component.shell is not None
        MockShellManager.assert_called_once()

        terminal_component.will_unmount()
        mock_shell_instance.close.assert_called_once()


@pytest.mark.asyncio
async def test_terminal_output_update(terminal_component):
    """Test that shell output updates the UI."""
    # Mock page
    mock_page = MagicMock()
    terminal_component.page = mock_page

    # Mock output_control.update (since we don't have a real page connection)
    terminal_component.output_control.update = MagicMock()

    # Capture the task passed to run_task
    captured_task: Any = None

    def capture_task(task):
        nonlocal captured_task
        captured_task = task

    mock_page.run_task.side_effect = capture_task

    # Trigger output
    test_output = "Hello World\n"
    terminal_component._on_shell_output(test_output)

    # Verify run_task was called
    mock_page.run_task.assert_called_once()
    assert captured_task is not None

    # Execute the captured async task
    if captured_task:
        await captured_task()

    # Verify controls were updated
    assert len(terminal_component.output_control.controls) == 1
    assert isinstance(terminal_component.output_control.controls[0], ft.Text)
    assert terminal_component.output_control.controls[0].value == test_output

    # Verify update() was called
    terminal_component.output_control.update.assert_called_once()


def test_terminal_command_submit(terminal_component):
    """Test that submitting a command writes to shell."""
    # Mock shell
    mock_shell = MagicMock()
    terminal_component.shell = mock_shell

    # Mock input control behavior
    terminal_component.input_control.value = "ls -la"
    terminal_component.input_control.update = MagicMock()
    terminal_component.input_control.focus = MagicMock()

    # Trigger submit
    e = MagicMock()
    terminal_component._on_command_submit(e)

    # Verify shell.write called
    mock_shell.write.assert_called_once_with("ls -la")

    # Verify input cleared and refocused
    assert terminal_component.input_control.value == ""
    terminal_component.input_control.focus.assert_called_once()
    terminal_component.input_control.update.assert_called_once()


def test_terminal_empty_command_submit(terminal_component):
    """Test that empty commands are ignored."""
    mock_shell = MagicMock()
    terminal_component.shell = mock_shell

    terminal_component.input_control.value = ""

    e = MagicMock()
    terminal_component._on_command_submit(e)

    mock_shell.write.assert_not_called()
