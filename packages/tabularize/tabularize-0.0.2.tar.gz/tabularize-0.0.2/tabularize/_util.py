def find_any(
    content: str | bytes,
    target: tuple[str | int, ...],
    start: int = 0,
    end: int | None = None,
) -> int:
    """
    Looks for the first instance of a targeted character.

    :param content: The content to search through.
    :param target: A tuple of either targeted strings or integers (used for searching bytes).
    :param start: Minimum index to search.
    :param end: Maximum index to search.
    :return: Last occurrence index of targets in the specified range, or -1 if not found.
    """

    if end is None:
        end: int = len(content)

    for i in range(start, end):
        if content[i] in target:
            return i

    return -1


def rfind_any(
    content: str | bytes,
    target: tuple[str | int, ...],
    start: int = 0,
    end: int | None = None,
) -> int:
    """
    Starting from the end, looks for the first instance of a targeted character.

    :param content: The content to search through.
    :param target: A tuple of either targeted strings or integers (used for searching bytes).
    :param start: Minimum index to search.
    :param end: Maximum index to search.
    :return: Last occurrence index of targets in the specified range, or -1 if not found.
    """

    if end is None:
        end: int = len(content)

    for i in range(end - 1, start - 1, -1):
        if content[i] in target:
            return i

    return -1
