import os


def yes_or_no_question(question: str, default_no: bool = True) -> bool:
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True  # Ignore confirmations when running tests
    choices = " [y/N]: " if default_no else " [Y/n]: "
    default_answer = "n" if default_no else "y"
    reply = str(input(question + choices)).lower().strip() or default_answer
    if reply[0] == "y":
        return True
    if reply[0] == "n":
        return False
    else:
        return False if default_no else True
