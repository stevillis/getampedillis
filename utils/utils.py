def pad_list(lst, min_len=5, max_len=7, default_value="no"):
    """Pads the list with default_value if it's shorter than max_len."""
    len_lst = len(lst)
    if min_len <= len_lst < max_len:
        lst.extend([default_value] * (max_len - len_lst))

    return lst
