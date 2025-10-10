"""Type stubs for tree-sitter-sparql."""

def language() -> int:
    """Get the tree-sitter language for SPARQL.

    Returns:
        int: A pointer to the TSLanguage object for SPARQL.
    """
    ...

def get_language() -> int:
    """Get the tree-sitter language for SPARQL.

    Returns:
        int: A pointer to the TSLanguage object for SPARQL.

    Raises:
        ImportError: If the binding module is not available.
    """
    ...

__version__: str
__all__: list[str]
