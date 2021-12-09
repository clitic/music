import json
import pickle
from typing import Any, Optional


def dump_json(filename: str, obj: dict, pretty: Optional[bool] = False) -> None:
    """dumps a json file

    Args:
        filename (str): path of json file
        obj (dict): dict object to stored
        pretty (Optional[bool], optional): prettify json. Defaults to False.
    """
    with open(filename, "w") as f:
        if not pretty:
            json.dump(obj, f)
        else:
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

def dump_pickle(filename: str, obj: Any) -> None:
    """dump a object pickle

    Args:
        filename (str): path for pickle file
        obj (Any): object to serialize
    """
    with open(filename, "wb") as f:
        pickle.dump(obj, f)

def load_pickle(filename: str) -> Any:
    """load a pickle file

    Args:
        filename (str): path of pickled file

    Returns:
        Any: loaded object
    """
    with open(filename, "rb") as f:
        return pickle.load(f)
