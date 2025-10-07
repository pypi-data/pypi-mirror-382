"""
Provides a command-line interface to the package
"""

import argparse
import json
import sys
from typing import BinaryIO, Iterable

from . import parse


def _parse_file(
    file: BinaryIO,
    force_headers: Iterable[bytes],
    encoding: str = "utf-8",
    errors: str = "backslashreplace",
) -> None:
    """
    Parses `file` and prints output to standard output.

    :param file: File to parse.
    :param force_headers: Iterable of header names to use as a heuristic.
    :param encoding: Encoding to use for decoding.
    :param errors: Error resolution strategy for decoding.
    :return: None.
    """

    header_line: bytes = file.readline()
    while not header_line.strip():
        header_line = file.readline()

        # If we have no data...well, that's it.
        if not header_line:
            return

    headers: tuple[tuple[bytes, int, int | None], ...] = parse.parse_headers(
        header_line, force=force_headers
    )
    for line in file:
        print(
            json.dumps(
                {
                    k.decode(encoding, errors): v.decode(encoding, errors)
                    for k, v in parse.parse_body(headers, line).items()
                }
            )
        )


def _process_file(
    file_path: str,
    force_headers: Iterable[bytes],
    encoding: str = "utf-8",
    errors: str = "backslashreplace",
) -> None:
    """
    Opens the appropriate stream and performs parsing.

    :param file_path: Path to file to parse.
    :param force_headers: Iterable of header names to use as a heuristic.
    :param encoding: Encoding to use for decoding.
    :param errors: Error resolution strategy for decoding.
    :return: None.
    """

    if file_path == "-":
        if sys.stdin.isatty():
            raise RuntimeError("Terminal is attached - cannot process standard input")

        _parse_file(
            sys.stdin.buffer,
            force_headers=force_headers,
            encoding=encoding,
            errors=errors,
        )
    else:
        with open(file_path, "rb") as file:
            _parse_file(
                file, force_headers=force_headers, encoding=encoding, errors=errors
            )


def main() -> None:
    """
    Parses inputs from the command-line and prints output to standard output.

    :return: None.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--header",
        "-H",
        nargs="+",
        action="extend",
        default=[],
        help="Explicit header names to search for",
    )
    parser.add_argument(
        "--encoding", "-e", default="utf-8", help="Encoding for decoding bytes"
    )
    parser.add_argument(
        "--errors",
        "-E",
        default="backslashreplace",
        help="Decoding error resolution method",
    )
    parser.add_argument(
        "files", nargs="+", help="File path to process or '-' for standard input"
    )

    args: argparse.Namespace = parser.parse_args()

    headers: tuple[bytes, ...] = tuple(header.encode() for header in args.header)
    for file_path in args.files:
        # noinspection PyBroadException
        # pylint: disable=broad-exception-caught
        try:
            _process_file(
                file_path,
                force_headers=headers,
                encoding=args.encoding,
                errors=args.errors,
            )
        except Exception as e:
            print(f"Failed to process file: {file_path} ({e})", file=sys.stderr)


if __name__ == "__main__":
    main()


__all__: tuple[str, ...] = ("main",)
