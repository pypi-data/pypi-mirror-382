from typing import Union, Optional


def find_any(
    content: Union[str, bytes],
    target: tuple[Union[str, int], ...],
    start: int = 0,
    end: Optional[int] = None,
) -> int:
    """
    Looks for the first instance of a targeted character.

    :param content: The content to search through.
    :param target: A tuple of either targeted strings or integers (used for searching bytes).
    :param start: Minimum index to search.
    :param end: Maximum index to search.
    :return: Last occurrence index of targets in the specified range, or -1 if not found.
    """

    end_index: int = len(content) if end is None else end
    for i in range(start, end_index):
        if content[i] in target:
            return i

    return -1


def rfind_any(
    content: Union[str, bytes],
    target: tuple[Union[str, int], ...],
    start: int = 0,
    end: Optional[int] = None,
) -> int:
    """
    Starting from the end, looks for the first instance of a targeted character.

    :param content: The content to search through.
    :param target: A tuple of either targeted strings or integers (used for searching bytes).
    :param start: Minimum index to search.
    :param end: Maximum index to search.
    :return: Last occurrence index of targets in the specified range, or -1 if not found.
    """

    end_index: int = (len(content) if end is None else end) - 1
    for i in range(end_index, start - 1, -1):
        if content[i] in target:
            return i

    return -1
