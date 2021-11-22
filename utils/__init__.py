import json
from .millify import millify, prettify
from .time_soup import *

def dump_json(filename: str, obj: dict) -> None:
    """dumps a json file

    Args:
        filename (str): path of json file
        obj (dict): dict object to stored
    """
    with open(filename, "w") as f:
        json.dump(obj, f, indent=4)
        
def load_json(filename: str) -> dict:
    """loads a json file

    Args:
        filename (str): path of json file

    Returns:
        dict: json data
    """
    with open(filename) as f:
        return json.load(f)
