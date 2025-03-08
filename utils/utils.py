from typing import List

"""Utility functions for list manipulation and other general-purpose operations."""


def pad_list(
    lst: List[str], min_len: int = 5, max_len: int = 7, fill_with: str = "no"
) -> List[str]:
    """Pads the list with fill_with if it's shorter than max_len."""
    len_lst = len(lst)
    if min_len <= len_lst < max_len:
        lst.extend([fill_with] * (max_len - len_lst))

    return lst
