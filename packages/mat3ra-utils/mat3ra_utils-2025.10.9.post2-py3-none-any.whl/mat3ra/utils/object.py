import copy
import json
from typing import Any, Dict, List

import numpy as np
from mat3ra.utils.mixins import RoundNumericValuesMixin


def omit(obj: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    return {k: v for k, v in obj.items() if k not in keys}


def set_object_key(obj: Dict[str, Any], key: str, value: Any) -> None:
    obj[key] = value


def clone_shallow(obj: Any) -> Any:
    return copy.copy(obj)


def clone_deep(obj: Any) -> Any:
    return copy.deepcopy(obj)


def get(config: Dict, path: str = "", separator: str = "/") -> Any:
    """
    Get value by deep/nested path with separator "/ or "."
    """
    segments = path.strip(separator).split(separator)
    for segment in segments:
        config = config.get(segment, {})
    return config


class AttributeDict(dict):
    """
    Subclass of dict that allows read-only attribute-like access to dictionary key/values
    """

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            return super(AttributeDict, self).__getattribute__(name)


class NumpyNDArrayRoundEncoder(json.JSONEncoder, RoundNumericValuesMixin):
    def default(self, obj: Any) -> Any:
        """
        Convert Numpy NDArray to list and round numeric values.
        Args:
            obj (Any): The object to convert.

        Returns:
            tuple: A tuple containing the converted key and the rounded value.
        """
        if isinstance(obj, np.ndarray):
            return self.round_array_or_number(obj.tolist())
        if isinstance(obj, (int, float)):
            return self.round_array_or_number(obj)
        return json.JSONEncoder.default(self, obj)
