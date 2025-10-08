from __future__ import annotations

from enum import Enum
from typing import Optional, List, Dict, Any

from sapiopylib.rest.pojo.DataRecord import DataRecord


class RuleRelationType(Enum):
    """
    Specify a relation type from a record to a base record. This is used inside a rule context.
    """
    PARENT = "Parent"
    CHILD = "Child"
    ANCESTOR = "Ancestor"
    DESCENDANT = "Descendant"
    NONE = "None"

    java_enum: str

    def __init__(self, java_enum: str):
        self.java_enum = java_enum

    def to_pojo(self) -> str:
        return self.java_enum


class VeloxRuleElnEntry:
    """
    Describes an ELN entry that is part of the condition that triggered the rule.

    Attributes:
        entry_name: The name of the ELN entry.
        data_type_name: The data type name of the ELN entry.
    """
    entry_name: str
    data_type_name: Optional[str]

    def __init__(self, entry_name: str, data_type_name: Optional[str] = None):
        self.entry_name = entry_name
        self.data_type_name = data_type_name

    def to_json(self) -> Dict[str, Any]:
        return {
            'entryName': self.entry_name,
            'dataTypeName': self.data_type_name
        }

    def __eq__(self, other):
        if not isinstance(other, VeloxRuleElnEntry):
            return False
        return self.entry_name == other.entry_name and self.data_type_name == other.data_type_name

    def __hash__(self):
        return hash((self.entry_name, self.data_type_name))


class VeloxRuleType:
    data_type_name: Optional[str]
    source_entry: Optional[VeloxRuleElnEntry]
    relation_type: RuleRelationType
    __inner_type: Optional[VeloxRuleType]

    def __init__(self, data_type_name: str, source_entry: Optional[VeloxRuleElnEntry], relation_type: RuleRelationType,
                 inner_type: VeloxRuleType):
        self.data_type_name = data_type_name
        self.source_entry = source_entry
        self.relation_type = relation_type
        # PR-53266: Don't check for circular dependencies; the server already did that for us.
        self.__inner_type = inner_type

    def get_inner_type(self) -> Optional[VeloxRuleType]:
        """
        Get inner rule type for this rule type.
        """
        return self.__inner_type

    def __eq__(self, other):
        if not isinstance(other, VeloxRuleType):
            return False
        return self.data_type_name == other.data_type_name and self.source_entry == other.source_entry and \
            self.__inner_type == other.__inner_type and self.relation_type == other.relation_type

    def __hash__(self):
        return hash((self.data_type_name, self.source_entry, self.__inner_type, self.relation_type))

    def __str__(self):
        ret: str = ""
        if self.relation_type == RuleRelationType.PARENT:
            ret += "(Parent)"
        elif self.relation_type == RuleRelationType.CHILD:
            ret += "(Child)"
        elif self.relation_type == RuleRelationType.ANCESTOR:
            ret += "(Ancestor)"
        elif self.relation_type == RuleRelationType.DESCENDANT:
            ret += "(Descendant)"
        if self.data_type_name is not None:
            ret += self.data_type_name
        if self.__inner_type is not None:
            ret += str(self.__inner_type)
        return ret


class VeloxTypedRuleResult:
    """
    Holds rule results for a single rule-annotated object such as a record ID or an entry name.
    """
    velox_rule_type: VeloxRuleType
    data_records: List[DataRecord]

    def __init__(self, velox_rule_type: VeloxRuleType, data_records: List[DataRecord]):
        self.velox_rule_type = velox_rule_type
        self.data_records = data_records


class ElnEntryRecordResult:
    record_id: int
    rule_result_list: List[VeloxTypedRuleResult]

    def __init__(self, record_id: int, rule_result_list: List[VeloxTypedRuleResult]):
        self.record_id = record_id
        self.rule_result_list = rule_result_list


