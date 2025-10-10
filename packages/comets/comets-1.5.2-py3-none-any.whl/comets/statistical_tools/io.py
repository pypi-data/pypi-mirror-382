import json
from pathlib import Path
import importlib

from ..utilities.utilities import to_list
from ..utilities import get_logger
from .sampling import CustomSampling

SERIALIZABLE_CLASSES = [
    "Histogram",
    "KDE",
    "EmpiricalSampler",
]


def dump_sampling_list(list_of_sampling_dictionaries, filepath, indent=4):
    """Serialize and dump a list of sampling dictionaries into a json-formatted file.

    Args:
        list_of_sampling_dictionaries (list): list of sampling dictionaries in the CoMETS format.
        filepath (str): path to the output json file.
        indent (int, optional): Indentation for the json file. Defaults to 4.
    """
    logger = get_logger(__name__)

    # Convert to list
    list_to_dump = to_list(list_of_sampling_dictionaries)

    def serialize_variable(variable):
        if isinstance(variable["sampling"], CustomSampling):
            # Copy in order not to modify the initial dict
            variable = variable.copy()
            try:
                variable["sampling"] = variable["sampling"]._serialize()
            except Exception as e:
                logger.error(
                    f"When dumping into file {filepath}: error trying to serialize object {variable['sampling']} of variable {variable}."
                )
                obj_type = type(variable["sampling"])
                if obj_type not in SERIALIZABLE_CLASSES:
                    raise TypeError(
                        f"Serialization not supported for object type {obj_type}. Supported object types are: {SERIALIZABLE_CLASSES}."
                    )
                else:  # pragma: no cover
                    # In case of an unknown error, reraise
                    raise e
        elif isinstance(variable["sampling"], str):
            pass
        else:
            logger.error(
                f"When dumping into file {filepath}: object {variable['sampling']} of variable {variable} does not have a valid type."
            )
            raise TypeError(
                f"Invalid type for 'sampling' value {variable['sampling']}. 'sampling' should contain either a string or on of the following object types: {SERIALIZABLE_CLASSES}"
            )
        return variable

    list_to_dump = [serialize_variable(variable) for variable in list_to_dump]

    filepath = Path(filepath)
    with filepath.open("w") as f:
        json.dump(list_to_dump, f, indent=indent)


def load_sampling_list(filepath):
    """Load a json-formatted file containing a list of sampling dictionaries.

    Args:
        filepath (str): path to the json file.

    Returns:
        list: list of sampling dictionaries in the CoMETS format.
    """
    logger = get_logger(__name__)

    filepath = Path(filepath)
    with filepath.open("r") as f:
        data = json.load(f)

    def unserialize_variable(obj):
        if isinstance(obj["sampling"], dict):
            class_name = obj["sampling"].get("class")
            if class_name not in SERIALIZABLE_CLASSES:
                logger.error(
                    f"Error when loading object {obj} in file {filepath}: invalid object type {class_name}."
                )
                raise TypeError(
                    f"Unknown object type {class_name} for {obj['sampling']}. Supported object types are: {SERIALIZABLE_CLASSES}."
                )
            cls = getattr(importlib.import_module('comets'), class_name)
            obj["sampling"] = cls._deserialize(obj["sampling"])
        return obj

    sampling_list = [unserialize_variable(obj) for obj in data]
    return sampling_list
