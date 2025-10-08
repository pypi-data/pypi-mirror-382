from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Any, List, Optional, Dict

import pandas as pd

from sapiopylib.rest.pojo.DataRecordPaging import AbstractPageCriteria
from sapiopylib.rest.pojo.Sort import SortDirection, SortDirectionParser
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType


class QueryRestriction(Enum):
    """
    Should the report's initial retrieval of records based off of a particular record?
    If so, what is the relation of the results to this record? Default is not to restrict (QUERY_ALL).
    """
    QUERY_ALL = 0
    QUERY_CHILDREN = 1
    QUERY_PARENTS = 2
    QUERY_DESCENDANTS = 3
    QUERY_ANCESTORS = 4

    query_code: int

    def __init__(self, query_code: int):
        self.query_code = query_code


class CompositeTermOperation(Enum):
    """
    A composite report term describes an operation to be applied to one or two terms.

    The operations possible are: AND, OR, NOT.

    The operation "NOT" should not be used anymore, as there is a negated flag on each report term.
    """
    AND_OPERATOR = 4, "AND", "AND", "AND"
    OR_OPERATOR = 5, "OR", "OR", "OR"
    NOT_OPERATOR = 6, "NOT", "NOT", "NOT"

    op_code: int
    op_string: str
    html_op_string: str
    display_string: str

    def __init__(self, op_code: int, op_string: str, html_op_string: str, display_string: str):
        self.op_code = op_code
        self.op_string = op_string
        self.html_op_string = html_op_string
        self.display_string = display_string

    def __str__(self):
        return self.display_string


class RawTermOperation(Enum):
    """
    A raw term operation compares a term value with a raw value.

    The possible operations are: >, <, ==, !=, >=, <=
    """
    GREATER_THAN_OPERATOR = 0, ">", "&gt;", ">"
    LESS_THAN_OPERATOR = 1, "<", "&lt;", "<"
    EQUAL_TO_OPERATOR = 2, "=", "=", "="
    NOT_EQUAL_TO_OPERATOR = 3, "!=", "&ne;", "\u2260"
    GREATER_THAN_OR_EQUAL_OPERATOR = 7, ">=", "&ge;", "\u2265"
    LESS_THAN_OR_EQUAL_OPERATOR = 8, "<=", "&le;", "\u2264"

    op_code: int
    op_string: str
    html_op_string: str
    display_string: str

    def __init__(self, op_code: int, op_string: str, html_op_string: str, display_string: str):
        self.op_code = op_code
        self.op_string = op_string
        self.html_op_string = html_op_string
        self.display_string = display_string

    def __str__(self):
        return self.display_string


class TermType(Enum):
    """
    The type of custom report term.
    RAW_TERM: you can think of this as a leaf node in the term tree.

    COMPOSITE_TERM: you can think of this as a parent of two terms.

    NULL_TERM: Not used anymore.
    """
    RAW_TERM = 0, 0
    JOIN_TERM = 1, 0
    COMPOSITE_TERM = 2, 1
    NULL_TERM = 3, 2

    term_code: int
    internal_code: int

    def __init__(self, internal_code: int, term_code: int):
        self.internal_code = internal_code
        self.term_code = term_code

    def get_term_code(self) -> int:
        """
        Get the term code used in Sapio API for this term.
        """
        return self.term_code


class AbstractReportTerm(ABC):
    """
    A report term inside a custom report provides a single condition or logical operator in a single WHERE clause.
    This is simulating abstract class in Java. Must use a subclass. (Python does not have abstract class)
    """
    term_type: TermType
    negated: bool

    def __init__(self, term_type: TermType, negated: bool):
        self.term_type = term_type
        self.negated = negated

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = {
            'termType': self.term_type.name,
            'negated': self.negated
        }
        return ret

    @classmethod
    def from_json(cls, json_dct: Dict[str, Any]) -> AbstractReportTerm:
        term_type_name = json_dct.get('termType')
        term_type = TermType[term_type_name]
        if term_type == TermType.RAW_TERM:
            return RawReportTerm.from_json(json_dct)
        elif term_type == TermType.COMPOSITE_TERM:
            return CompositeReportTerm.from_json(json_dct)
        elif term_type == TermType.JOIN_TERM:
            return FieldCompareReportTerm.from_json(json_dct)
        raise ValueError("Unsupported term type: " + term_type_name)


