"""
Parsing utilities for semi-structured tabular text input
"""

from typing import TypeAlias, TYPE_CHECKING, Iterable
from . import _util

if TYPE_CHECKING:
    BytesType: TypeAlias = bytearray | bytes
    Header: TypeAlias = tuple[bytes, int, int | None]


def parse_headers(
    data: "BytesType", force: Iterable["BytesType"] | None = None
) -> tuple["Header", ...]:
    """
    Parses a line of data to derive header names and positions.

    :param data: Data to parse.
    :param force: Iterable of header names to use as a heuristic.
    :return: Tuple of headers, consisting of a name, start index, and end index.
    """

    extracted_headers: list["Header"] = []

    header_start: int = 0
    header_found: bool = False
    data_length: int = len(data)

    i: int = 0
    while i < data_length:
        current_header: "BytesType" = data[header_start:i].strip()
        if force is not None and current_header in force:
            header_found = True

        if data[i] == 32:
            if len(data) > i + 1 and data[i + 1] == 32 and current_header:
                # We know that the next character is a space, so skip it.
                i += 1
                header_found = True
        elif data[i] == 9:
            header_found = True
        elif header_found:
            extracted_headers.append((bytes(current_header), header_start, i))
            header_start = i
            header_found = False

        i += 1

    # Capture our final header if there is one.
    ending_header: "BytesType" = data[header_start:].strip()
    if ending_header:
        extracted_headers.append((bytes(ending_header), header_start, None))

    return tuple(extracted_headers)


def parse_body(
    headers: tuple["Header", ...], line: "BytesType"
) -> dict[bytes, "BytesType"]:
    """
    Parses a body line based on provided headers.

    :param headers: Headers to map data to.
    :param line: Data to parse.
    :return: Dictionary of parsed data.
    """

    entry: dict[bytes, "BytesType"] = {}

    start_offset: int | None = 0
    for header_name, start_index, end_index in headers:
        if start_offset is None or start_index > len(line):
            break

        # If our data is shorter than our headers
        if end_index is not None:
            end_index: int = min(end_index, len(line))

        # If `end_index` is None, it indicates that we should capture everything remaining.
        # The end of our header being our space character indicates our simplest case
        # where we may potentially have fixed-width columns.
        header_start_offset: int = max(start_offset, start_index)
        if header_start_offset >= len(line):
            break

        if end_index is not None and (
            end_index <= start_offset or line[end_index - 1] != 32
        ):
            # Rather than strictly go off of our header indices, assume that continuous
            # data represents a singular column as it appears we might be overflowing.
            end_index: int = _util.find_any(line, (32, 9), header_start_offset)
            end_index: int | None = None if end_index == -1 else end_index

        # Given we have established that our current offset is assigned to our current
        # header, we'll also assume that the whole chunk is associated as well.
        if line[header_start_offset] != 32:
            start_index: int = _util.rfind_any(line, (32, 9), 0, header_start_offset)
            header_start_offset = None if start_index == -1 else start_index

        value: "BytesType" = line[header_start_offset:end_index].strip()
        if value:
            entry[header_name] = value

        start_offset = end_index

    return entry


__all__: tuple[str, ...] = ("parse_headers", "parse_body")
