"""
Enables the execution of the CLI by package name
"""

from . import main


def init() -> None:
    """
    If executed as a script, runs the main function.

    :return: None.
    """

    if __name__ == "__main__":
        main.main()


init()

__all__: tuple[str, ...] = tuple()
