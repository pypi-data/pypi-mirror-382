from typing import Iterable, Dict, Any, List

from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.utils.MultiMap import SetMultimap, ListMultimap
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel, SapioRecordModelException


class RecordModelUtil:
    @staticmethod
    def get_data_record_list(model_list: List[PyRecordModel]) -> List[DataRecord]:
        return [x.get_data_record() for x in model_list]

    @staticmethod
    def multi_map_models_by_data_type_name(models: Iterable[PyRecordModel]) -> SetMultimap[str, PyRecordModel]:
        """
        Given an iterable of record models, returns a set multimap keyed by data type name.
        :param models: The models to be organized.
        """
        ret: SetMultimap[str, PyRecordModel] = SetMultimap()
        for model in models:
            ret.put(model.data_type_name, model)
        return ret

    @staticmethod
    def map_model_by_field_value(models: Iterable[PyRecordModel], field_name: str) -> Dict[Any, PyRecordModel]:
        """
        Given a field name has unique values across this model, return a dictionary map of models by the field name.

        This method will throw exception when the values are not unique.
        """
        ret: Dict[Any, PyRecordModel] = dict()
        for model in models:
            value = model.get_field_value(field_name)
            if value in ret and model != ret.get(value):
                raise SapioRecordModelException("Duplicated value " +
                                                str(value) + " found when processing key " + str(model), model)
            ret[value] = model
        return ret

    @staticmethod
    def multi_map_model_by_field_value(models: Iterable[PyRecordModel], field_name: str) -> \
            ListMultimap[Any, PyRecordModel]:
        """
        Given an iterable of models and a field name, build a multimap keyed by the field value of field name.
        """
        ret: ListMultimap[Any, PyRecordModel] = ListMultimap()
        for model in models:
            value = model.get_field_value(field_name)
            ret.put(value, model)
        return ret

    @staticmethod
    def get_value_list(models: List[PyRecordModel], field_name: str) -> List[Any]:
        """
        Get a list of values in order of original model list.
        """
        ret: List[Any] = list()
        for model in models:
            ret.append(model.get_field_value(field_name))
        return ret

    @staticmethod
    def validate_backing_records(models: Iterable[PyRecordModel]):
        """
        Validate the backing records of all record models in the list, to make sure they have already been submitted with a valid Record ID.
        """
        for model in models:
            if model.record_id < 0 or not model.get_data_record():
                raise ValueError("Model " + str(model) + " does not have a backing record.")

    @staticmethod
    def map_model_by_record_id(to_load_list: Iterable[PyRecordModel]):
        """
        Map each model by their associated Record ID.
        """
        ret: dict[int, PyRecordModel] = dict()
        for model in to_load_list:
            ret[model.record_id] = model
        return ret
