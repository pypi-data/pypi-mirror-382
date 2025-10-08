from abc import abstractmethod, ABC
from enum import Enum
from typing import Dict, Any, List, Optional, TypeVar, Generic, Iterable

import sapiopylib.utils.string as ssutil
from sapiopylib.rest.pojo.Sort import SortDirection, SortDirectionParser


class FieldType(Enum):
    """
    All possible data field types in a data field of any data type.
    """
    BOOLEAN = 0, "True / False", True
    DOUBLE = 1, "Decimal", True,
    ENUM = 2, "Old-Style Pick List", True,
    LONG = 3, "Long Integer", True
    INTEGER = 4, "Integer", True,
    SHORT = 5, "Small Integer", True
    STRING = 6, "Text"
    DATE = 7, "Date", True
    ACTION = 9, "Action Button", False, True, False, False
    SELECTION = 10, "Selection List"
    PARENTLINK = 11, "Linked Record", False, False, True, False
    IDENTIFIER = 12, "Identifier", False, False, True, False
    PICKLIST = 13, "Pick List"
    LINK = 14, "Link"
    MULTIPARENTLINK = 15, "Multi-Parent Link", False, False, False, False
    CHILDLINK = 16, "Linked Child;", True, False, True, False
    AUTO_ACCESSION = 17, "Auto-Accession"
    DATE_RANGE = 18, "Date Range", True, True, True, True, True
    SIDE_LINK = 19, "Side Link", True, True, True, True, False
    ACTION_STRING = 20, "Action Text", False, True, True, True, False

    index: int
    display_name: str
    is_numeric_base_type: bool
    is_user_creatable: bool
    is_in_record_table: bool
    is_audit_logged: bool
    is_multi_column: bool

    def __init__(self, index: int, display_name: str, is_numeric_base_type: bool = False,
                 is_user_creatable: bool = True, is_in_record_table: bool = True, is_audit_logged: bool = True,
                 is_multi_column: bool = False):
        self.index = index
        self.display_name = display_name
        self.is_numeric_base_type = is_numeric_base_type
        self.is_user_creatable = is_user_creatable
        self.is_in_record_table = is_in_record_table
        self.is_audit_logged = is_audit_logged
        self.is_multi_column = is_multi_column

    def __str__(self):
        return self.display_name


class AbstractVeloxFieldDefinition(ABC):
    """
    A data field definition of a Sapio data type field.
    """
    _data_type_name: str
    data_field_type: FieldType
    _data_field_name: str
    description: Optional[str] = None
    display_name: str
    required: bool = False
    editable: bool = False
    visible: bool = True
    identifier: bool = False
    identifier_order: Optional[int] = None
    sort_direction: Optional[SortDirection] = None
    sort_order: Optional[int] = None
    tag: Optional[str] = None
    key_field: bool = False
    key_field_order: Optional[int] = None
    system_field: bool = False
    audit_logged: bool = True
    default_table_column_width: Optional[int] = None

    @property
    def default_value(self) -> Any:
        """
        Get the default value of the current field type.
        Note: this can be not applicable to certain types. In which case None will be returned.
        """
        if hasattr(self, '_default_value'):
            return self._default_value
        return None

    @default_value.setter
    def default_value(self, value: Any):
        setattr(self, '_default_value', value)

    @property
    def data_type_name(self) -> str:
        """
        Get the data type name of the current field.
        This is the same as get_data_type_name()
        """
        return self._data_type_name

    @property
    def data_field_name(self) -> str:
        """
        Get the data field name of the current field.
        This is the same as get_data_field_name()
        """
        return self._data_field_name

    def get_data_type_name(self):
        return self._data_type_name

    def get_data_field_name(self):
        return self._data_field_name

    @abstractmethod
    def get_json_type_id(self) -> str:
        """
        Return the Java class name discriminator from jackson's JsonTypeInfo.Id.NAME default attribute.
        This is required for server to distinguish among sub-classes.
        """
        pass

    def __eq__(self, other):
        if not isinstance(other, AbstractVeloxFieldDefinition):
            return False
        other_pojo: AbstractVeloxFieldDefinition = other
        if self.data_field_type != other_pojo.data_field_type:
            return False
        return self._data_type_name == other._data_type_name and self._data_field_name == other._data_field_name

    def __hash__(self):
        return hash((self.data_field_type.name, self._data_type_name, self._data_field_name))

    def __init__(self, data_type_name: str, data_field_type: FieldType, data_field_name: str,
                 display_name: str, **kwargs):
        """
        This should never be used directly outside the library as it is an abstract type.
        Defines common data field definition attributes across all field definition types.
        :param data_type_name: The data type name of the field.
        :param data_field_type: The field type to provide jackson hints at server side during deserialization.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param description: The description of the field.
        :param required: Does the field require non-blank value?
        :param editable: Is the field editable by user in GUI?
        :param visible: Is the field visible to user?
        :param identifier: Is the field an identifier of the record (i.e. show in data record name)
        :param identifier_order: The order of this field among all ID fields
        :param sort_direction: If records should be pre-sorted, the direction of the sorting.
        :param sort_order: The sorting priority among all sorting fields.
        :param tag: The tag can be used to programmatically identify a field's function.
        :param key_field: Is the field a key field (show in minimized views)
        :param key_field_order: The order of this field among all key fields.
        :param system_field: Is this field a system field. Note: API will disregard this input.
        :param audit_logged: Are changes to this field audit logged?
        :param default_table_column_width: The custom column width of the field in UI table grids.
        Note: does not affect python display. Only in Sapio.
        """
        description: Optional[str] = kwargs.get('description')
        if description is None:
            kwargs['description'] = ""
        tag: Optional[str] = kwargs.get('tag')
        if tag is None:
            kwargs['tag'] = ""
        sort_direction: Optional[SortDirection] = kwargs.get('sort_direction')
        if sort_direction is None:
            kwargs['sort_direction'] = None

        self._data_type_name = data_type_name
        self.data_field_type = data_field_type
        self._data_field_name = data_field_name
        self.display_name = display_name
        self.__dict__.update(kwargs)

    def __str__(self):
        return self._data_field_name

    def to_json(self) -> Dict[str, Any]:
        sort_direction: Optional[str]
        if self.sort_direction is not None:
            sort_direction = self.sort_direction.field_def_enum_name
        else:
            sort_direction = SortDirection.NONE.field_def_enum_name
        return {
            '@type': self.get_json_type_id(),
            'dataTypeName': self._data_type_name,
            'dataFieldType': self.data_field_type.name,
            'dataFieldName': self._data_field_name,
            'displayName': self.display_name,
            'description': self.description,
            'required': self.required,
            'editable': self.editable,
            'visible': self.visible,
            'identifier': self.identifier,
            'identifierOrder': self.identifier_order,
            'sortDirection': sort_direction,
            'sortOrder': self.sort_order,
            'tag': self.tag,
            'keyField': self.key_field,
            'keyFieldOrder': self.key_field_order,
            'systemField': self.system_field,
            'auditLogged': self.audit_logged,
            'defaultTableColumnWidth': self.default_table_column_width
        }


