"""utility functions for natal"""

from datetime import datetime
from natal.config import Config
from typing import Iterable


def color_hex(name: str, config: Config = Config()) -> str:
    """Get color hex code from name and config.

    Args:
        name (str): Color name to look up
        config (Config): Config containing color definitions

    Returns:
        str: Hex color code string
    """
    return getattr(config.colors, name)


def pairs[T](iterable: Iterable[T]) -> list[tuple[T, T]]:
    """Generate unique pairs of elements from an iterable.

    Args:
        iterable (Iterable[T]): Source of elements to pair

    Returns:
        list[tuple[T, T]]: List of element pairs as tuples
    """
    output = []
    for i in range(len(iterable)):
        for j in range(i + 1, len(iterable)):
            output.append((iterable[i], iterable[j]))
    return output


def member_of[T](const: list[T], name: str) -> T:
    """Get a member from a list of constants by name.

    Args:
        const (list[T]): List of constant definitions
        name (str): Name to look up

    Returns:
        T: Matching constant member
    """
    idx: int = const["name"].index(name)
    return {prop: const[prop][idx] for prop in const.model_fields}


def str_to_dt(dt_str: str) -> datetime:
    """Convert string to datetime object.

    Args:
        dt_str (str): Datetime string in format "YYYY-MM-DD HH:MM"

    Returns:
        datetime: Parsed datetime object
    """
    return datetime.strptime(dt_str[:16], "%Y-%m-%d %H:%M")
