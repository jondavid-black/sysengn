from sysengn.main import get_greeting, main
import pytest


def test_get_greeting():
    """Verify the greeting message is correct."""
    assert get_greeting() == "Hello from SysEngn!"


def test_main(capsys):
    """Verify the main entry point prints the greeting."""
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello from SysEngn!"
