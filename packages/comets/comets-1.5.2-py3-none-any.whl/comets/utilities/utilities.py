# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.
import inspect
from datetime import timedelta
import math
import numpy as np


def to_list(variable):
    if isinstance(variable, list):
        return variable
    else:
        return [variable]


def check_size(variable):
    """
    Checks value of "size" input value in a variable, distribution or generator
    """
    if "size" in variable:
        if not isinstance(variable['size'], int):
            raise ValueError("Size should be an integer")
        if variable['size'] < 1:
            raise ValueError('Size should be positive')


# compute the next_multiple >= value for which next_multiple%divider = 0
def next_multiple(value, divider):
    if value % divider == 0:
        next_multiple = value
    else:
        next_multiple = divider * (value // divider + 1)
    return next_multiple


def next_power_of_2(value):
    value = max(int(value) - 1, 1)
    return 1 << value.bit_length()


def filter_method_optional_arguments(method, list_of_options):
    method_options = {}
    for key, param in inspect.signature(method).parameters.items():
        if key in list_of_options and param.default is not param.empty:
            method_options[key] = list_of_options[key]
    return method_options


def format_duration(seconds):  # pragma: no cover
    """Format a duration given in seconds to a user-readable format

    Args:
        seconds (float): number of seconds
    """
    if seconds == math.inf:
        return str(math.inf)
    return str(timedelta(seconds=seconds))


def remove_nans_from_array(inarray):
    """Remove nan values from an array and return the array without them."""

    inarray = np.asarray(inarray)
    return inarray[~np.isnan(inarray)]
