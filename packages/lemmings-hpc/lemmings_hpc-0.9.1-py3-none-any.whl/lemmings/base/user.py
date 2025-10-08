""" user parameters"""

import yaml
import json
from collections import namedtuple


def _convert(dictionary):
    """
    *Convert a dict( ) to a NamedTuple( ).*
    """
    return namedtuple("NamedTupleJJH", dictionary.keys())(**dictionary)


def get_user_params(workflow_input_file):
    """
    Get the user parameters and generate a NamedTuple with it
    """

    with open(workflow_input_file, "r") as fin:
        tmp = yaml.load(fin, Loader=yaml.SafeLoader)

    if tmp is None:
        raise ValueError(f"WOrkflow file {workflow_input_file} is empty")

    try:
        farm_file = tmp["farming"]["parameter_file"]
    except KeyError:
        pass
    else:
        with open(farm_file, "r") as fin:
            farming_params = json.load(fin)

        del tmp["farming"]["parameter_file"]
        tmp["farming"]["parameter_array"] = farming_params
    return _convert(tmp)