class RawReportTerm(AbstractReportTerm):
    """
    A raw report term describes an operation to be performed on result data.
    """
    data_type_name: str
    data_field_name: str
    term_operation: RawTermOperation
    trim: bool
    value: str

    def __eq__(self, other):
        if not isinstance(other, RawReportTerm):
            return False
        return self.data_type_name == other.data_type_name and self.data_field_name == other.data_field_name \
            and self.term_operation == other.term_operation and self.trim == other.trim and self.value == other.value

    def __init__(self, data_type_name: str, data_field_name: str, term_operation: RawTermOperation, value: str,
                 trim: bool = False, is_negated: bool = False):
        """
        Create a new raw report term for a data field.
        :param data_type_name: The data type name of the term.
        :param data_field_name: The data field name of the term.
        :param term_operation: The operator of the term.
        """
        super().__init__(TermType.RAW_TERM, is_negated)
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name
        self.term_operation = term_operation
        self.value = value
        self.trim = trim

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['dataTypeName'] = self.data_type_name
        ret['dataFieldName'] = self.data_field_name
        ret['termOperation'] = self.term_operation.name
        ret['trim'] = self.trim
        ret['value'] = self.value
        return ret

    def __str__(self):
        return self.data_type_name + '.' + self.data_field_name + str(self.term_operation) + self.value

    @classmethod
    def from_json(cls, json_dct: Dict[str, Any]) -> AbstractReportTerm:
        negated = bool(json_dct.get('negated'))
        data_type_name: str = json_dct.get('dataTypeName')
        data_field_name: str = json_dct.get('dataFieldName')
        term_operation: RawTermOperation = RawTermOperation[json_dct.get('termOperation')]
        trim: bool = bool(json_dct.get('trim'))
        value: str = json_dct.get('value')
        ret = RawReportTerm(data_type_name, data_field_name, term_operation, value, trim=trim, is_negated=negated)
        return ret


class CompositeReportTerm(AbstractReportTerm):
    """
     A composite custom report term describes a logical operation on one or two report terms.

     When operation is (AND, OR), we expect both children to be non-trivial.

     The operation "NOT" should not be used anymore, as there is a negated flag on each report term.
    """
    term_operation: CompositeTermOperation
    left_child: AbstractReportTerm
    right_child: AbstractReportTerm

    def __eq__(self, other):
        if not isinstance(other, CompositeReportTerm):
            return False
        return self.left_child == other.left_child and self.term_operation == other.term_operation and self.right_child == other.right_child

    def __init__(self, left_child: AbstractReportTerm, term_operation: CompositeTermOperation,
                 right_child: AbstractReportTerm, is_negated: bool = False):
        """
         A composite custom report term describes a logical operation on two report terms.
        :param term_operation: The operation to join the left and right child
        :param left_child: One child term
        :param right_child: The other child term
        """
        super().__init__(TermType.COMPOSITE_TERM, is_negated)
        self.term_operation = term_operation
        self.left_child = left_child
        self.right_child = right_child

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['termOperation'] = self.term_operation.name
        ret['leftChild'] = self.left_child.to_json()
        ret['rightChild'] = self.right_child.to_json()
        return ret

    def __str__(self):
        return "[" + str(self.left_child) + "]" + str(self.term_operation) + "[" + str(self.right_child) + "]"

    @classmethod
    def from_json(cls, json_dct: Dict[str, Any]) -> AbstractReportTerm:
        negated = bool(json_dct.get('negated'))
        term_operation: CompositeTermOperation = CompositeTermOperation[json_dct.get('termOperation')]
        left_child = AbstractReportTerm.from_json(json_dct.get('leftChild'))
        right_child = AbstractReportTerm.from_json(json_dct.get('rightChild'))
        ret = CompositeReportTerm(left_child, term_operation, right_child, is_negated=negated)
        return ret


