from __future__ import annotations

from enum import Enum
from typing import Optional, Dict, Any, List
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser


class AccessionCriteriaType(Enum):
    """
    Accessioning cache type.
    """
    SYSTEM = 1
    """Global accessioning. Note that the Accession Service from Sapio Foundations does not use this cache."""
    DATA_FIELD = 2
    """Cached per data type's maximum value of a data field."""


class AbstractAccessionCriteriaPojo:
    """
    Describes a criteria for server accession service request, in order to obtain a list of accession IDs.
    """
    criteria_type: AccessionCriteriaType
    """The type of accessioning that is being requested."""
    prefix: Optional[str] = None
    """If specified, the value returned will have this starting text."""
    suffix: Optional[str] = None
    """If specified, the value returned will have this trailing text."""
    sequence_key: Optional[str]
    """The key of the sequence. Each key holds separate cache of values. At minimum, for requests with different prefix,
    suffix, data type name, or data field name, they should have different keys."""
    initial_sequence_value: int = 1
    """If there are no value at all among all records in the field, start with this value."""

    def __init__(self, criteria_type: AccessionCriteriaType, sequence_key: str):
        """
        INTERNAL USE ONLY. Use one of the subclasses.
        """
        self.criteria_type = criteria_type
        self.sequence_key = sequence_key

    def from_pojo(self, json_dct: dict) -> None:
        self.prefix = json_dct.get('prefix')
        self.suffix = json_dct.get('suffix')
        self.sequence_key = json_dct.get('sequenceKey')
        self.initial_sequence_value = int(json_dct.get('initialSequenceValue'))

    def to_pojo(self) -> Dict[str, Any]:
        return {
            'criteriaType': self.criteria_type.name,
            'prefix': self.prefix,
            'suffix': self.suffix,
            'sequenceKey': self.sequence_key,
            'initialSequenceValue': self.initial_sequence_value
        }


class AccessionSystemCriteriaPojo(AbstractAccessionCriteriaPojo):
    """
    Describes request to accession a global (unrelated to data records) accession IDs.
    """
    def __init__(self, sequence_key: str):
        """
        Accession by sequence order in sequence key, regardless of existing record values.

        :param sequence_key: The sequence table ID to accession for. IDs in the same sequence will not duplicate.
        """
        super().__init__(AccessionCriteriaType.SYSTEM, sequence_key)


class AccessionDataFieldCriteriaPojo(AbstractAccessionCriteriaPojo):
    """
    Describes request to accession data record's IDs for a data field under a specified format.
    """
    data_type_name: str
    """The name of the data type that the data field name is under."""
    data_field_name: str
    """The data field name of the field to accession. This field must have the "Unique" boolean set to true in the
    data designer."""

    def __init__(self, data_type_name: str, data_field_name: str, sequence_key: str):
        """
        Accession for a data field's value

        :param data_type_name: The data type name to accession for.
        :param data_field_name: The data field name to accession for. This field must have the "Unique" boolean set
            to true in the data designer.
        :param sequence_key: The sequence key that must be unique for the same formatting (prefix, suffix) of IDs.
        """
        super().__init__(AccessionCriteriaType.DATA_FIELD, sequence_key)
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name

    def from_pojo(self, json_dct: dict):
        super().from_pojo(json_dct)
        self.data_type_name = json_dct.get('dataTypeName')
        self.data_field_name = json_dct.get('dataFieldName')

    def to_pojo(self) -> Dict[str, Any]:
        ret = super().to_pojo()
        ret['dataTypeName'] = self.data_type_name
        ret['dataFieldName'] = self.data_field_name
        return ret


class AccessionManager:
    """
    Accession new IDs for the system to be consistent with plugin logic.
    """
    user: SapioUser
    __instances: WeakValueDictionary[SapioUser, AccessionManager] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, user: SapioUser):
        """
        Observes singleton pattern per record model manager object.

        :param user: The user that will make the webservice request to the application.
        """
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, user: SapioUser):
        """
        Obtains REST accession manager to perform accessioning operations.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def accession_for_system(self, num_to_accession: int, criteria: AccessionSystemCriteriaPojo) -> List[str]:
        """
        Accession IDs that are not tied to a specific data type and field.

        If this is the first time that the system is being accessioned with these criteria, the returned results
        will start from the initial_sequence_value of the criteria. Otherwise, they will continue on from the previous
        value.

        :param num_to_accession: The number of new IDs to return.
        :param criteria: The criteria by which the accession IDs will be generated.
        :return: A list of unique IDs that will never be generated with this method again for the same criteria.
        """
        sub_path = self.user.build_url(['accession', 'accessionForSystem'])
        param = {'numToAccession': num_to_accession}
        payload = criteria.to_pojo()
        response = self.user.post(sub_path, param, payload)
        self.user.raise_for_status(response)
        return response.json()

    def accession_for_field(self, num_to_accession: int, criteria: AccessionDataFieldCriteriaPojo) -> List[str]:
        """
        Accession IDs that are tied to a specific data type and data field. The data field definition of the field that
        is used must have the "Unique" boolean set to true in the data designer.

        If this is the first time that this field is being accessioned with the given criteria, the returned results
        will use the maximum value of the field across the records in the system that matches the criteria and add 1.
        If there are no values that match the criteria, then the initial_sequence_value from the criteria is used. For
        all subsequent calls, the returned results will continue on from the previous value.

        :param num_to_accession: The number of new IDs to return.
        :param criteria: The criteria by which the accession IDs will be generated.
        :return: A list of unique IDs that will never be generated with this method again for the same criteria.
        """
        sub_path = self.user.build_url(['accession', 'accessionForField'])
        param = {'numToAccession': num_to_accession}
        payload = criteria.to_pojo()
        response = self.user.post(sub_path, param, payload)
        self.user.raise_for_status(response)
        return response.json()
