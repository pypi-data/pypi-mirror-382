"""
Utilities for parsing semi-structured text data
"""

from .parse import parse_headers, parse_body


__all__: tuple[str, ...] = ("parse_headers", "parse_body")
