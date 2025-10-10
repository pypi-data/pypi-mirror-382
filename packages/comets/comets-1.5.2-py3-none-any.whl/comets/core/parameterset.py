# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pandas
from numpy import number

from ..utilities.utilities import to_list


class ParameterSet(dict):
    """
    A ParameterSet consists of a set of parameters, stored as a dictionary containing names of parameters and their values.
    The keys of the dictionary are strings representing the name of each parameter, and the values are python datatypes representing the corresponding value of a parameter (it may be a string, a float, an int, a bool, a list, a dict or a combination of these).
    Throughout the library a ParameterSet can be used interchangeably with a standard Python dictionary, since a ParameterSet is simply a dictionary. This class is mostly used for documentation purpose.

    Example
    -------

    {'param1': 1, 'param2': 1.5, 'param3': [1,2,4], 'param4': "option1", 'param5': {'a':1, 'b':2}}
    """

    @staticmethod
    def flatten(obj):
        output = {}
        flattened = True
        for key, val in obj.items():
            if isinstance(val, (tuple, list)):
                flattened = False
                new_dict = {
                    "{old_key}.{new_key}".format(old_key=key, new_key=i): v
                    for (i, v) in enumerate(val)
                }
                output.update(new_dict)
            elif isinstance(val, dict):
                flattened = False
                new_dict = {
                    "{old_key}.{new_key}".format(old_key=key, new_key=k): v
                    for (k, v) in val.items()
                }
                output.update(new_dict)
            else:
                output.update({key: val})

        if flattened:
            return output
        else:
            return ParameterSet.flatten(output)

    @staticmethod
    def to_dataframe(data, flatten=True, keep_numeric_only=False):
        """
        Transforms a (list of) ParameterSet(s) into a pandas DataFrame.

        Args:

            data (ParameterSet or list of ParameterSet): the ParameterSet(s) to transform
            flatten (bool, optional): If True, flattens the ParameterSet.
                Flattened keys are a concatenation of the ParameterSet keys interspersed with dots: "<level1_key>.<level2_key>...<leveln_key>".
                Lists are also flattened, the index of the element in the list is used as key.
                If False, the DataFrame columns are the first level of keys in the ParameterSet, and cells might contain dictionaries and lists.
                Defaults to True.
            keep_numeric_only (bool, optional): If True, keep only the numeric columns of the output DataFrame. Default to False.

        Returns:
            DataFrame: the output pandas DataFrame

        Example
        -------
        Suppose we have the following list of ParameterSets:

        .. code-block:: python

            parameterset = [
                {"kpi1": ["A", "B"], "kpi2": {"y1": [1, 2], "y2": [3, 4, 5]}},
                {"kpi1": ["B", "B"], "kpi2": {"y1": [3, 4], "y2": [3, 4, 5]}},
            ]

        If ``flatten=True``, the columns of the output DataFrame are::

            'kpi1.0', 'kpi1.1', 'kpi2.y1.0', 'kpi2.y1.1', 'kpi2.y2.0', 'kpi2.y2.1', 'kpi2.y2.2',

        and the first row of the DataFrame contains values::

            "A", "B", 1, 2, 3, 4, 5

        """

        # convert data to list if it isn't
        data = to_list(data)

        if flatten:
            data = [ParameterSet.flatten(parameterset) for parameterset in data]

        df = pandas.DataFrame(data)

        if keep_numeric_only:
            df = df.select_dtypes(include=number)

        return df