class FieldCompareReportTerm(AbstractReportTerm):
    """
    This is the special RAW term in Java API that represents "Join" of two types by field values.
    """
    left_data_type_name: str
    left_data_field_name: str
    term_operation: RawTermOperation
    right_data_type_name: str
    right_data_field_name: str
    trim: bool

    def __eq__(self, other):
        if not isinstance(other, FieldCompareReportTerm):
            return False
        return self.left_data_type_name == other.left_data_type_name and \
            self.left_data_field_name == other.left_data_field_name and \
            self.term_operation == other.term_operation and \
            self.right_data_type_name == other.right_data_type_name and \
            self.right_data_field_name == other.right_data_field_name and \
            self.trim == other.trim

    def __init__(self, left_data_type_name: str, left_data_field_name: str, term_operation: RawTermOperation,
                 right_data_type_name: str, right_data_field_name: str, trim: bool = False, is_negated: bool = False):
        """
        This is the special RAW term in Java API that represents "Join" of two types by field values.
        :param left_data_type_name: Join's left data type name
        :param left_data_field_name: Join's left data field name
        :param term_operation: Inner join operator.
        :param right_data_type_name: Join's right data type name
        :param right_data_field_name: Join's right data field name
        :param trim: Whether to trim string before processing.
        """
        super().__init__(TermType.JOIN_TERM, False)
        self.left_data_type_name = left_data_type_name
        self.left_data_field_name = left_data_field_name
        self.term_operation = term_operation
        self.right_data_type_name = right_data_type_name
        self.right_data_field_name = right_data_field_name
        self.trim = trim
        self.negated = is_negated

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['termOperation'] = self.term_operation.name
        ret['leftDataTypeName'] = self.left_data_type_name
        ret['leftDataFieldName'] = self.left_data_field_name
        ret['rightDataTypeName'] = self.right_data_type_name
        ret['rightDataFieldName'] = self.right_data_field_name
        ret['trim'] = self.trim
        return ret

    def __str__(self):
        return '[' + self.left_data_type_name + '.' + self.left_data_field_name + ']' + str(self.term_operation) + \
               '[' + self.right_data_type_name + '.' + self.right_data_field_name + ']'

    @classmethod
    def from_json(cls, json_dct: Dict[str, Any]) -> AbstractReportTerm:
        negated = bool(json_dct.get('negated'))
        left_data_type_name: str = json_dct.get('leftDataTypeName')
        left_data_field_name: str = json_dct.get('leftDataFieldName')
        term_operation: RawTermOperation = RawTermOperation[json_dct.get('termOperation')]
        right_data_type_name: str = json_dct.get('rightDataTypeName')
        right_data_field_name: str = json_dct.get('rightDataFieldName')
        trim: bool = bool(json_dct.get('trim'))
        return FieldCompareReportTerm(left_data_type_name, left_data_field_name, term_operation, right_data_type_name,
                                      right_data_field_name, trim, negated)


class ReportColumn:
    """
    Represents a column in a custom report POJO.

    Attributes:
        data_type_name: The data type name of the report column.
        data_field_name: The data field name of the report column.
        field_type: The type of this data field.
        sort_order: The sorting priority among columns in a report, if this column is sorting.
        sort_direction: Is this a sorting column? If so, is it ascending or descending?
        group_by: Is the field used for group by operation?
    """
    data_type_name: str
    data_field_name: str
    field_type: FieldType
    sort_order: int
    sort_direction: Optional[SortDirection]
    group_by: bool

    def __eq__(self, other):
        if not isinstance(other, ReportColumn):
            return False
        if not self.data_type_name == other.data_type_name:
            return False
        if not self.data_field_name == other.data_field_name:
            return False
        if not self.field_type == other.field_type:
            return False
        if not self.sort_order == other.sort_order:
            return False
        if not self.sort_direction == other.sort_direction:
            if self.sort_direction is None or self.sort_order == SortDirection.NONE:
                if not (other.sort_direction is None or other.sort_direction == SortDirection.NONE):
                    return False
            else:
                return False
        if not self.group_by == other.group_by:
            return False
        return True

    def __hash__(self):
        return hash((self.data_type_name, self.data_field_name, self.field_type, self.sort_order, self.group_by))

    def __init__(self, data_type_name: str, data_field_name: str, field_type: FieldType,
                 sort_order: int = 0, sort_direction: Optional[SortDirection] = None, group_by: bool = False):
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name
        self.field_type = field_type
        self.sort_order = sort_order
        self.sort_direction = sort_direction
        self.group_by = group_by

    def to_pojo(self) -> Dict[str, Any]:
        sort_direction: Optional[str] = SortDirectionParser.direction_to_json(self.sort_direction, True)
        return {
            'dataTypeName': self.data_type_name,
            'dataFieldName': self.data_field_name,
            'fieldType': self.field_type.name,
            'sortOrder': self.sort_order,
            'sortDirection': sort_direction,
            'groupBy': self.group_by
        }

    def __str__(self):
        return self.data_type_name + "." + self.data_field_name

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> ReportColumn:
        data_type_name: str = json_dct.get('dataTypeName')
        data_field_name: str = json_dct.get('dataFieldName')
        field_type: FieldType = FieldType[json_dct.get('fieldType')]
        sort_order: int = int(json_dct.get('sortOrder'))
        sort_order_direction_name = json_dct.get('sortDirection')
        group_by: bool = json_dct.get("groupBy")
        sort_direction = SortDirectionParser.parse_sort_direction(sort_order_direction_name)
        return ReportColumn(data_type_name, data_field_name, field_type, sort_order, sort_direction, group_by)