BlockerFieldType = TypeVar("BlockerFieldType")


class VeloxBlockerFieldDefinition(AbstractVeloxFieldDefinition, ABC, Generic[BlockerFieldType]):
    """
    Field definitions that are able to have field dependencies.
    """
    hide_disabled_fields: bool
    """If True, disabled dependent fields will be hidden in form layouts. If False, the field will be made uneditable
    but still visible. Table layouts only support the uneditable behavior."""
    # This is flipped from how the server stores field dependencies, since JSON dictionary keys must be strings.
    # Python also doesn't like sets in JSON, so we use a list internally instead.
    _dependent_fields_map: dict[str, list[BlockerFieldType]]
    """A map of field name to the field value that causes that dependent field to become disabled."""

    def __init__(self, data_type_name: str, data_field_type: FieldType, data_field_name: str, display_name: str, **kwargs):
        super().__init__(data_type_name, data_field_type, data_field_name, display_name, **kwargs)
        self.hide_disabled_fields = False
        self._dependent_fields_map = {}

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = super().to_json()
        ret['hideDisabledFields'] = self.hide_disabled_fields
        ret['dependentFieldMap'] = self._dependent_fields_map
        return ret

    def add_dependent_field(self, key: BlockerFieldType, dependent_field: str) -> None:
        """
        Add a dependent field to the field definition.

        :param key: The field value that will cause the dependent field to be disabled.
        :param dependent_field: The field name that will be disabled when the key is set.
        """
        field_dependencies = self._dependent_fields_map.setdefault(dependent_field, [])
        if key not in field_dependencies:
            field_dependencies.append(key)

    def add_dependent_field_list(self, key: BlockerFieldType, dependent_fields: Iterable[str]) -> None:
        """
        Add a list of dependent fields to the field definition.

        :param key: The field value that will cause the dependent fields to be disabled.
        :param dependent_fields: The list of field names that will be disabled when the key is set.
        """
        for dependent_field in dependent_fields:
            self.add_dependent_field(key, dependent_field)

    def get_dependent_field_map(self) -> dict[BlockerFieldType, set[str]]:
        """
        Get the map of dependent fields for this field definition.

        :return: The map of field values to the set of field names that will be disabled when the field value is set.
        """
        ret_val: dict[BlockerFieldType, set[str]] = {}
        for key, values in self._dependent_fields_map.items():
            for value in values:
                ret_val.setdefault(key, set()).add(value)
        return ret_val

    def set_dependent_field_map(self, dependencies: dict[BlockerFieldType, set[str]] | None = None) -> None:
        """
        Set the map of dependent fields for this field definition.

        :param dependencies: The map of field values to the set of field names that will be disabled when the field
            value is set. If None, the existing dependencies will be cleared.
        """
        self._dependent_fields_map = {}
        if not dependencies:
            return
        for key, values in dependencies.items():
            self.add_dependent_field_list(key, values)



class VeloxAccessionFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition representing a field on the data type that will be automatically accessioned when
    new records of this type are created.  Fields of this type cannot be modified through the API.
    """
    unique_value: bool
    sequence_key: str
    prefix: str
    suffix: str
    number_of_digits: int
    starting_value: int
    link_out: bool | None
    link_out_url: str | None

    def get_json_type_id(self):
        return 'VeloxAccessionFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 sequence_key: str, prefix: str | None = None, suffix: str | None = None,
                 number_of_digits: int = 6, unique_value: bool = False, starting_value: int | None = None,
                 link_out: bool | None = False, link_out_url: str | None = None,
                 **kwargs):
        """
        Create a new auto-accession field definition.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param sequence_key: The key that will be used to track the accession value for this field.
        This could map to a sequence that already exists in the accession manager, or it could be a new key.
        :param prefix: The prefix that will be added before the accessioned numeric value.
        :param suffix: The suffix that will be added to the end of the accessioned numeric value.
        :param number_of_digits: The minimum number of digits to include in the accessioned value.
        :param unique_value: Whether this field must be unique in the system. (Error if it is not, when set to True.)
        :param kwargs:
        """
        super().__init__(data_type_name, FieldType.AUTO_ACCESSION, data_field_name, display_name, **kwargs)
        self.sequence_key = sequence_key
        if prefix is None:
            prefix = ""
        self.prefix = prefix
        if suffix is None:
            suffix = ""
        if starting_value is None:
            starting_value = 1
        self.suffix = suffix
        self.number_of_digits = number_of_digits
        self.unique_value = unique_value
        self.starting_value = starting_value
        self.link_out = link_out
        self.link_out_url = link_out_url

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['uniqueValue'] = self.unique_value
        ret['sequenceKey'] = self.sequence_key
        ret['prefix'] = self.prefix
        ret['suffix'] = self.suffix
        ret['numberOfDigits'] = self.number_of_digits
        ret['startingValue'] = self.starting_value
        ret['linkOut'] = self.link_out
        ret['linkOutUrl'] = self.link_out_url
        return ret


class VeloxActionFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition representing a button that can be displayed in a form layout.
    No backing field data.
    """

    def __init__(self, data_type_name: str, data_field_name: str,
                 display_name: str, **kwargs):
        super().__init__(data_type_name, FieldType.ACTION, data_field_name, display_name, **kwargs)

    def get_json_type_id(self):
        return 'VeloxActionFieldDefinitionPojo'


