"""snake_to_pascal_case module definition"""

def snake_to_pascal(snake_str: str) -> str:
    """Converts a snake_case string to PascalCase.

    Parameters
    ----------
    snake_str : str
        The string in snake_case format.

    Returns
    -------
    str
        The converted string in PascalCase format.
    """
    return ''.join(word.capitalize() for word in snake_str.split('_'))