class VeloxTypeRuleFieldMapResult:
    velox_type_pojo: VeloxRuleType
    field_map_list: List[Dict[str, Any]]

    def __init__(self, velox_type_pojo: VeloxRuleType, field_map_list: List[Dict[str, Any]]):
        self.velox_type_pojo = velox_type_pojo
        self.field_map_list = field_map_list

    def __str__(self):
        return str(self.field_map_list)

    def __repr__(self):
        return str(self.field_map_list)

    @staticmethod
    def get_field_map_list(velox_type: VeloxRuleType,
                           velox_type_rule_field_map_result_list: List[VeloxTypeRuleFieldMapResult]):
        ret: List[Dict[str, Any]] = []
        for result in velox_type_rule_field_map_result_list:
            if velox_type == result.velox_type_pojo:
                ret.extend(result.field_map_list)
        return ret

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> VeloxTypeRuleFieldMapResult:
        velox_type_pojo: VeloxRuleType = VeloxRuleParser.parse_velox_rule_type(json_dct.get("veloxTypePojo"))
        field_map_list: List[Dict[str, Any]] = json_dct.get("fieldMapSet")
        return VeloxTypeRuleFieldMapResult(velox_type_pojo, field_map_list)


class ElnEntryFieldMapResult:
    record_id: int
    velox_type_rule_field_map_result_list: List[VeloxTypeRuleFieldMapResult]

    def __init__(self, record_id: int, velox_type_rule_field_map_result_list: List[VeloxTypeRuleFieldMapResult]):
        self.record_id = record_id
        self.velox_type_rule_field_map_result_list = velox_type_rule_field_map_result_list

    def __str__(self):
        return str(self.record_id) + ": " + str(self.velox_type_rule_field_map_result_list)

    def __repr__(self):
        return str(self.record_id) + ": " + str(self.velox_type_rule_field_map_result_list)

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> ElnEntryFieldMapResult:
        record_id: int = json_dct.get("record_id")
        velox_type_rule_field_map_result_list: List[VeloxTypeRuleFieldMapResult] = json_dct.get(
            "veloxTypeRuleFieldMapResultList")
        return ElnEntryFieldMapResult(record_id, velox_type_rule_field_map_result_list)



class VeloxRuleParser:
    @staticmethod
    def parse_eln_record_result(json_dct: Dict[str, Any]) -> ElnEntryRecordResult:
        rule_pojo_list: List[Dict[str, Any]] = json_dct.get('veloxTypeRuleResultList')
        rule_result_list: List[VeloxTypedRuleResult] = [VeloxRuleParser.parse_velox_typed_rule_result(x)
                                                        for x in rule_pojo_list]
        record_id: int = json_dct.get('recordId')
        return ElnEntryRecordResult(record_id, rule_result_list)

    @staticmethod
    def parse_velox_typed_rule_result(json_dct: Dict[str, Any]) -> VeloxTypedRuleResult:
        rule_type: VeloxRuleType = VeloxRuleParser.parse_velox_rule_type(json_dct.get('veloxTypePojo'))
        data_records: List[DataRecord] = [DataRecord.from_json(x) for x in json_dct.get('dataRecordPojoSet')]
        return VeloxTypedRuleResult(rule_type, data_records)

    @staticmethod
    def parse_eln_rule_entry(json_dct: Dict[str, Any]) -> VeloxRuleElnEntry:
        entry_name: str = json_dct.get('entryName')
        data_type_name: Optional[str] = json_dct.get('dataTypeName')
        return VeloxRuleElnEntry(entry_name, data_type_name=data_type_name)

    @staticmethod
    def parse_relation_type(json_value: Optional[str]) -> RuleRelationType:
        if json_value is None or len(json_value) == 0:
            return RuleRelationType.NONE
        return RuleRelationType[json_value.upper()]

    @staticmethod
    def parse_velox_rule_type(json_dct: Dict[str, Any]) -> VeloxRuleType:
        data_type_name: Optional[str] = json_dct.get('dataTypeName')
        source_entry: Optional[VeloxRuleElnEntry] = None
        if json_dct.get('sourceEntry') is not None:
            source_entry = VeloxRuleParser.parse_eln_rule_entry(json_dct.get('sourceEntry'))
        relation_type: RuleRelationType = VeloxRuleParser.parse_relation_type(json_dct.get('relationType'))
        inner_type: Optional[VeloxRuleType] = None
        if json_dct.get('veloxType') is not None:
            inner_type = VeloxRuleParser.parse_velox_rule_type(json_dct.get('veloxType'))
        return VeloxRuleType(data_type_name, source_entry, relation_type, inner_type)
