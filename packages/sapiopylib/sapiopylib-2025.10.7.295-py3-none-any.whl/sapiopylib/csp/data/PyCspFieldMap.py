from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, List


class CspDataException(Exception):
    """
    This is thrown when there is anything explicitly wrong detected while converting CSP data in Python.
    """
    message: str

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class PyCspObject(ABC):
    """
    This represents a CspFieldMap subclass with easy access methods.
    """
    _backing_model: Dict[str, Any]
    KEYLESS_MODEL_KEY = "Keyless"

    def __init__(self, backing_model: Dict[str, Any] = None):
        if backing_model is None:
            backing_model = dict()
        self._backing_model = backing_model

    def to_json(self) -> Dict[str, Any]:
        return self._backing_model

    def __getitem__(self, key: str):
        return self._backing_model.get(key)

    def __setitem__(self, key: str, value: Any):
        return self._backing_model.__setitem__(key, value)

    def __str__(self):
        return self._backing_model.__str__()

    def __hash__(self):
        return hash(self.get_model_key())

    @property
    def backing_model(self):
        return self._backing_model

    def __eq__(self, other):
        if other is None:
            return self is None
        if not isinstance(other, PyCspObject):
            return False
        return self.get_model_key() == other.get_model_key()

    def get_string_value(self, field_name: str, default_value: Optional[str] = None) -> Optional[str]:
        ret = self._backing_model.get(field_name)
        if ret is None:
            return default_value
        return str(ret)

    def get_int_value(self, field_name: str, default_value: Optional[float] = None) -> Optional[int]:
        ret = self._backing_model.get(field_name)
        if ret is None:
            return default_value
        return int(ret)

    def get_float_value(self, field_name: str, default_value: Optional[float] = None) -> Optional[float]:
        ret = self._backing_model.get(field_name)
        if ret is None:
            return default_value
        return float(ret)

    def get_boolean_value(self, field_name: str, default_value: Optional[bool] = None) -> Optional[bool]:
        ret = self._backing_model.get(field_name)
        if ret is None:
            return default_value
        return bool(ret)

    def set_csp_data(self, field_name: str, csp_data: Optional[PyCspObject]):
        if csp_data is None:
            self[field_name] = None
        else:
            self[field_name] = csp_data._backing_model

    def get_csp_data(self, field_name: str, obj_type: Type[PyCspObject]):
        field_map = self[field_name]
        if field_map is None:
            return None
        return obj_type(field_map)

    def set_csp_data_list(self, field_name: str, csp_data: Optional[List[PyCspObject]]):
        if csp_data is None:
            self[field_name] = None
        else:
            self[field_name] = [x._backing_model for x in csp_data]

    def get_csp_data_list(self, field_name: str, obj_type: Type[PyCspObject]):
        field_map_list = self[field_name]
        if field_map_list is None:
            return None
        ret = list()
        for field_map in field_map_list:
            if field_map is None:
                ret.append(None)
            else:
                ret.append(obj_type(field_map))
        return ret

    @abstractmethod
    def get_model_key(self) -> str:
        """
        The model key is the test for equality inside a UI multi-element store, such as in a live grid or a pick list.
        """
        pass