class RelatedRecordCriteria:
    """
    Describes additional criteria that the report's data must be related somehow to a single record. This is optional.
    """
    related_record_id: Optional[int]
    related_record_type: Optional[str]
    query_restriction: QueryRestriction

    def __init__(self, query_restriction: QueryRestriction,
                 related_record_id: Optional[int] = None, related_record_type: Optional[str] = None):
        """
        Describes additional criteria that the report's data must be related somehow to a single record.
        This is optional.
        :param query_restriction: Default is query all.
        :param related_record_id: This is the record ID to check against. Not used when restriction is 'query all'.
        :param related_record_type: Specifies the data type name of relatedRecordId.
        """
        self.related_record_id = related_record_id
        self.related_record_type = related_record_type
        self.query_restriction = query_restriction

    def to_json(self) -> Dict[str, Any]:
        ret = {'queryRestriction': self.query_restriction.name}
        if self.related_record_id is not None:
            ret['relatedRecordId'] = self.related_record_id
        if self.related_record_type is not None:
            ret['relatedRecordType'] = self.related_record_type
        return ret

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> RelatedRecordCriteria:
        query_restriction = QueryRestriction[json_dct.get('queryRestriction')]
        related_record_id = None
        if 'relatedRecordId' in json_dct:
            related_record_id = int(json_dct.get('relatedRecordId'))
        related_record_type = None
        if 'relatedRecordType' in json_dct:
            related_record_type = json_dct.get('relatedRecordType')
        return RelatedRecordCriteria(query_restriction,
                                     related_record_id=related_record_id, related_record_type=related_record_type)


class ExplicitJoinDefinition:
    """
    A custom join defined for an advanced search.

    data_type_name: The name of the (UNRELATED) data type to be joined to the other data types referenced
    in the advanced search. The report term included in this object much define how this type will be joined with
    the other types in the search.

    report_term: The terms that will be used to join the provided data type name to the advanced search
    that it is set on. These terms cannot reference data type names that have not been added to the advanced search
    yet.
    """
    data_type_name: str
    report_term: FieldCompareReportTerm

    def __init__(self, data_type_name: str, report_term: FieldCompareReportTerm):
        """
        A custom join defined for an advanced search.
        :param data_type_name: The name of the (UNRELATED) data type to be joined to the other data types referenced
        in the advanced search. The report term included in this object much define how this type will be joined with
        the other types in the search.
        :param report_term: The terms that will be used to join the provided data type name to the advanced search
        that it is set on. These terms cannot reference data type names that have not been added to the advanced search
        yet.
        """
        self.data_type_name = data_type_name
        self.report_term = report_term

    def to_json(self) -> Dict[str, Any]:
        return {
            'dataTypeName': self.data_type_name,
            'reportTermPojo': self.report_term.to_json()
        }

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, ExplicitJoinDefinition):
            return False
        return self.data_type_name == other.data_type_name

    def __hash__(self):
        return hash(self.data_type_name)

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> ExplicitJoinDefinition:
        data_type_name: str = json_dct.get('dataTypeName')
        # noinspection PyTypeChecker
        report_term: FieldCompareReportTerm = AbstractReportTerm.from_json(json_dct.get('reportTermPojo'))
        return ExplicitJoinDefinition(data_type_name, report_term)

