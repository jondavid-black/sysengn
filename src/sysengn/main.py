import argparse
import flet as ft


def get_greeting() -> str:
    """Returns the application greeting message.

    Returns:
        The greeting string.
    """
    return "Hello from SysEngn!"


def main_page(page: ft.Page) -> None:
    """The main page of the application.

    Args:
        page: The Flet page object to construct the UI on.
    """
    page.title = "SysEngn"
    page.add(ft.Text(value=get_greeting(), size=30))


def main() -> None:
    """Entry point for the application."""
    parser = argparse.ArgumentParser(description="SysEngn Application")
    parser.add_argument("--web", action="store_true", help="Run in web browser")
    args = parser.parse_args()

    view = ft.AppView.WEB_BROWSER if args.web else ft.AppView.FLET_APP
    ft.app(target=main_page, view=view)


if __name__ == "__main__":
    main()
