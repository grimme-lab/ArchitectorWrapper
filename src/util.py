from collections import Counter
import numpy as np
from typing import Any


def get_random_CN(low: int = 4, high: int = 6) -> int:
    """Get random coordination number from the range [low, high).

    Args:
        low (int, optional): Lowest possible coordination number, lower bound of range. Defaults to 4.
        high (int, optional): Minimum impossible coordination number, uppen bound of range. Defaults to 6.

    Returns:
        int: Random coordination number from the range [low, high).
    """
    return np.random.randint(low=low, high=high)


def split_dict_into_chunks(
    input_dict: dict[Any, Any], num_parts: int
) -> list[dict[Any, Any]]:
    """Split a dictionary into a specified number of smaller dictionaries.

    Args:
        input_dict (dict[Any, Any]): The dictionary to split.
        num_parts (int): The number of smaller dictionaries to create.

    Returns:
        list[dict[Any, Any]]: A list of smaller dictionaries.
    """
    dict_items = list(input_dict.items())
    dict_length = len(dict_items)

    # Calculate the size of each chunk and the number of remaining items
    chunk_size, remaining_items = divmod(dict_length, num_parts)

    chunks = []
    start = 0

    for _ in range(num_parts):
        # Add an extra item to the current chunk if there are remaining items
        extra_item = 1 if remaining_items > 0 else 0
        chunk_end = start + chunk_size + extra_item

        # Create the current chunk and add it to the list of chunks
        chunks.append(dict(dict_items[start:chunk_end]))

        # Update the start point for the next iteration
        start = chunk_end
        remaining_items -= extra_item

    return chunks


def read_xyz(file_path: str) -> tuple[list[str], list[tuple[float, float, float]]]:
    """
    Reads an XYZ file and returns the elements and coordinates.

    Args:
        file_path (str): The path to the XYZ file.

    Returns:
        tuple[list[str], list[tuple[float, float, float]]]: A tuple containing a list of elements and a list of coordinates.
    """
    elements = []
    coordinates = []

    with open(file_path, "r") as f:
        lines = f.readlines()[
            2:
        ]  # Skip the first two lines which usually contain meta-information

        for line in lines:
            tokens = line.strip().split()
            if (
                len(tokens) < 4
            ):  # Ensure there are enough tokens for an element and coordinates
                continue

            element, x, y, z = (
                tokens[0],
                float(tokens[1]),
                float(tokens[2]),
                float(tokens[3]),
            )
            elements.append(element)
            coordinates.append((x, y, z))

    return elements, coordinates


def check_max_one_overlap(list_a: list[str], list_b: list[str]) -> bool:
    """
    Check if at most one element from list_a appears in list_b, and appears only once.

    Args:
        list_a (list[str]): The first list to compare.
        list_b (list[str]): The second list to compare.

    Returns:
        bool: True if at most one element from list_a appears in list_b and appears only once, otherwise False.
    """

    count = Counter(list_b)
    overlap = set(list_a).intersection(set(list_b))

    if len(overlap) > 1:
        return False

    for item in overlap:
        if count.get(item, 0) > 1:
            return False

    return True