#FR-52729 Super class to AbstractPageCriteria
class CustomReportCriteria(AbstractPageCriteria):
    """
    Specifies the custom report criteria object to tell the server what to query.
    """
    column_list: List[ReportColumn]
    root_term: AbstractReportTerm
    related_record_criteria: RelatedRecordCriteria
    case_sensitive: bool
    page_number: int
    root_data_type: Optional[str]
    owner_restriction_set: Optional[List[str]]
    join_list: Optional[List[ExplicitJoinDefinition]]

    def __init__(self, column_list: List[ReportColumn], root_term: AbstractReportTerm = None,
                 related_record_criteria: RelatedRecordCriteria = RelatedRecordCriteria(QueryRestriction.QUERY_ALL),
                 root_data_type: Optional[str] = None, case_sensitive: bool = False, page_size: int = 0,
                 page_number: int = -1, owner_restriction_set: List[str] = None,
                 join_list: Optional[List[ExplicitJoinDefinition]] = None, **kwargs):
        """
        Specifies the custom report criteria object to tell the server what to query.
        :param column_list: The list of columns in the output of this report.
        :param root_term: Conditions that needs to be satisfied for a row to show up in a report.
        :param related_record_criteria: Specifies further restriction that all results must be related to this record.
        :param root_data_type: Only required when the path is ambiguous. Specifies the highest ancestor data type name.
        :param case_sensitive: When searching texts, should the search be case sensitive?
        :param page_size: The page size of the custom report.
        :param page_number: The page number of the current report.
        :param owner_restriction_set: Specifies to only return records if record is owned by this set of usernames.
        Applicable to role-based applications only.
        """
        super().__init__(page_size)
        self.column_list = column_list
        self.root_term = root_term
        self.related_record_criteria = related_record_criteria
        self.root_data_type = root_data_type
        self.case_sensitive = case_sensitive
        self.page_size = page_size
        self.page_number = page_number
        self.owner_restriction_set = owner_restriction_set
        self.join_list = join_list
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_json(self) -> Dict[str, Any]:
        ret = {
            'columnList': [x.to_pojo() for x in self.column_list],
            'relatedRecordCriteria': self.related_record_criteria.to_json(),
            'caseSensitive': self.case_sensitive,
            'pageSize': self.page_size,
            'pageNumber': self.page_number
        }
        if self.root_term is not None:
            ret['rootTerm'] = self.root_term.to_json()
        if self.root_data_type is not None:
            ret['rootDataType'] = self.root_data_type
        if self.owner_restriction_set is not None:
            ret['ownerRestrictionSet'] = self.owner_restriction_set
        if self.join_list is not None:
            ret['joinList'] = [x.to_json() for x in self.join_list]
        return ret

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> CustomReportCriteria:
        column_list = [ReportColumn.from_json(dct) for dct in json_dct.get('columnList')]
        root_term: AbstractReportTerm | None = None
        if json_dct.get('rootTerm') is not None:
            root_term = AbstractReportTerm.from_json(json_dct.get('rootTerm'))
        related_record_criteria = RelatedRecordCriteria(QueryRestriction.QUERY_ALL)
        if json_dct.get('relatedRecordCriteria') is not None:
            related_record_criteria = RelatedRecordCriteria.from_json(json_dct.get('relatedRecordCriteria'))
        case_sensitive = bool(json_dct.get('caseSensitive'))
        page_size = int(json_dct.get('pageSize'))
        page_number = int(json_dct.get('pageNumber'))
        root_data_type = None
        if json_dct.get('rootDataType') is not None:
            root_data_type = json_dct.get('rootDataType')
        owner_restriction_set = None
        if json_dct.get('ownerRestrictionSet') is not None:
            owner_restriction_set = json_dct.get('ownerRestrictionSet')
        join_list: Optional[List[ExplicitJoinDefinition]] = None
        if json_dct.get('joinList') is not None:
            join_list = [ExplicitJoinDefinition.from_json(x) for x in json_dct.get('joinList')]
        return CustomReportCriteria(column_list, root_term, related_record_criteria=related_record_criteria,
                                    root_data_type=root_data_type, case_sensitive=case_sensitive,
                                    page_size=page_size, page_number=page_number,
                                    owner_restriction_set=owner_restriction_set, join_list=join_list)

# FR-52729 Added class
class CustomReport(CustomReportCriteria):
    """
    Holds a custom report run result.
    """
    has_next_page: bool
    result_table: list[list[Any]]

    def __init__(self, has_next_page: bool, result_table: list[list[Any]],
                 criteria: CustomReportCriteria):
        """
        Holds a custom report run result.
        :param has_next_page: Does the next page have any records?
        :param result_table: The data in the report. The first dimension is row, each row represent a record.
        For each row, the column is in order of the column list defined in this report.
        """
        super().__init__(**criteria.__dict__)
        self.has_next_page = has_next_page
        self.result_table = result_table

    def to_json(self) -> Dict[str, Any]:
        ret = super().to_json()
        ret['hasNextPage'] = self.has_next_page
        ret['resultTable'] = self.result_table
        return ret

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> CustomReport:
        criteria = CustomReportCriteria.from_json(json_dct)
        has_next_page: bool = json_dct.get('hasNextPage')
        result_table: list[list[Any]] = json_dct.get('resultTable')
        return CustomReport(has_next_page, result_table, criteria)

    def get_data_frame(self) -> pd.DataFrame:
        """
        Obtain the result data as a pandas package DataFrame object.
        """
        columns = [str(x) for x in self.column_list]
        return pd.DataFrame(self.result_table, columns=columns)

    def __str__(self):
        return str(self.get_data_frame())
