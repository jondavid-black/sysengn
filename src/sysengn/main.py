def get_greeting() -> str:
    """Returns the application greeting message.

    Returns:
        The greeting string.
    """
    return "Hello from SysEngn!"


def main() -> None:
    """Entry point for the application."""
    print(get_greeting())


if __name__ == "__main__":
    main()
