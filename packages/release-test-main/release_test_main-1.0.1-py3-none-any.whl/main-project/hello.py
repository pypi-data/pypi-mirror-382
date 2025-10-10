"""Simple greeting module."""

def greet(name: str) -> str:
    """Greet someone by name."""
    message = f"Hello, {name}! This is the main project."
    print(message)
    return message


if __name__ == "__main__":
    greet('Bob')