"""Tree-sitter SPARQL language binding."""

from typing import Optional

try:
    from .binding import language
except ImportError:
    language = None


def get_language() -> int:
    """Get the tree-sitter language for SPARQL.

    Returns:
        int: A pointer to the TSLanguage object for SPARQL.

    Raises:
        ImportError: If the binding module is not available.
    """
    if language is None:
        raise ImportError(
            "The tree-sitter-sparql binding is not available. "
            "Make sure the package is properly installed with: "
            "pip install tree-sitter-sparql"
        )
    return language()


__all__ = ["get_language", "language"]
__version__ = "0.1.0"
