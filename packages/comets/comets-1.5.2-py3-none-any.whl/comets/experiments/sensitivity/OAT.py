# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pandas as pd
from .sensitivityanalyzer import BaseSensitivityAnalyzer

CHANGE_MODE = ["absolute", "relative", "replacement"]

VARIABLE_TYPES = ["float", "int", "categorical"]


class OAT(BaseSensitivityAnalyzer):
    """
    OAT local sensitivity analyzer
    """

    def __init__(self, variables):
        for variable in variables:
            if "name" not in variable:
                raise ValueError("Variable should have a name")
            if "type" not in variable:
                raise ValueError(
                    "Variable {} should have a type".format(variable["name"])
                )
            if "reference" not in variable:
                raise ValueError(
                    "Variable {} should have a reference".format(variable["name"])
                )
            if "variation" not in variable:
                raise ValueError(
                    "Variable {} should have a variation value (replacement by default)".format(
                        variable["name"]
                    )
                )
            if variable["type"] not in VARIABLE_TYPES:
                raise ValueError(
                    "Type of variable {} should be in {}".format(
                        variable["name"], VARIABLE_TYPES
                    )
                )
            if "change" not in variable:
                variable["change"] = "replacement"

            if variable["change"] not in CHANGE_MODE:
                raise ValueError(
                    "Change mode of variable {} should be in {}".format(
                        variable["name"], CHANGE_MODE
                    )
                )

            if variable["type"] == 'categorical':
                if variable["change"] != "replacement":
                    raise ValueError(
                        "Change mode of the categorical variable {} should be a replacement".format(
                            variable["name"]
                        )
                    )

        self.variables = variables

        # Test if input variables have groups
        self.has_groups = False
        for variable in variables:
            if "group" in variable:
                self.has_groups = True
                break

        # Build parameter, group names, the reference sample (dict : {'x1':reference_x1, 'x2':... }) and the modified one (dict : {'x1':new_value_x1, 'x2':...} )
        self.parameter_names = []
        self.groups = {}
        self.reference_sample = {}
        self.modified_sample = {}
        for variable in variables:
            if "size" in variable:
                list_name = [
                    "{key}.{index}".format(key=variable["name"], index=i)
                    for i in range(variable["size"])
                ]
            else:
                list_name = [variable["name"]]
            for name in list_name:
                self.parameter_names.append(name)
                self.reference_sample[name] = variable["reference"]
                self.modified_sample[name] = self.calculate_modified_value(variable)
                self.groups.setdefault(variable.get("group", name), [])
                self.groups[variable.get("group", name)].append(name)

        # Analyze
        self.expected_number_of_evaluations = self._compute_number_of_evaluations()
        self.samples = self.get_samples()

    @staticmethod
    def calculate_modified_value(variable):
        if variable["change"] == "absolute":
            modified_value = variable["reference"] + variable["variation"]
        elif variable["change"] == "relative":
            modified_value = variable["reference"] * (1 + variable["variation"])
        elif variable["change"] == "replacement":
            modified_value = variable["variation"]
        if variable["type"] == "int":
            return round(modified_value)
        else:
            return modified_value

    def _compute_number_of_evaluations(self):
        # Problem dimension depends on groups
        if self.has_groups:
            dim = len(self.groups) + 1
        else:
            dim = len(set(self.parameter_names)) + 1
        return dim

    def get_samples(self):
        self.samples = [self.reference_sample]
        if self.has_groups:
            for list_parameters in self.groups.values():
                new_sample = self.reference_sample.copy()
                for parameter in list_parameters:
                    new_sample[parameter] = self.modified_sample[parameter]
                self.samples.append(new_sample)

        else:
            for key, value in self.modified_sample.items():
                new_sample = self.reference_sample.copy()
                new_sample[key] = value
                self.samples.append(new_sample)
        return self.samples

    def sensitivity_analysis(self, list_of_results):
        """Compute the OAT sensitivity analysis output quantities.

        Args:
            list_of_results (list): list of the task evaluation results.

        Returns:
            DataFrame: a multi-index DataFrame, with indexes being the output of the task, the input variable,
            and optionally the group if groups are specified. Column names are: "Output", "Group", "Name",
            "ReferenceInputValue", "NewInputValue", "ReferenceOutputValue", "NewOutputValue", "Gap",
            "RelativeChange", "SF", "SSF", "SI".
        """
        results = []
        for kpi in list_of_results[0].keys():
            sum_si = 0
            results_by_group = []
            for i, group in enumerate(list(self.groups.keys())):
                ref_y = list_of_results[0][kpi]
                new_y = list_of_results[i + 1][kpi]
                gap = new_y - ref_y
                sum_si += abs(gap)
                results_by_name = {}
                for name in self.groups[group]:
                    ref_x = self.reference_sample[name]
                    new_x = self.modified_sample[name]

                    try:
                        relative_change = gap / ref_y
                    except ZeroDivisionError:
                        relative_change = float("nan")

                    try:
                        sf = gap / (new_x - ref_x)
                    except (ZeroDivisionError, TypeError):
                        sf = float("nan")

                    try:
                        ssf = sf * (ref_x / ref_y)
                    except (ZeroDivisionError, TypeError):
                        ssf = float("nan")

                    results_by_name = {
                        "Output": kpi,
                        "Group": group,
                        "Name": name,
                        "ReferenceInputValue": ref_x,
                        "NewInputValue": new_x,
                        "ReferenceOutputValue": ref_y,
                        "NewOutputValue": new_y,
                        "Difference": gap,
                        "RelativeChange": relative_change,
                        "SF": sf,
                        "SSF": ssf,
                        "SI": gap,
                    }

                    results_by_group.append(results_by_name)

            for results_by_name in results_by_group:
                try:
                    results_by_name["SI"] = abs(results_by_name["SI"] / sum_si)
                except ZeroDivisionError:
                    results_by_name["SI"] = float("nan")

                results.append(results_by_name)

        if self.has_groups:
            return pd.DataFrame(results).set_index(['Output', 'Group', 'Name'])
        else:
            df = pd.DataFrame(results).set_index(['Output', 'Name'])
            del df['Group']
            return df