class VeloxBooleanFieldDefinition(VeloxBlockerFieldDefinition[bool]):
    """
    Field definition representing a field containing a boolean value.
    """
    _default_value: Optional[bool]
    process_todo_item: bool

    def get_json_type_id(self) -> str:
        return 'VeloxBooleanFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 default_value: Optional[bool] = None, is_process_todo_item: bool = False,
                 **kwargs):
        """
        Create a new boolean field.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param default_value: The default value that will be set in this field when a new record is created.
        :param is_process_todo_item: Whether this is a 'to do' field that backs a Process View Component.
        """
        super().__init__(data_type_name, FieldType.BOOLEAN, data_field_name, display_name, **kwargs)
        self._default_value = default_value
        self.process_todo_item = is_process_todo_item

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['defaultValue'] = self._default_value
        ret['processTodoItem'] = self.process_todo_item
        return ret


class VeloxChildLinkFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition representing a link to a child type.
    """

    def get_json_type_id(self) -> str:
        return 'VeloxChildLinkFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str,
                 display_name: str, **kwargs):
        super().__init__(data_type_name, FieldType.CHILDLINK, data_field_name, display_name, **kwargs)


# noinspection PyAbstractClass
class AbstractDateFieldDefinition(AbstractVeloxFieldDefinition):
    date_time_format: str

    def __init__(self, data_type_name: str, field_type: FieldType, data_field_name: str, display_name: str,
                 date_time_format: str = 'MMM dd, yyyy',
                 **kwargs):
        super().__init__(data_type_name, field_type, data_field_name, display_name, **kwargs)
        self.date_time_format = date_time_format

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['dateTimeFormat'] = self.date_time_format
        return ret


class VeloxDateFieldDefinition(AbstractDateFieldDefinition):
    """
    Field definition representing a field that can contain a date value.
    """
    _default_value: str
    static_date: bool

    def get_json_type_id(self) -> str:
        return 'VeloxDateFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 date_time_format: str = 'MMM dd, yyyy',
                 default_value: Optional[str] = None, static_date: bool = False,
                 **kwargs):
        """
        Create a new date field definition.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param default_value: The default value of this field.
        :param static_date: Whether the date is static date. (Whether client will always use UTC timezone)
        """
        super().__init__(data_type_name, FieldType.DATE, data_field_name, display_name, **kwargs)
        self.date_time_format = date_time_format
        self._default_value = default_value
        self.static_date = static_date

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['defaultValue'] = self._default_value
        ret['staticDate'] = self.static_date
        return ret


class VeloxDateRangeFieldDefinition(AbstractDateFieldDefinition):
    """
    Field definition representing a field that can contain a date range value.
    """
    _default_value: str
    static_date: bool

    def get_json_type_id(self) -> str:
        return 'VeloxDateRangeFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 date_time_format: str = 'MMM dd, yyyy', static_date: bool = False,
                 default_value: Optional[str] = None,
                 **kwargs):
        """
        Create a new date range field definition.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param default_value: The default value of this field.
        """
        super().__init__(data_type_name, FieldType.DATE_RANGE, data_field_name, display_name, **kwargs)
        self._default_value = default_value
        self.date_time_format = date_time_format
        self.static_date = static_date

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['defaultValue'] = self._default_value
        ret['static'] = self.static_date
        return ret


class SapioDoubleFormat(Enum):
    CURRENCY = 0
    PERCENTAGE = 1


class VeloxDoubleFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition representing a field that can contain a double value.
    """
    min_value: float
    max_value: float
    _default_value: Optional[float]
    precision: int
    double_format: Optional[SapioDoubleFormat]

    def get_json_type_id(self) -> str:
        return 'VeloxDoubleFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 min_value: float = -10000000, max_value: float = 100000000,
                 default_value: Optional[float] = None, precision: int = 1,
                 double_format: Optional[SapioDoubleFormat] = None,
                 **kwargs):
        """
        Create a new double field definition.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param default_value: The default value of this field.
        :param min_value: The minimum allowed value in this field, if not blank.
        :param max_value: The maximum allowed value in this field, if not blank.
        :param precision: The precision to be displayed. Does not change storage precision.
        :param double_format: Special Sapio formatting decorations for this field.
        """
        super().__init__(data_type_name, FieldType.DOUBLE, data_field_name, display_name, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self._default_value = default_value
        self.precision = precision
        self.double_format = double_format

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['minValue'] = self.min_value
        ret['maxValue'] = self.max_value
        ret['defaultValue'] = self._default_value
        ret['precision'] = self.precision
        if self.double_format is not None:
            ret['doubleFormat'] = self.double_format.name
        return ret


class VeloxEnumFieldDefinition(VeloxBlockerFieldDefinition[int]):
    """
    Field definition representing a field that is backed by enum values.  This field definition defines
    a list of possible values that can be set on the field.  The values returned for fields of this type
    will be short values that index into the array of values set on the field definition.
    """
    _default_value: Optional[int]
    values: Optional[List[str]]

    def get_json_type_id(self) -> str:
        return 'VeloxEnumFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 default_value: Optional[int], values: Optional[List[str]] = None,
                 **kwargs):
        """
        Create a enum field definition.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param default_value: The default value of this field.
        :param values: the in order value list to translate a index number to a display text.
        """
        super().__init__(data_type_name, FieldType.ENUM, data_field_name, display_name, **kwargs)
        self._default_value = default_value
        self.values = values

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['defaultValue'] = self._default_value
        ret['values'] = self.values
        return ret


class VeloxIdentifierFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition that defines an identifier of this data type.  This field is created by the server
    and cannot be modified through the API.

    The value of this field will be composed of values from fields that are marked with the identifier boolean field.
    The field value is not guaranteed to be unique.
    """

    def get_json_type_id(self) -> str:
        return 'VeloxIdentifierFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 **kwargs):
        """
        Internal usage only!
        """
        super().__init__(data_type_name, FieldType.IDENTIFIER, data_field_name, display_name, **kwargs)


# noinspection PyAbstractClass
class AbstractIntegerFieldFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Python specific class to shortcut writing redundant integer field classes.
    """
    min_value: int
    max_value: int
    _default_value: Optional[int]
    unique_value: bool

    def __init__(self, data_type_name: str, data_field_type: FieldType, data_field_name: str, display_name: str,
                 min_value: int, max_value: int, default_value: Optional[int] = None,
                 unique_value: bool = False, **kwargs):
        """
        Create a new integer field definition.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param default_value: The default value of this field.
        :param min_value: The minimum allowed value in this field, if not blank.
        :param max_value: The maximum allowed value in this field, if not blank.
        """
        super().__init__(data_type_name, data_field_type, data_field_name, display_name, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self._default_value = default_value
        self.unique_value = unique_value

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['minValue'] = self.min_value
        ret['maxValue'] = self.max_value
        ret['defaultValue'] = self._default_value
        ret['uniqueValue'] = self.unique_value
        return ret


class VeloxIntegerFieldDefinition(AbstractIntegerFieldFieldDefinition):
    """
    Field definition representing a column that holds an integer value.
    """

    def get_json_type_id(self) -> str:
        return 'VeloxIntegerFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 min_value: int = -10000, max_value: int = 10000, default_value: Optional[int] = None,
                 unique_value: bool = False, **kwargs):
        super().__init__(data_type_name, FieldType.INTEGER, data_field_name, display_name,
                         min_value, max_value, default_value, unique_value, **kwargs)


class VeloxLongFieldDefinition(AbstractIntegerFieldFieldDefinition):
    """
    Field definition representing a column that holds an long value.
    """

    def get_json_type_id(self) -> str:
        return 'VeloxLongFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 min_value: int = -10000000, max_value: int = 10000000, default_value: Optional[int] = None,
                 unique_value: bool = False, **kwargs):
        """
        Create a new long field definition.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param default_value: The default value of this field.
        :param min_value: The minimum allowed value in this field, if not blank.
        :param max_value: The maximum allowed value in this field, if not blank.
        """
        super().__init__(data_type_name, FieldType.LONG, data_field_name, display_name,
                         min_value, max_value, default_value, unique_value, **kwargs)


class VeloxMultiParentFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition representing a link to multiple parents of a given type.
    These fields are automatically created by the server for relations where the child type can be under multiple
    records of the parent type.
    User should not create new multi parent fields directly.
    """

    def get_json_type_id(self) -> str:
        return 'VeloxMultiParentFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 **kwargs):
        """
        Internal usage only!
        """
        super().__init__(data_type_name, FieldType.MULTIPARENTLINK, data_field_name, display_name, **kwargs)


class VeloxParentFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition representing a link to a single parent of a given type.  These fields are automatically
    related by the server for relations where the child type cannot be under many records of the given parent type.
    These fields cannot be added or set manually through the API.
    """

    def get_json_type_id(self) -> str:
        return 'VeloxParentLinkFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 **kwargs):
        """
        Internal usage only!
        """
        super().__init__(data_type_name, FieldType.PARENTLINK, data_field_name, display_name, **kwargs)


class VeloxPickListFieldDefinition(VeloxBlockerFieldDefinition[str]):
    """
    Field definition representing a field that can be backed by a configurable list that is defined in the system.
    Fields of this type do not support having multiple values from the list set at the same time.
    """
    _default_value: str
    pick_list_name: str
    direct_edit: bool

    def get_json_type_id(self) -> str:
        return 'VeloxPickListFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 pick_list_name: str, default_value: Optional[str] = None, direct_edit: bool = False,
                 **kwargs):
        super().__init__(data_type_name, FieldType.PICKLIST, data_field_name, display_name, **kwargs)
        self._default_value = default_value
        self.pick_list_name = pick_list_name
        self.direct_edit = direct_edit

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['defaultValue'] = self._default_value
        ret['pickListName'] = self.pick_list_name
        ret['directEdit'] = self.direct_edit
        return ret


class ListMode(Enum):
    """
    Possible list modes for selection lists.
    """
    LIST = "[List]"
    REPORT = "[Report]"
    PLUGIN = "[Plugin]"
    USER = "[Users]"
    NON_API_USER = "[Users]" + "[NonApi]"
    USER_GROUP = "[UserGroups]"

    list_mode_name: str

    def __init__(self, list_mode_name: str):
        self.list_mode_name = list_mode_name


