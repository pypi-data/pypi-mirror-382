from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np


def convert_dict_np_to_float(dic: dict) -> dict:
    """
    Convert all numpy floats in a dictionary to Python floats.

    Parameters
    ----------
    dic : dict
        The dictionary to convert.

    Returns
    -------
    dict
        The dictionary with all numpy floats converted to Python floats.
    """
    for key, value in dic.items():
        if isinstance(value, Mapping):
            convert_dict_np_to_float(value)
        elif isinstance(value, np.float32 | np.float64):
            dic[key] = float(value)
        elif isinstance(dic[key], Sequence) and not isinstance(dic[key], str):
            dic[key] = [
                float(x) if isinstance(x, np.float32 | np.float64) else x for x in value
            ]
    return dic
