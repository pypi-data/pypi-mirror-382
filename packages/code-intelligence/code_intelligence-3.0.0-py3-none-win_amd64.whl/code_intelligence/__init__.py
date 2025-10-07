from .goober import (
    Language,
    Definition_Link,
    scan_file,
    find_symbols_in_text,
    stop,
)

__version__ = "3.0.0"
__version_info__ = tuple(int(i) for i in __version__.split('.'))

__all__ = [
    "Language",
    "Definition_Link",
    "scan_file",
    "find_symbols_in_text",
    "stop",
]