class VeloxSelectionFieldDefinition(VeloxBlockerFieldDefinition[str]):
    _default_value: str
    list_mode: ListMode
    unique_value: bool
    multi_select: bool
    pick_list_name: str
    custom_report_name: str
    plugin_name: str
    direct_edit: bool
    static_list_values: list[str] | None

    def get_json_type_id(self) -> str:
        return 'VeloxSelectionFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 list_mode: ListMode, unique_value: bool = False, multi_select: bool = False,
                 default_value: Optional[str] = None, pick_list_name: Optional[str] = None,
                 custom_report_name: Optional[str] = None, plugin_name: Optional[str] = None,
                 direct_edit: bool = False, static_list_values: list[str] = None,
                 **kwargs):
        super().__init__(data_type_name, FieldType.SELECTION, data_field_name, display_name, **kwargs)
        self.list_mode = list_mode
        self.unique_value = unique_value
        self.multi_select = multi_select
        self._default_value = default_value
        if list_mode == ListMode.LIST and pick_list_name is None:
            raise ValueError('When selection list mode is LIST, the pick list name must be non-blank.')
        self.pick_list_name = pick_list_name
        if list_mode == ListMode.REPORT and custom_report_name is None:
            raise ValueError('When selection list mode is REPORT, the report name must be non-blank.')
        self.custom_report_name = custom_report_name
        self.plugin_name = plugin_name
        self.direct_edit = direct_edit
        self.static_list_values = static_list_values

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        list_mode_str: Optional[str] = None
        if self.list_mode is not None:
            list_mode_str = self.list_mode.list_mode_name
            if self.list_mode == ListMode.LIST:
                list_mode_str += self.pick_list_name
            elif self.list_mode == ListMode.PLUGIN:
                if self.plugin_name:
                    list_mode_str += self.plugin_name
            elif self.list_mode == ListMode.REPORT:
                list_mode_str += self.custom_report_name
        ret['listMode'] = list_mode_str
        ret['defaultValue'] = self._default_value
        ret['uniqueValue'] = self.unique_value
        ret['multiSelect'] = self.multi_select
        ret['directEdit'] = self.direct_edit
        ret['staticListValues'] = self.static_list_values
        return ret


class VeloxShortFieldDefinition(AbstractIntegerFieldFieldDefinition):
    """
    Field definition representing a field that can store a short integer value.
    """

    def get_json_type_id(self) -> str:
        return 'VeloxShortFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 min_value: int = -100, max_value: int = 100, default_value: Optional[int] = None,
                 unique_value: bool = False, **kwargs):
        """
        Create a new short field definition.
        :param data_type_name: The data type name of the field.
        :param data_field_name: The field name of the field.
        :param display_name The field name to be displayed to user in Sapio.
        :param default_value: The default value of this field.
        :param min_value: The minimum allowed value in this field, if not blank.
        :param max_value: The maximum allowed value in this field, if not blank.
        """
        super().__init__(data_type_name, FieldType.SHORT, data_field_name, display_name,
                         min_value, max_value, default_value, unique_value, **kwargs)


class SapioStringFormat(Enum):
    PHONE = 0
    EMAIL = 1


class FieldValidator:
    """
    POJO used to specify custom field validation logic for a given String field.

    validation_regex: The regex to check for this field
    error_message: The error message to display if validation has failed.
    """
    validation_regex: str
    error_message: str

    def __init__(self, validation_regex: str, error_message: str):
        """
        POJO used to specify custom field validation logic for a given String field.
        :param validation_regex: The regex to check for this field
        :param error_message: The error message to display if validation has failed.
        """
        self.validation_regex = validation_regex
        self.error_message = error_message

    def to_json(self) -> Dict[str, Any]:
        return {
            "validationRegex": self.validation_regex,
            "errorMessage": self.error_message
        }


class VeloxStringFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition representing a field that can store a string value.
    """
    _default_value: Optional[str]
    max_length: int
    unique_value: bool
    html_editor: bool
    string_format: SapioStringFormat
    num_lines: int
    auto_size: bool
    link_out: Optional[bool]
    link_out_url: Optional[str]
    field_validator: Optional[FieldValidator]

    def get_json_type_id(self) -> str:
        return 'VeloxStringFieldDefinitionPojo'

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 default_value: Optional[str] = None, max_length: int = 100,
                 unique_value: bool = False, html_editor: bool = False,
                 string_format: Optional[SapioStringFormat] = None,
                 num_lines: int = 1, auto_size: bool = False,
                 link_out: Optional[bool] = False, link_out_url: Optional[str] = None,
                 field_validator: Optional[FieldValidator] = None,
                 **kwargs):
        """
        Field definition representing a field that can store a string value.
        :param data_type_name: Data type name of this field.

        :param data_field_name: Data field name of this field.

        :param display_name: Display name of this field.

        :param default_value: The default value that will be set in this field when a new record is created.

        :param max_length: The maximum number of characters that can be stored in this field.

        :param unique_value: Whether this field must be unique in the system.

        :param html_editor: Whether this field will be able to render html markup.

        :param string_format: The formatting to be used when displaying this field.

        :param num_lines: Number of lines of this string field. Default is 1. Must not be None.

        :param auto_size: Whether the string field shall be auto-sized based off of its content length.
        Overrides number of lines
        :param link_out: Whether this field is a link-out field.

        :param link_out_url: The link-out URL macro that uses this field's field value if link out property
        is set to true. The format of this field should have value like this
        DISPLAY_TEXT\thttp://sapiosciences.com/[[LINK_OUT]]
        The text shown to user will be "DISPLAY_TEXT". And when user clicks on link, it will navigate to
        http://sapiosciences.com/[[LINK_OUT]] where [[LINK_OUT]] is replaced with value of the string field at the time.

        :param field_validator: When set, user input will be validated against a regular expression.
        Failing to validate will cause the UI not accept user input and provide the user a custom error message
        set in the same object.

        :param kwargs: Additional arguments to abstract field definition.
        """
        super().__init__(data_type_name, FieldType.STRING, data_field_name, display_name, **kwargs)
        self._default_value = default_value
        self.max_length = max_length
        self.unique_value = unique_value
        self.html_editor = html_editor
        self.string_format = string_format
        self.num_lines = num_lines
        self.auto_size = auto_size
        self.link_out = link_out
        self.link_out_url = link_out_url
        self.field_validator = field_validator

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['defaultValue'] = self._default_value
        ret['maxLength'] = self.max_length
        ret['uniqueValue'] = self.unique_value
        ret['htmlEditor'] = self.html_editor
        if self.string_format is not None:
            ret['stringFormat'] = self.string_format.name
        ret['numLines'] = self.num_lines
        ret['autoSize'] = self.auto_size
        ret['linkOut'] = self.link_out
        ret['linkOutUrl'] = self.link_out_url
        if self.field_validator is not None:
            ret['fieldValidator'] = self.field_validator.to_json()
        return ret


class VeloxSideLinkFieldDefinition(AbstractVeloxFieldDefinition):
    """
    This field definition represents a link to another record in the system.
    """

    linked_data_type_name: Optional[str]
    _default_value: Optional[int]

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 default_value: Optional[int] = None, linked_data_type_name: Optional[str] = None, **kwargs):
        super().__init__(data_type_name, FieldType.SIDE_LINK, data_field_name, display_name, **kwargs)
        self._default_value = default_value
        self.linked_data_type_name = linked_data_type_name

    def get_json_type_id(self) -> str:
        return "VeloxSideLinkFieldDefinitionPojo"

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['defaultValue'] = self._default_value
        ret['linkedDataTypeName'] = self.linked_data_type_name
        return ret


class VeloxActionStringFieldDefinition(AbstractVeloxFieldDefinition):
    """
    Field definition representing a field that can store a string field as regular text field,
    and also is associated with a button backed by a custom plugin (in Java deployed as server-side plugin).
    """

    _default_value: Optional[str]
    max_length: int
    unique_value: bool
    field_validator: Optional[FieldValidator]
    icon_name: Optional[str]
    action_plugin_path: Optional[str]
    direct_edit: bool

    def __init__(self, data_type_name: str, data_field_name: str, display_name: str,
                 default_value: Optional[str] = None, max_length: int = 100,
                 unique_value: bool = False, field_validator: Optional[FieldValidator] = None,
                 icon_name: Optional[str] = None, action_plugin_path: Optional[str] = None,
                 direct_edit: bool = False, **kwargs):
        super().__init__(data_type_name, FieldType.ACTION_STRING, data_field_name, display_name, **kwargs)
        self._default_value = default_value
        self.max_length = max_length
        self.unique_value = unique_value
        self.field_validator = field_validator
        self.icon_name = icon_name
        self.action_plugin_path = action_plugin_path
        self.direct_edit = direct_edit

    def get_json_type_id(self) -> str:
        return "VeloxActionStringFieldDefinitionPojo"

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_json()
        ret['defaultValue'] = self._default_value
        ret['maxLength'] = self.max_length
        ret['uniqueValue'] = self.unique_value
        if self.field_validator is not None:
            ret['fieldValidator'] = self.field_validator.to_json()
        ret['iconName'] = self.icon_name
        ret['actionPluginPath'] = self.action_plugin_path
        ret['directEdit'] = self.direct_edit
        return ret


class FieldDefinitionParser:
    @staticmethod
    def to_field_definition(json_dct: Dict[str, Any]) -> AbstractVeloxFieldDefinition:
        """
        Calls parser method to obtain the correct type of field definition class and fill the data fields in object.
        :param json_dct: The JSON dictionary directly contain a field's data.
        :return: A field definition object.
        """
        return _parse_abstract_field_def(json_dct)


class _FieldDefBaseParserParams:
    data_type_name: str
    data_field_name: str
    display_name: str
    data_field_type: FieldType

    def __init__(self, data_type_name: str, data_field_type: FieldType, data_field_name: str,
                 display_name: str):
        self.data_type_name = data_type_name
        self.data_field_type = data_field_type
        self.data_field_name = data_field_name
        self.display_name = display_name


def _parse_blocker_field_def(json_dct: Dict[str, Any], blocker_field: VeloxBlockerFieldDefinition[Any]) -> \
        AbstractVeloxFieldDefinition:
    blocker_field.hide_disabled_fields = json_dct.get('hideDisabledFields')
    blocker_field._dependent_fields_map = json_dct.get('dependentFieldMap')
    return blocker_field


def _parse_boolean_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    default_value: bool = json_dct.get('defaultValue')
    is_process_todo_item = json_dct.get('processTodoItem')
    field = VeloxBooleanFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                        base_params.display_name,
                                        default_value=default_value, is_process_todo_item=is_process_todo_item)
    return _parse_blocker_field_def(json_dct, field)


def _parse_double_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    min_value: float = float(json_dct.get('minValue'))
    max_value: float = float(json_dct.get('maxValue'))
    default_value: Optional[float] = json_dct.get('defaultValue')
    precision: int = int(json_dct.get('precision'))
    double_format_name: str = json_dct.get('doubleFormat')
    double_format: Optional[SapioDoubleFormat] = None
    if double_format_name:
        double_format = SapioDoubleFormat[double_format_name]
    return VeloxDoubleFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                      base_params.display_name,
                                      min_value=min_value, max_value=max_value, default_value=default_value,
                                      precision=precision, double_format=double_format)


def _parse_enum_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    default_value: int = json_dct.get('defaultValue')
    values: List[str] = json_dct.get('values')
    field = VeloxEnumFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                     base_params.display_name,
                                     default_value=default_value, values=values)
    return _parse_blocker_field_def(json_dct, field)


def _parse_int_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    min_value: int = json_dct.get('minValue')
    max_value: int = json_dct.get('maxValue')
    default_value: int = json_dct.get('defaultValue')
    unique_value: bool = json_dct.get('uniqueValue')
    if base_params.data_field_type == FieldType.INTEGER:
        return VeloxIntegerFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                           base_params.display_name,
                                           min_value=min_value, max_value=max_value, default_value=default_value,
                                           unique_value=unique_value)
    elif base_params.data_field_type == FieldType.LONG:
        return VeloxLongFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                        base_params.display_name,
                                        min_value=min_value, max_value=max_value, default_value=default_value,
                                        unique_value=unique_value)
    elif base_params.data_field_type == FieldType.SHORT:
        return VeloxShortFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                         base_params.display_name,
                                         min_value=min_value, max_value=max_value, default_value=default_value,
                                         unique_value=unique_value)


def _parse_string_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    default_value: str = json_dct.get('defaultValue')
    max_length: int = json_dct.get('maxLength')
    unique_value: bool = json_dct.get('uniqueValue')
    html_editor: bool = json_dct.get('htmlEditor')
    string_format: Optional[SapioStringFormat] = None
    if json_dct.get('stringFormat') is not None:
        string_format = SapioStringFormat[json_dct.get('stringFormat')]
    num_lines: Optional[int] = json_dct.get('numLines')
    auto_size: bool = json_dct.get('autoSize')
    link_out: Optional[bool] = json_dct.get('linkOut')
    link_out_url: Optional[str] = json_dct.get('linkOutUrl')
    field_validator: Optional[FieldValidator] = None
    if json_dct.get('fieldValidator') is not None:
        field_validator = _parse_field_validator(json_dct.get('fieldValidator'))

    return VeloxStringFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                      base_params.display_name,
                                      default_value=default_value, max_length=max_length, unique_value=unique_value,
                                      html_editor=html_editor, string_format=string_format,
                                      num_lines=num_lines, auto_size=auto_size, link_out=link_out,
                                      link_out_url=link_out_url, field_validator=field_validator)


def _parse_date_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    date_time_format: str = json_dct.get('dateTimeFormat')
    default_value: str = json_dct.get('defaultValue')
    static_date: bool = json_dct.get('staticDate')
    return VeloxDateFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                    base_params.display_name, date_time_format=date_time_format,
                                    default_value=default_value, static_date=static_date)


def _parse_date_range_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    date_time_format: str = json_dct.get('dateTimeFormat')
    default_value: str = json_dct.get('defaultValue')
    static_date: bool = json_dct.get('static')
    return VeloxDateRangeFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                         base_params.display_name, date_time_format=date_time_format,
                                         default_value=default_value, static_date=static_date)


def _parse_no_data_field_def(base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    if base_params.data_field_type == FieldType.ACTION:
        return VeloxActionFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                          base_params.display_name)
    elif base_params.data_field_type == FieldType.PARENTLINK:
        return VeloxParentFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                          base_params.display_name)
    elif base_params.data_field_type == FieldType.MULTIPARENTLINK:
        return VeloxMultiParentFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                               base_params.display_name)
    elif base_params.data_field_type == FieldType.IDENTIFIER:
        return VeloxIdentifierFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                              base_params.display_name)
    elif base_params.data_field_type == FieldType.CHILDLINK:
        return VeloxChildLinkFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                             base_params.display_name)
    else:
        raise ValueError('Unexpected no data field type: ' + str(base_params.data_field_type))


def _parse_selection_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    default_value: str = json_dct.get('defaultValue')
    list_mode_str: str = json_dct.get('listMode')
    unique_value: bool = json_dct.get('uniqueValue')
    multi_select: bool = json_dct.get('multiSelect')
    direct_edit: bool = json_dct.get('directEdit')
    static_list_values: list[str] | None = json_dct.get('staticListValues')
    list_mode: ListMode
    list_name: Optional[str] = None
    report_name: Optional[str] = None
    plugin_name: Optional[str] = None
    if list_mode_str.startswith(ListMode.LIST.list_mode_name):
        list_name = ssutil.removeprefix(list_mode_str, ListMode.LIST.list_mode_name)
        list_mode = ListMode.LIST
    elif list_mode_str.startswith(ListMode.REPORT.list_mode_name):
        report_name =  ssutil.removeprefix(list_mode_str, ListMode.REPORT.list_mode_name)
        list_mode = ListMode.REPORT
    elif list_mode_str.startswith(ListMode.PLUGIN.list_mode_name):
        plugin_name =  ssutil.removeprefix(list_mode_str, ListMode.PLUGIN.list_mode_name)
        list_mode = ListMode.PLUGIN
    elif list_mode_str.startswith(ListMode.USER_GROUP.list_mode_name):
        list_mode = ListMode.USER_GROUP
    elif list_mode_str.startswith(ListMode.NON_API_USER.list_mode_name):
        list_mode = ListMode.NON_API_USER
    elif list_mode_str.startswith(ListMode.USER.list_mode_name):
        list_mode = ListMode.USER
    else:
        raise ValueError("Cannot parse list mode data: " + list_mode_str)
    field = VeloxSelectionFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                          base_params.display_name,
                                          list_mode=list_mode, unique_value=unique_value, multi_select=multi_select,
                                          default_value=default_value, pick_list_name=list_name,
                                          custom_report_name=report_name, plugin_name=plugin_name,
                                          direct_edit=direct_edit, static_list_values=static_list_values)
    return _parse_blocker_field_def(json_dct, field)


def _parse_pick_list_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    default_value: str = json_dct.get('defaultValue')
    pick_list_name: str = json_dct.get('pickListName')
    direct_edit: bool = json_dct.get('directEdit')
    field = VeloxPickListFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                         base_params.display_name,
                                         pick_list_name=pick_list_name, default_value=default_value,
                                         direct_edit=direct_edit)
    return _parse_blocker_field_def(json_dct, field)


def _parse_accession_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    unique_value: bool = json_dct.get('uniqueValue')
    sequence_key: str = json_dct.get('sequenceKey')
    prefix: str = json_dct.get('prefix')
    suffix: str = json_dct.get('suffix')
    number_of_digits: int = json_dct.get('numberOfDigits')
    starting_value: Optional[int] = json_dct.get('startingValue')
    link_out: Optional[bool] = json_dct.get('linkOut')
    link_out_url: Optional[str] = json_dct.get('linkOutUrl')
    return VeloxAccessionFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                         base_params.display_name,
                                         sequence_key=sequence_key, prefix=prefix, suffix=suffix,
                                         number_of_digits=number_of_digits, unique_value=unique_value,
                                         starting_value=starting_value,
                                         link_out=link_out, link_out_url=link_out_url)


def _parse_side_link_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    linked_data_type_name: Optional[str] = json_dct.get('linkedDataTypeName')
    default_value: Optional[int] = json_dct.get('defaultValue')
    return VeloxSideLinkFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                        base_params.display_name,
                                        default_value=default_value, linked_data_type_name=linked_data_type_name)


def _parse_action_string_field_def(json_dct: Dict[str, Any], base_params: _FieldDefBaseParserParams) -> \
        AbstractVeloxFieldDefinition:
    default_value: str = json_dct.get('defaultValue')
    max_length: int = json_dct.get('maxLength')
    unique_value: bool = json_dct.get('uniqueValue')
    field_validator: Optional[FieldValidator] = None
    if json_dct.get('fieldValidator') is not None:
        field_validator = _parse_field_validator(json_dct.get('fieldValidator'))
    icon_name: Optional[str] = json_dct.get('iconName')
    action_plugin_path: Optional[str] = json_dct.get('actionPluginPath')
    direct_edit: bool = json_dct.get('directEdit')
    return VeloxActionStringFieldDefinition(base_params.data_type_name, base_params.data_field_name,
                                            base_params.display_name,
                                            default_value=default_value, max_length=max_length,
                                            unique_value=unique_value, field_validator=field_validator,
                                            icon_name=icon_name, action_plugin_path=action_plugin_path,
                                            direct_edit=direct_edit)


def _parse_abstract_field_def(json_dct: Dict[str, Any]) -> AbstractVeloxFieldDefinition:
    data_type_name: str = json_dct.get('dataTypeName')
    data_field_type: FieldType = FieldType[json_dct.get('dataFieldType')]
    data_field_name: str = json_dct.get('dataFieldName')
    display_name: str = json_dct.get('displayName')

    base_params = _FieldDefBaseParserParams(data_type_name, data_field_type, data_field_name, display_name)

    ret: AbstractVeloxFieldDefinition
    if data_field_type == FieldType.BOOLEAN:
        ret = _parse_boolean_field_def(json_dct, base_params)
    elif data_field_type == FieldType.DOUBLE:
        ret = _parse_double_field_def(json_dct, base_params)
    elif data_field_type == FieldType.ENUM:
        ret = _parse_enum_field_def(json_dct, base_params)
    elif data_field_type in [FieldType.INTEGER, FieldType.LONG, FieldType.SHORT]:
        ret = _parse_int_field_def(json_dct, base_params)
    elif data_field_type == FieldType.STRING:
        ret = _parse_string_field_def(json_dct, base_params)
    elif data_field_type == FieldType.DATE:
        ret = _parse_date_field_def(json_dct, base_params)
    elif data_field_type in [FieldType.ACTION, FieldType.PARENTLINK, FieldType.MULTIPARENTLINK,
                             FieldType.IDENTIFIER, FieldType.CHILDLINK]:
        ret = _parse_no_data_field_def(base_params)
    elif data_field_type == FieldType.SELECTION:
        ret = _parse_selection_field_def(json_dct, base_params)
    elif data_field_type == FieldType.PICKLIST:
        ret = _parse_pick_list_def(json_dct, base_params)
    elif data_field_type == FieldType.AUTO_ACCESSION:
        ret = _parse_accession_field_def(json_dct, base_params)
    elif data_field_type == FieldType.DATE_RANGE:
        ret = _parse_date_range_field_def(json_dct, base_params)
    elif data_field_type == FieldType.SIDE_LINK:
        ret = _parse_side_link_field_def(json_dct, base_params)
    elif data_field_type == FieldType.ACTION_STRING:
        ret = _parse_action_string_field_def(json_dct, base_params)
    else:
        raise ValueError('Unexpected field type: ' + str(data_field_type))

    description: Optional[str] = json_dct.get('description')
    ret.description = description
    required: bool = json_dct.get('required')
    ret.required = required
    editable: bool = json_dct.get('editable')
    ret.editable = editable
    visible: bool = json_dct.get('visible')
    ret.visible = visible
    identifier: bool = json_dct.get('identifier')
    ret.identifier = identifier
    identifier_order: int = json_dct.get('identifierOrder')
    ret.identifier_order = identifier_order
    sort_direction_name: Optional[str] = json_dct.get('sortDirection')
    sort_direction = SortDirectionParser.parse_sort_direction(sort_direction_name)
    ret.sort_direction = sort_direction
    sort_order: int = json_dct.get('sortOrder')
    ret.sort_order = sort_order
    tag: str = json_dct.get('tag')
    ret.tag = tag
    key_field: bool = json_dct.get('keyField')
    ret.key_field = key_field
    key_field_order: int = json_dct.get('keyFieldOrder')
    ret.key_field_order = key_field_order
    system_field: bool = json_dct.get('systemField')
    ret.system_field = system_field
    audit_logged: bool = json_dct.get('auditLogged')
    ret.audit_logged = audit_logged
    default_table_column_width: int = json_dct.get('defaultTableColumnWidth')
    ret.default_table_column_width = default_table_column_width
    return ret


def _parse_field_validator(json_dct: Dict[str, Any]) -> FieldValidator:
    validation_regex: str = json_dct.get('validationRegex')
    error_message: str = json_dct.get('errorMessage')
    return FieldValidator(validation_regex=validation_regex, error_message=error_message)
