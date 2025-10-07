"""
Enables the execution of the CLI by package name
"""

if __name__ == "__main__":
    from . import main

    main.main()


__all__: tuple[str, ...] = tuple()
