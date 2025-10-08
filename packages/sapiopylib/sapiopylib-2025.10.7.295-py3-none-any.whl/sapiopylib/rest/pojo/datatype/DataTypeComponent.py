import datetime
from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Optional, Dict, List, Any

from sapiopylib.rest.pojo.datatype.DataTypeDescriptors import DataFieldDescriptor, DataFieldDescriptorParser
from sapiopylib.rest.pojo.datatype.DataTypeEnums import *
from sapiopylib.rest.utils.SapioDateUtils import date_time_to_java_millis, java_millis_to_datetime


@total_ordering
class FieldDefinitionPosition:
    """
    Position of a field within a form component. The field definition also needs to be on the data type.

    form_name: The name of the form to be displayed in for this position.

    data_field_name: The data field name of this position.

    order: The order of the field in the form.

    form_column: The column position this form starts at.

    form_column_span: Length of this form column in number of columns.

    field_height: The height of the field to be displayed in the layout.
    If this value is set to null then the client will generate a value based on the
    VeloxStringFieldDefinition.num_lines value.
    This value will only be used for String fields and Selection List fields.
    """
    form_name: Optional[str]
    data_field_name: str
    order: Optional[int]
    form_column: Optional[int]
    form_column_span: Optional[int]
    field_height: Optional[int]

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, FieldDefinitionPosition):
            return False
        return self.form_name == other.form_name and self.data_field_name == other.data_field_name and \
            self.order == other.order and self.form_column == other.form_column

    def __hash__(self):
        return hash((self.form_name, self.data_field_name, self.order))

    def __lt__(self, other):
        if other is None:
            return False
        if not isinstance(other, FieldDefinitionPosition):
            return False
        if self.order != other.order:
            return self.order < other.order
        if self.form_column != other.form_column:
            return self.form_column < other.form_column
        return self.data_field_name < other.data_field_name

    def __init__(self, data_field_name: str,
                 form_name: Optional[str] = None, order: Optional[int] = None, form_column: Optional[int] = None,
                 form_column_span: Optional[int] = None, field_height: Optional[int] = None):
        self.form_name = form_name
        self.data_field_name = data_field_name
        self.order = order
        self.form_column = form_column
        self.form_column_span = form_column_span
        self.field_height = field_height

    def to_pojo(self) -> Dict[str, Any]:
        return {
            'formName': self.form_name,
            'dataFieldName': self.data_field_name,
            'order': self.order,
            'formColumn': self.form_column,
            'formColumnSpan': self.form_column_span,
            'fieldHeight': self.field_height
        }


def _parse_field_definition_position(json_dct: Dict[str, Any]) -> FieldDefinitionPosition:
    form_name: Optional[str] = json_dct.get('formName')
    data_field_name: str = json_dct.get('dataFieldName')
    order: Optional[int] = json_dct.get('order')
    form_column: Optional[int] = json_dct.get('formColumn')
    form_column_span: Optional[int] = json_dct.get('formColumnSpan')
    field_height: Optional[int] = json_dct.get('fieldHeight')
    return FieldDefinitionPosition(data_field_name, form_name=form_name, order=order, form_column=form_column,
                                   form_column_span=form_column_span, field_height=field_height)


class AbstractCalendarDataSource(ABC):
    """
    Abstract calendar data source, subclasses describe how calendar component shall retrieve data when being rendered.

    data_type_name: The data type name that this data source is providing.

    data_field_name: The data field name from provided data type name.

    end_date_field_name: The end date to use with the calendar.
    This field is only needed to provide a range when the primary dataFieldName is a Date instead of a DateRange field.
    """
    data_type_name: str
    data_field_name: str
    end_date_field_name: Optional[str]

    def __init__(self, data_type_name: str, data_field_name: str, end_date_field_name: Optional[str]):
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name
        self.end_date_field_name = end_date_field_name

    @abstractmethod
    def get_data_source_type(self) -> CalendarDataSourceType:
        pass

    def to_pojo(self) -> Dict[str, Any]:
        return {
            'dataSourceType': self.get_data_source_type().name,
            'dataTypeName': self.data_type_name,
            'dataFieldName': self.data_field_name,
            'endDateFieldName': self.end_date_field_name
        }


class CalendarReportDataSource(AbstractCalendarDataSource):

    def __init__(self, data_type_name: str, data_field_name: str, end_date_field_name: Optional[str]):
        super().__init__(data_type_name, data_field_name, end_date_field_name)

    def get_data_source_type(self) -> CalendarDataSourceType:
        return CalendarDataSourceType.REPORT


class CalendarAllRecordsOfTypeDataSource(AbstractCalendarDataSource):

    def __init__(self, data_type_name: str, data_field_name: str, end_date_field_name: Optional[str]):
        super().__init__(data_type_name, data_field_name, end_date_field_name)

    def get_data_source_type(self) -> CalendarDataSourceType:
        return CalendarDataSourceType.ALL_RECS_OF_TYPE


def _parse_calendar_data_source(json_dct: Dict[str, Any]):
    data_source_type: CalendarDataSourceType = CalendarDataSourceType[json_dct.get('dataSourceType')]
    data_type_name: str = json_dct.get('dataTypeName')
    data_field_name: str = json_dct.get('dataFieldName')
    end_date_field_name: Optional[str] = json_dct.get('endDateFieldName')
    if data_source_type == CalendarDataSourceType.REPORT:
        return CalendarReportDataSource(data_type_name, data_field_name, end_date_field_name)
    elif data_source_type == CalendarDataSourceType.ALL_RECS_OF_TYPE:
        return CalendarAllRecordsOfTypeDataSource(data_type_name, data_field_name, end_date_field_name)
    else:
        raise NotImplemented("Unexpected calendar data source type: " + data_source_type.name)


class AbstractViewDetails(ABC):
    """
    Abstract class used to contain common attributes between
    the different table views that require additional attributes
    to function like the kanban view.
    """
    data_type_name: Optional[str]
    data_field_name: Optional[str]

    @abstractmethod
    def get_view_detail_type(self) -> ViewDetailsType:
        pass

    def __init__(self, data_type_name: Optional[str], data_field_name: Optional[str]):
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name

    def to_pojo(self) -> Dict[str, Any]:
        return {
            'viewDetailType': self.get_view_detail_type().name,
            'dataTypeName': self.data_type_name,
            'dataFieldName': self.data_field_name
        }


class KanbanDetails(AbstractViewDetails):
    """
    This class specifies the field to group on as well as any additional configurations
    that may need to be applied to the component it gets set on.
    """
    aggregate_field_name: Optional[str]
    aggregate_type: Optional[AggregationType]
    value_black_list: List[str]
    data_field_list: List[DataFieldDescriptor]
    show_unassigned_category: bool

    def __init__(self, data_type_name: Optional[str], data_field_name: Optional[str],
                 aggregate_field_name: Optional[str], aggregate_type: Optional[AggregationType],
                 value_black_list: Optional[List[str]] = None,
                 data_field_list: Optional[List[DataFieldDescriptor]] = None,
                 show_unassigned_category: bool = False):
        super().__init__(data_type_name, data_field_name)
        if data_field_list is None:
            data_field_list = []
        if value_black_list is None:
            value_black_list = []
        self.aggregate_field_name = aggregate_field_name
        self.aggregate_type = aggregate_type
        self.value_black_list = value_black_list
        self.data_field_list = data_field_list
        self.show_unassigned_category = show_unassigned_category

    def get_view_detail_type(self) -> ViewDetailsType:
        return ViewDetailsType.KANBAN

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['aggregateFieldName'] = self.aggregate_field_name
        ret['aggregationType'] = self.aggregate_type.name
        ret['valueBlackList'] = self.value_black_list
        ret['dataFieldList'] = self.data_field_list
        ret['showUnassignedCategory'] = self.show_unassigned_category
        return ret


class FormCyclerDetails(AbstractViewDetails):
    """
    Includes additional form cycler component view configurations.

    record_image_placement: Determines if the record image should show or not.

    custom_form_fields_to_show: Retrieves the field list to show.
    """
    record_image_placement: Optional[RecordImagePlacement]
    custom_form_fields_to_show: List[DataFieldDescriptor]

    def get_view_detail_type(self) -> ViewDetailsType:
        return ViewDetailsType.FORM_CYCLER

    def __init__(self, data_type_name: Optional[str], data_field_name: Optional[str],
                 record_image_placement: Optional[RecordImagePlacement] = None,
                 custom_form_fields_to_show: Optional[List[DataFieldDescriptor]] = None):
        super().__init__(data_type_name, data_field_name)
        if custom_form_fields_to_show is None:
            custom_form_fields_to_show = []
        self.record_image_placement = record_image_placement
        self.custom_form_fields_to_show = custom_form_fields_to_show

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        if self.record_image_placement is not None:
            ret['recordImagePlacement'] = self.record_image_placement.name
        ret['customFormFieldsToShow'] = self.custom_form_fields_to_show
        return ret


def _parse_view_details(json_dct: Dict[str, Any]) -> AbstractViewDetails:
    view_detail_type: ViewDetailsType = ViewDetailsType[json_dct.get('viewDetailType')]
    data_type_name: Optional[str] = json_dct.get('dataTypeName')
    data_field_name: Optional[str] = json_dct.get('dataFieldName')
    if view_detail_type == ViewDetailsType.KANBAN:
        aggregate_field_name: Optional[str] = json_dct.get('aggregateFieldName')
        aggregate_type: Optional[AggregationType] = None
        aggregate_type_name: Optional[str] = json_dct.get('aggregationType')
        if aggregate_type_name is not None and len(aggregate_type_name) > 0:
            aggregate_type = AggregationType[aggregate_type_name]
        value_black_list: Optional[List[str]] = json_dct.get('valueBlackList')
        data_field_list: Optional[List[DataFieldDescriptor]] = None
        data_field_parse_list = json_dct.get('dataFieldList')
        if data_field_parse_list is not None:
            data_field_list = [DataFieldDescriptorParser.parse_data_field_descriptor(x) for x in data_field_parse_list]
        show_unassigned_category: bool = json_dct.get('showUnassignedCategory')
        return KanbanDetails(data_type_name, data_field_name,
                             aggregate_field_name=aggregate_field_name, aggregate_type=aggregate_type,
                             value_black_list=value_black_list, data_field_list=data_field_list,
                             show_unassigned_category=show_unassigned_category)
    elif view_detail_type == ViewDetailsType.FORM_CYCLER:
        record_image_placement: Optional[RecordImagePlacement] = None
        record_image_placement_name: Optional[str] = json_dct.get('recordImagePlacement')
        if record_image_placement_name is not None and len(record_image_placement_name) > 0:
            record_image_placement = RecordImagePlacement[record_image_placement_name]
        custom_form_fields_to_show: Optional[List[DataFieldDescriptor]] = None
        custom_form_fields_parse_list = json_dct.get('customFormFieldsToShow')
        if custom_form_fields_parse_list is not None:
            custom_form_fields_to_show = [DataFieldDescriptorParser.parse_data_field_descriptor(x)
                                          for x in custom_form_fields_parse_list]
        return FormCyclerDetails(data_type_name, data_field_name,
                                 record_image_placement=record_image_placement,
                                 custom_form_fields_to_show=custom_form_fields_to_show)
    else:
        raise NotImplemented("Unexpected view details type: " + view_detail_type.name)


@total_ordering
class AbstractDataTypeComponent(ABC):
    """
    A component within an outer data type tab layout.
    """
    component_name: str
    display_name: str
    description: Optional[str]
    parent_tab_name: Optional[str]
    order: int
    column: int
    column_span: int
    height: int
    hide_heading: bool
    hide_header_icon: bool
    collapsed: bool
    component_tag: Optional[str]
    active: bool
    hide_if_no_data: bool

    def __init__(self, component_name: str, display_name: str,
                 description: Optional[str] = None, parent_tab_name: Optional[str] = None,
                 order: int = 0, column: int = 0, column_span: int = 4, height: int = 200,
                 hide_heading: bool = False, hide_header_icon: bool = False, collapsed: bool = False,
                 component_tag: Optional[str] = None, active: bool = True, hide_if_no_data: bool = False):
        self.component_name = component_name
        self.display_name = display_name
        self.description = description
        self.parent_tab_name = parent_tab_name
        self.order = order
        self.column = column
        self.column_span = column_span
        self.height = height
        self.hide_heading = hide_heading
        self.hide_header_icon = hide_header_icon
        self.collapsed = collapsed
        self.component_tag = component_tag
        self.active = active
        self.hide_if_no_data = hide_if_no_data

    def __str__(self):
        return self.display_name

    def __hash__(self):
        return hash(self.component_name)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, AbstractDataTypeComponent):
            return False
        return self.component_name == other.component_name

    def __lt__(self, other):
        if other is None:
            return False
        if not isinstance(other, AbstractDataTypeComponent):
            return False
        if self.order != other.order:
            return self.order < other.order
        if self.column != other.column:
            return self.column < other.column
        if self.display_name != other.display_name:
            return self.display_name < other.display_name
        return self.component_name < other.component_name

    @abstractmethod
    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        pass

    def to_pojo(self) -> Dict[str, Any]:
        ret: dict = {
            'layoutComponentType': self.get_layout_component_type().name,
            'componentName': self.component_name,
            'displayName': self.display_name,
            'description': self.description,
            'parentTabName': self.parent_tab_name,
            'order': self.order,
            'column': self.column,
            'columnSpan': self.column_span,
            'height': self.height,
            'hideHeading': self.hide_heading,
            'hideHeaderIcon': self.hide_header_icon,
            'collapsed': self.collapsed,
            'componentTag': self.component_tag,
            'active': self.active,
            'hideIfNoData': self.hide_if_no_data
        }
        return ret

    def set_optional_fields_from_json(self, json_dct: Dict[str, Any]):
        self.description = json_dct.get('description')
        self.parent_tab_name = json_dct.get('parentTabName')
        self.order = json_dct.get('order')
        self.column = json_dct.get('column')
        self.column_span = json_dct.get('columnSpan')
        self.height = json_dct.get('height')
        self.hide_heading = json_dct.get('hideHeading')
        self.hide_header_icon = json_dct.get('hideHeaderIcon')
        self.collapsed = json_dct.get('collapsed')
        self.component_tag = json_dct.get('componentTag')
        self.active = json_dct.get('active')
        self.hide_if_no_data = json_dct.get('hideIfNoData')


@total_ordering
class DataTypeComponentTabDefinition:
    """
    Defines what is within this (inner) tab.

    tab_name: This should match the map's key. Unique within the tab component.
    tab_display_name: The tab's display name to end users.
    tab_order: The order of this tab among all inner tabs at same level.
    layout_component: The component to be displayed inside this tab.
    """
    tab_name: str
    tab_display_name: str
    tab_order: Optional[int]
    layout_component: AbstractDataTypeComponent

    def __init__(self, tab_name: str, tab_display_name: str, tab_order: Optional[int],
                 layout_component: AbstractDataTypeComponent):
        self.tab_name = tab_name
        self.tab_display_name = tab_display_name
        self.tab_order = tab_order
        self.layout_component = layout_component

    def to_pojo(self) -> Dict[str, Any]:
        return {
            'tabName': self.tab_name,
            'tabDisplayName': self.tab_display_name,
            'tabOrder': self.tab_order,
            'layoutComponent': self.layout_component.to_pojo()
        }

    def __hash__(self):
        return hash((self.tab_order, self.tab_display_name, self.tab_name))

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, DataTypeComponentTabDefinition):
            return False
        return self.tab_order == other.tab_order and self.tab_display_name == other.tab_display_name and \
            self.tab_name == other.tab_name

    def __le__(self, other):
        if other is None:
            return False
        if not isinstance(other, DataTypeComponentTabDefinition):
            return False
        if self.tab_order != other.tab_order:
            return self.tab_order < other.tab_order
        if self.tab_display_name != other.tab_display_name:
            return self.tab_display_name < other.tab_display_name
        return self.tab_name != other.tab_name

    def __str__(self):
        return self.tab_display_name


def _parse_data_type_component_tab_def(json_dct: Dict[str, Any]) -> DataTypeComponentTabDefinition:
    tab_name: str = json_dct.get('tabName')
    tab_display_name: str = json_dct.get('tabDisplayName')
    tab_order: int = json_dct.get('tabOrder')
    layout_component: AbstractDataTypeComponent = DataTypeComponentParser.parse_data_type_component(
        json_dct.get('layoutComponent'))
    return DataTypeComponentTabDefinition(tab_name=tab_name, tab_display_name=tab_display_name,
                                          tab_order=tab_order, layout_component=layout_component)


class AbstractDashboardViewRecordComponent(AbstractDataTypeComponent):
    dashboard_guid_list: Optional[List[str]]
    default_dashboard_size: int

    def __init__(self, component_name: str, display_name: str,
                 dashboard_guid_list: Optional[List[str]] = None, default_dashboard_size: int = 50):
        super().__init__(component_name, display_name)
        self.dashboard_guid_list = dashboard_guid_list
        self.default_dashboard_size = default_dashboard_size

    @abstractmethod
    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        pass

    def to_pojo(self) -> Dict[str, Any]:
        ret: dict = super().to_pojo()
        ret['dashboardGuidList'] = self.dashboard_guid_list
        ret['defaultDashboardSize'] = self.default_dashboard_size
        return ret

    def set_optional_fields_from_json(self, json_dct: Dict[str, Any]):
        super().set_optional_fields_from_json(json_dct)
        self.dashboard_guid_list = json_dct.get('dashboardGuidList')
        self.default_dashboard_size = json_dct.get('defaultDashboardSize')


class AbstractTableLayoutComponent(AbstractDashboardViewRecordComponent):
    """
    Layouts that can be rendered in a table format within a form. Note the actual display may not be in table format.
    display_type: How shall this component be displayed to user. If not specified, the default is usually Table.

    view_details: Attributes that configures the data of this view. Usually should be not blank.

    default_dashboard_guid: The chart that shows initially in the right pop-out of this component.

    hide_field_labels: Whether to hide field labels in titles of the view.

    disable_search_changing_menu: Determines if the 'change search' menu should appear or not in the component's header.

    toolbar_group_function_black_list: Determines what toolbar features are to be omitted from the usual toolbar
    of this collection display type.

    hide_paging_toolbar: Determines if the component should show a paging toolbar or not.
    If not, the component will only ever get the first page of data.
    """
    display_type: Optional[DisplayType]
    view_details: Optional[AbstractViewDetails]
    default_dashboard_guid: Optional[str]
    hide_field_labels: bool
    disable_search_changing_menu: bool
    toolbar_group_function_black_list: List[str]
    hide_paging_toolbar: bool

    def __init__(self, component_name: str, display_name: str,
                 display_type: Optional[DisplayType] = None,
                 view_details: Optional[AbstractViewDetails] = None,
                 default_dashboard_guid: Optional[str] = None, hide_field_labels: bool = False,
                 disable_search_changing_menu: bool = False,
                 toolbar_group_function_black_list: Optional[List[str]] = None,
                 hide_paging_toolbar: bool = False):
        super().__init__(component_name, display_name)
        if toolbar_group_function_black_list is None:
            toolbar_group_function_black_list = []
        self.display_type = display_type
        self.view_details = view_details
        self.default_dashboard_guid = default_dashboard_guid
        self.hide_field_labels = hide_field_labels
        self.disable_search_changing_menu = disable_search_changing_menu
        self.toolbar_group_function_black_list = toolbar_group_function_black_list
        self.hide_paging_toolbar = hide_paging_toolbar

    @abstractmethod
    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        pass

    def to_pojo(self) -> Dict[str, Any]:
        ret: dict = super().to_pojo()
        if self.display_type is not None:
            ret['displayType'] = self.display_type.name
        if self.view_details is not None:
            ret['viewDetails'] = self.view_details.to_pojo()
        ret['defaultDashboardGuid'] = self.default_dashboard_guid
        ret['hideFieldLabels'] = self.hide_field_labels
        ret['disableSearchChangingMenu'] = self.disable_search_changing_menu
        ret['toolbarGroupFunctionBlackList'] = self.toolbar_group_function_black_list
        ret['hidePagingToolbar'] = self.hide_paging_toolbar
        return ret

    def set_optional_fields_from_json(self, json_dct: Dict[str, Any]):
        super().set_optional_fields_from_json(json_dct)
        display_type_name: Optional[str] = json_dct.get('displayType')
        if display_type_name is not None and len(display_type_name) > 0:
            self.display_type = DisplayType[display_type_name]
        else:
            self.display_type = None
        view_details_to_parse = json_dct.get('viewDetails')
        if view_details_to_parse is not None:
            self.view_details = DataTypeComponentParser.parse_view_details(view_details_to_parse)
        self.default_dashboard_guid = json_dct.get('defaultDashboardGuid')
        self.hide_field_labels = json_dct.get('hideFieldLabels')
        self.disable_search_changing_menu = json_dct.get('disableSearchChangingMenu')
        self.toolbar_group_function_black_list = json_dct.get('toolbarGroupFunctionBlackList')
        self.hide_paging_toolbar = json_dct.get('hidePagingToolbar')


class RelatedRecordLayoutComponentBase(AbstractTableLayoutComponent, ABC):
    """
    Base class to support IDV components displaying tables of related records.
    """
    related_data_type_name: str
    related_extension_type_name: Optional[str]
    show_key_fields_only: bool
    hide_toolbar: bool

    def __init__(self, component_name: str, display_name: str,
                 related_data_type_name: str, related_extension_type_name: Optional[str], show_key_fields_only: bool,
                 hide_toolbar: bool):
        super().__init__(component_name, display_name)
        self.related_data_type_name = related_data_type_name
        self.related_extension_type_name = related_extension_type_name
        self.show_key_fields_only = show_key_fields_only
        self.hide_toolbar = hide_toolbar

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['relatedDataTypeName'] = self.related_data_type_name
        ret['relatedExtensionTypeName'] = self.related_extension_type_name
        ret['showKeyFieldsOnly'] = self.show_key_fields_only
        ret['hideToolbar'] = self.hide_toolbar
        return ret


class RelatedRecordLayoutComponent(RelatedRecordLayoutComponentBase):
    """
    A data type component displays a table of parents, a table of children,
    a table of ancestors, or a table of descendants.
    """
    component_relation_type: Optional[ComponentRelationType]

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.RELATED_RECORDS_COMPONENT

    def __init__(self, component_name: str, display_name: str,
                 component_relation_type: Optional[ComponentRelationType],
                 related_data_type_name: str, related_extension_type_name: Optional[str], show_key_fields_only: bool,
                 hide_toolbar: bool):
        super().__init__(component_name, display_name,
                         related_data_type_name, related_extension_type_name, show_key_fields_only, hide_toolbar)
        self.component_relation_type = component_relation_type

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        # PR-51544 none type check
        if self.component_relation_type:
            ret['componentRelationType'] = self.component_relation_type.name
        return ret


class SearchLayoutComponent(AbstractTableLayoutComponent):
    """
    Display custom report search results in this data type component.
    """
    custom_report_name: str
    hide_toolbar: bool
    query_restriction: Optional[ComponentRelationType]

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.SEARCH_COMPONENT

    def __init__(self, component_name: str, display_name: str,
                 custom_report_name: str, hide_toolbar: bool = False,
                 query_restriction: Optional[ComponentRelationType] = None):
        super().__init__(component_name, display_name)
        self.custom_report_name = custom_report_name
        self.hide_toolbar = hide_toolbar
        self.query_restriction = query_restriction

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['customReportName'] = self.custom_report_name
        ret['hideToolbar'] = self.hide_toolbar
        if self.query_restriction is not None:
            ret['queryRestriction'] = self.query_restriction.name
        return ret


class HierarchyComponent(AbstractDashboardViewRecordComponent):
    """
    Component to display a hierarchy view from the data type backing the layout.

    hierarchy_node_data_types: The list of data types in the hierarchy from the type backing this layout.
    These are the types that will be displayed in the hierarchy component.  Any types not included will be filtered out.

    toolbar_group_function_black_list: The toolbar functions that are not supported on the hierarchy nodes.
    Any functions listed in this field will not show on the node toolbars.

    fields_to_show_by_type: The fields that should be displayed in the hierarchy nodes keyed by the node
    data type that they are to be displayed on.
    """
    hierarchy_node_data_types: List[str]
    toolbar_group_function_black_list: Optional[List[str]]
    fields_to_show_by_type: Optional[Dict[str, List[DataFieldDescriptor]]]

    def __init__(self, component_name: str, display_name: str,
                 hierarchy_node_data_types: List[str],
                 toolbar_group_function_black_list: Optional[List[str]] = None,
                 fields_to_show_by_type: Optional[Dict[str, List[DataFieldDescriptor]]] = None):
        super().__init__(component_name, display_name)
        self.hierarchy_node_data_types = hierarchy_node_data_types
        self.toolbar_group_function_black_list = toolbar_group_function_black_list
        self.fields_to_show_by_type = fields_to_show_by_type

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.HIERARCHY_COMPONENT

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['hierarchyNodeDataTypeSet'] = self.hierarchy_node_data_types
        ret['toolbarGroupFunctionBlackList'] = self.toolbar_group_function_black_list
        if self.fields_to_show_by_type is not None:
            fields_to_show_pojo_map = dict()
            for key, value in self.fields_to_show_by_type.items():
                fields_to_show_pojo_map[key] = [x.to_pojo() for x in value]
            ret['fieldsToShowByType'] = fields_to_show_pojo_map
        return ret


class AbstractPluginComponent(AbstractDataTypeComponent):
    """
    Abstract client and server plugin components inside a data type layout

    plugin_path: The fully qualified plugin pass that will be executed to render this component.
    plugin_component_attributes: Any additional attributes for this plugin component, sent to the plugin.
    """
    plugin_path: Optional[str]
    plugin_component_attributes: Optional[Dict[str, str]]

    def __init__(self, component_name: str, display_name: str,
                 plugin_path: str = None, plugin_component_attributes: Dict[str, str] = None):
        super().__init__(component_name, display_name)
        self.plugin_path = plugin_path
        self.plugin_component_attributes = plugin_component_attributes

    @abstractmethod
    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        pass

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['pluginPath'] = self.plugin_path
        ret['pluginComponentAttributes'] = self.plugin_component_attributes
        return ret

    def set_optional_fields_from_json(self, json_dct: Dict[str, Any]):
        self.plugin_path = json_dct.get('pluginPath')
        self.plugin_component_attributes = json_dct.get('pluginComponentAttributes')


class ClientPluginComponent(AbstractPluginComponent):

    def __init__(self, component_name: str, display_name: str):
        super().__init__(component_name, display_name)

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.CLIENT_PLUGIN_COMPONENT


class TemporaryDataComponent(AbstractPluginComponent):

    def __init__(self, component_name: str, display_name: str):
        super().__init__(component_name, display_name)

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.TEMP_DATA_COMPONENT


class AttachmentPreviewComponent(AbstractDataTypeComponent):
    """
    A component that displays the content preview of an attachment. Some file types are not supported.

    preview_display_type: What is the size of content in this component.
    """
    preview_display_type: PreviewDisplayType

    def __init__(self, component_name: str, display_name: str,
                 preview_display_type: PreviewDisplayType):
        super().__init__(component_name, display_name)
        self.preview_display_type = preview_display_type

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.ATTACHMENT_PREVIEW_COMPONENT

    def to_pojo(self) -> Dict[str, Any]:
        ret = super().to_pojo()
        ret['previewDisplayType'] = self.preview_display_type.name
        return ret


class CalendarComponent(AbstractDataTypeComponent):
    """
    Data type component that displays a calendar view.

    hide_toolbar: Whether to hide the toolbar that is displayed on the calendar component.

    calendar_data_sources: A collection of data sources used to gather the data to back the calendar component.

    calendar_view: The default view of the calendar when it is first opened.

    calendar_default_start_time: The default start time that is used when displaying the component.
    The component will be displayed starting with this time of day.

    show_integrated_calendar_events: Whether events from an integrated calendar should be shown in the view in addition
    to the records returned by the data source.
    """
    hide_toolbar: bool
    calendar_data_sources: Optional[List[AbstractCalendarDataSource]]
    calendar_view: Optional[CalendarView]
    calendar_default_start_time: Optional[int]
    show_integrated_calendar_events: bool

    def __init__(self, component_name: str, display_name: str,
                 hide_toolbar: bool = False,
                 calendar_data_sources: Optional[List[AbstractCalendarDataSource]] = None,
                 calendar_view: Optional[CalendarView] = None,
                 calendar_default_start_time: Optional[int] = None,
                 show_integrated_calendar_events: bool = False):
        super().__init__(component_name, display_name)
        self.hide_toolbar = hide_toolbar
        self.calendar_data_sources = calendar_data_sources
        self.calendar_view = calendar_view
        self.calendar_default_start_time = calendar_default_start_time
        self.show_integrated_calendar_events = show_integrated_calendar_events

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.CALENDAR_COMPONENT

    def to_pojo(self) -> Dict[str, Any]:
        ret = super().to_pojo()
        ret['hideToolbar'] = self.hide_toolbar
        if self.calendar_data_sources is not None:
            ret['calendarDataSources'] = [x.to_pojo() for x in self.calendar_data_sources]
        if self.calendar_view is not None:
            ret['calendarView'] = self.calendar_view.name
        ret['calendarDefaultStartTime'] = self.calendar_default_start_time
        ret['showIntegratedCalendarEvents'] = self.show_integrated_calendar_events
        return ret

    def set_calendar_default_date_time(self, time: datetime.datetime):
        """
        Set the default time of the calendar view
        """
        self.calendar_default_start_time = date_time_to_java_millis(time)

    def get_calendar_default_date_time(self) -> datetime.datetime:
        """
        Get the default time of the calendar view.
        """
        return java_millis_to_datetime(self.calendar_default_start_time)


class DashboardComponent(AbstractDataTypeComponent):
    """
    A data type component that shows a chart (dashboard)

    dashboard_relation_type: How the data inside the dashboard is related to the current record.
    dashboard_data_type_name: Data type name of the data source.
    """
    dashboard_relation_type: ComponentRelationType
    dashboard_data_type_name: str

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.DASHBOARD_COMPONENT

    def __init__(self, component_name: str, display_name: str,
                 dashboard_relation_type: ComponentRelationType, dashboard_data_type_name: str):
        super().__init__(component_name, display_name)
        self.dashboard_relation_type = dashboard_relation_type
        self.dashboard_data_type_name = dashboard_data_type_name

    def to_pojo(self) -> Dict[str, Any]:
        ret = super().to_pojo()
        ret['dashboardRelationType'] = self.dashboard_relation_type.name
        ret['dashboardDataTypeName'] = self.dashboard_data_type_name
        return ret


class DataFormComponent(AbstractDataTypeComponent):
    """
    A data form within a tab of a data type layout or a temporary data type layout.

    field_def_position_map: All fields that will show up in this form will have their component layout
    details described here.
    """
    _field_def_position_map: Dict[str, FieldDefinitionPosition]

    def __init__(self, component_name: str, display_name: str,
                 field_def_position_map: Dict[str, FieldDefinitionPosition] = None):
        super().__init__(component_name, display_name)
        if field_def_position_map is None:
            field_def_position_map = dict()
        self._field_def_position_map = field_def_position_map

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.FORM_COMPONENT

    def set_field_definition_position(self, position: FieldDefinitionPosition) -> None:
        """
        Add a new field position to this form. The field should already exist as the data type's definition.
        Note: this setter will alter the original object's data to indicate it is set inside this form.
        :param position: The position object to be addd to this form.
        """
        position.form_name = self.component_name
        if position.order is None:
            position.order = len(self._field_def_position_map)
        self._field_def_position_map[position.data_field_name.upper()] = position

    def set_field_definition_position_list(self, pos_list: List[FieldDefinitionPosition]) -> None:
        """
        Re-set all field positions in this form, clearing out all existing position values first.
        Note: this setter will alter the original object's data to indicate it is set inside this form.
        :param pos_list: The position objects to be set to this form after deleting all existing positions.
        """
        self._field_def_position_map.clear()
        for pos in pos_list:
            self.set_field_definition_position(pos)

    def remove_field(self, data_field_name: str) -> Optional[FieldDefinitionPosition]:
        """
        Remove a field from this form.
        :return The field definition that has been deleted, or None, if it didn't exist when attempting to delete.
        """
        if data_field_name.upper() in self._field_def_position_map:
            ret = self._field_def_position_map.get(data_field_name.upper())
            del self._field_def_position_map[data_field_name.upper()]
            return ret
        return None

    def get_field_position(self, data_field_name: str) -> Optional[FieldDefinitionPosition]:
        """
        Get the field position of a data field.
        :param data_field_name: The data field to get position for.
        :return: None if not found, otherwise, the position object for this data field in this form.
        """
        return self._field_def_position_map.get(data_field_name.upper())

    @property
    def positions(self) -> list[FieldDefinitionPosition]:
        """
        Get sorted position list of all positions in this form in ascending order.
        """
        if not self._field_def_position_map:
            return []
        return sorted(self._field_def_position_map.values())

    @property
    def max_position(self) -> FieldDefinitionPosition | None:
        """
        Get the highest position we have in this form.
        """
        if not self._field_def_position_map:
            return None
        return max(self._field_def_position_map.values())

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        field_def_pojo_map = dict()
        for key, value in self._field_def_position_map.items():
            field_def_pojo_map[key] = value.to_pojo()
        ret['fieldDefinitionPositionMap'] = field_def_pojo_map
        return ret


class DataTypeFeedComponent(AbstractDataTypeComponent):
    """
    Data Type Layout component used to display feed information.

    descendant_name_list: The set of descendant data type names that will be displayed in the feed
    in addition to the current type.
    This will retrieve descendant record modifications, but will not show comments for descendant types.
    """
    descendant_name_list: Optional[List[str]]

    def __init__(self, component_name: str, display_name: str,
                 descendant_name_list: Optional[List[str]]):
        super().__init__(component_name, display_name)
        self.descendant_name_list = descendant_name_list

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['descendantNameSet'] = self.descendant_name_list
        return ret

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.FEED_COMPONENT


class DataTypeNewsFeedComponent(AbstractDataTypeComponent):
    data_type_name: Optional[str]
    relation_type: Optional[ComponentRelationType]
    data_field_name: Optional[str]

    def __init__(self, component_name: str, display_name: str,
                 data_type_name: Optional[str], relation_type: Optional[ComponentRelationType],
                 data_field_name: Optional[str]):
        super().__init__(component_name, display_name)
        self.data_type_name = data_type_name
        self.relation_type = relation_type
        self.data_field_name = data_field_name

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.NEWS_FEED_COMPONENT

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['dataTypeName'] = self.data_type_name
        ret['dataFieldName'] = self.data_field_name
        if self.relation_type is not None:
            ret['relationType'] = self.relation_type.name
        return ret


class DataTypeTabComponent(AbstractDataTypeComponent):
    """
    A tab component. This is distinct from the outer tab component.
    This cannot be used as a direct tab from layout and need to be contained in an outer tab.
    """
    _tab_layout_by_upper_tab_name: Dict[str, DataTypeComponentTabDefinition]

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.TAB_COMPONENT

    def __init__(self, component_name: str, display_name: str,
                 tab_layout_by_upper_tab_name: Optional[Dict[str, DataTypeComponentTabDefinition]] = None):
        super().__init__(component_name, display_name)
        if tab_layout_by_upper_tab_name is None:
            tab_layout_by_upper_tab_name = dict()
        self._tab_layout_by_upper_tab_name = tab_layout_by_upper_tab_name

    def set_tab_definition(self, tab_def: DataTypeComponentTabDefinition) -> None:
        """
         Set a tab definition object on this tab component.  This method will either add a new tab definition or replace
         the existing definition if it is already on the component (by upper case of tab name)
        :param tab_def: The tab definition to be set onto this tab view.
        """
        if tab_def.tab_order is None:
            tab_def.tab_order = len(self._tab_layout_by_upper_tab_name)
        self._tab_layout_by_upper_tab_name[tab_def.tab_name.upper()] = tab_def

    def set_tab_definition_list(self, tab_def_list: List[DataTypeComponentTabDefinition]) -> None:
        """
        Set a list of tab definition objects on this tab component.  This method will replace the current set of tab
        definitions with those included in the list.
        :param tab_def_list: The new definitions to be set after existing tab definitions is cleared in this tab.
        """
        self._tab_layout_by_upper_tab_name.clear()
        for tab_def in tab_def_list:
            self.set_tab_definition(tab_def)

    def remove_tab_definition(self, tab_name: str) -> Optional[DataTypeComponentTabDefinition]:
        """
        If the tab by this tab name exists, remove the tab definition and return the removed object.
        If it does not exist, return None.
        """
        if tab_name.upper() in self._tab_layout_by_upper_tab_name:
            ret = self._tab_layout_by_upper_tab_name.get(tab_name.upper())
            del self._tab_layout_by_upper_tab_name[tab_name.upper()]
            return ret
        return None

    def get_tab_definition(self, tab_name: str) -> Optional[DataTypeComponentTabDefinition]:
        """
        Get the tab by the matching tab name.
        :param tab_name: The tab name to get the tab for.
        :return: None if not found, otherwise, the tab definition
        """
        return self._tab_layout_by_upper_tab_name[tab_name.upper()]

    def get_tab_definition_list(self) -> List[DataTypeComponentTabDefinition]:
        """
        Get the list of TabDefinition objects set on this component.
        """
        ret: List[DataTypeComponentTabDefinition] = list(self._tab_layout_by_upper_tab_name.values())
        ret.sort()
        return ret

    def get_component_list(self) -> List[AbstractDataTypeComponent]:
        """
        Get the list of components contained in the tabs on this component.
        """
        ret: List[AbstractDataTypeComponent] = list()
        for tab in self._tab_layout_by_upper_tab_name.values():
            ret.append(tab.layout_component)
        return ret

    def find_component(self, component_name: str) -> Optional[AbstractDataTypeComponent]:
        """
        Find the component that matches the given component name in the tabs on this component.
        If the component is not found within the tabs then a None result is returned.
        :param component_name: The component name to search for in this inner tab.
        """
        for tab in self._tab_layout_by_upper_tab_name.values():
            if tab.layout_component.component_name.upper() == component_name.upper():
                return tab.layout_component
        return None

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        tab_layout_pojo_map = dict()
        for key, value in self._tab_layout_by_upper_tab_name.items():
            tab_layout_pojo_map[key] = value.to_pojo()
        ret['tabLayoutDefinitionMap'] = tab_layout_pojo_map
        return ret


class ProcessViewComponent(AbstractDataTypeComponent):
    """
    This component class is used to define graphic views of pick list or selection list fields on a data type that are
    driven through a process.  The field backing this component can define process details that define a list of to-dos
    for each step in the process.
    """
    plugin_backed: bool
    data_field_name: str
    value_black_list: List[str]

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.PROCESS_VIEW_COMPONENT

    def __init__(self, component_name: str, display_name: str,
                 plugin_backed: bool, data_field_name: str, value_black_list: Optional[List[str]]):
        super().__init__(component_name, display_name)
        if value_black_list is None:
            value_black_list = list()
        self.plugin_backed = plugin_backed
        self.data_field_name = data_field_name
        self.value_black_list = value_black_list

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['pluginBacked'] = self.plugin_backed
        ret['dataFieldName'] = self.data_field_name
        ret['valueBlackList'] = self.value_black_list
        return ret


class RelatedNotebookComponent(AbstractDataTypeComponent):
    """
    A related notebook GUI component in the layout, showing notebook experiments that are hierarchically related.

    related_types_to_aggregate: Also includes related experiments from these child types.
    """
    related_types_to_aggregate: Optional[List[str]]

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.RELATED_NOTEBOOK_EXPERIMENTS

    def __init__(self, component_name: str, display_name: str,
                 related_types_to_aggregate: Optional[List[str]]):
        super().__init__(component_name, display_name)
        self.related_types_to_aggregate = related_types_to_aggregate

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['relatedTypeToAggregateSet'] = self.related_types_to_aggregate
        return ret


class RecordImageComponent(AbstractDataTypeComponent):
    """
    A component that displays the record image set on a given record.

    Attributes:
        preview_display_type: What is the size of the content in this component.
    """

    preview_display_type: PreviewDisplayType

    def __init__(self, component_name: str, display_name: str,
                 preview_display_type: PreviewDisplayType):
        super().__init__(component_name, display_name)
        self.preview_display_type = preview_display_type

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['previewDisplayType'] = self.preview_display_type.name
        return ret

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.RECORD_IMAGE_COMPONENT


class RelatedSideLinkLayoutComponent(RelatedRecordLayoutComponentBase):
    related_side_link_field_name: str

    def __init__(self, component_name: str, display_name: str,
                 related_side_link_field_name: str,
                 related_data_type_name: str, related_extension_type_name: Optional[str], show_key_fields_only: bool,
                 hide_toolbar: bool):
        super().__init__(component_name, display_name,
                         related_data_type_name, related_extension_type_name, show_key_fields_only, hide_toolbar)
        self.related_side_link_field_name = related_side_link_field_name

    def get_layout_component_type(self) -> DataTypeLayoutComponentTypes:
        return DataTypeLayoutComponentTypes.RELATED_SIDE_LINK_COMPONENT

    def to_pojo(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = super().to_pojo()
        ret['relatedSideLinkFieldName'] = self.related_side_link_field_name
        return ret


class DataTypeComponentParser:
    @staticmethod
    def parse_field_def_position(json_dct: Dict[str, Any]) -> FieldDefinitionPosition:
        return _parse_field_definition_position(json_dct)

    @staticmethod
    def parse_view_details(json_dct: Dict[str, Any]) -> AbstractViewDetails:
        return _parse_view_details(json_dct)

    @staticmethod
    def parse_calendar_data_source(json_dct: Dict[str, Any]) -> AbstractCalendarDataSource:
        return _parse_calendar_data_source(json_dct)

    # PR-51544 Fixed inner tab definition parsing.
    @staticmethod
    def parse_inner_tab_definition(json_dct: dict[str, Any]) -> DataTypeTabComponent:
        component_name: str = json_dct.get('componentName')
        display_name: str = json_dct.get('displayName')
        def_map_pojo: dict[str, dict[str, Any]] = json_dct.get('tabLayoutDefinitionMap')
        def_map: dict[str, DataTypeComponentTabDefinition] = dict()
        for key, v in def_map_pojo.items():
            component: DataTypeComponentTabDefinition = _parse_data_type_component_tab_def(v)
            def_map[key] = component
        return DataTypeTabComponent(component_name, display_name, def_map)

    @staticmethod
    def parse_data_type_component(json_dct: Dict[str, Any]) -> AbstractDataTypeComponent:
        component_name: str = json_dct.get('componentName')
        display_name: str = json_dct.get('displayName')
        component_type_name: str = json_dct.get('layoutComponentType')
        component_type: DataTypeLayoutComponentTypes = DataTypeLayoutComponentTypes[component_type_name]
        if component_type == DataTypeLayoutComponentTypes.FORM_COMPONENT:
            field_pos_pojo_map: Dict[str, Dict[str, Any]] = json_dct.get('fieldDefinitionPositionMap')
            field_pos_map: Dict[str, FieldDefinitionPosition] = dict()
            for key, pojo_list in field_pos_pojo_map.items():
                field_pos_map[key] = DataTypeComponentParser.parse_field_def_position(pojo_list)
            ret = DataFormComponent(component_name, display_name,
                                    field_pos_map)
        elif component_type == DataTypeLayoutComponentTypes.TAB_COMPONENT:
            tab_pojo_map: Dict[str, Dict[str, Any]] = json_dct.get('tabLayoutDefinitionMap')
            tab_map: dict[str, DataTypeComponentTabDefinition] = dict()
            for key, item in tab_pojo_map.items():
                tab_map[key] = _parse_data_type_component_tab_def(item)
            ret = DataTypeTabComponent(component_name, display_name,
                                       tab_map)
        elif component_type == DataTypeLayoutComponentTypes.ATTACHMENT_PREVIEW_COMPONENT:
            display_type: PreviewDisplayType = PreviewDisplayType[json_dct.get('previewDisplayType')]
            ret = AttachmentPreviewComponent(component_name, display_name,
                                             display_type)
        elif component_type == DataTypeLayoutComponentTypes.CLIENT_PLUGIN_COMPONENT:
            ret = ClientPluginComponent(component_name, display_name)
        elif component_type == DataTypeLayoutComponentTypes.TEMP_DATA_COMPONENT:
            ret = TemporaryDataComponent(component_name, display_name)
        elif component_type == DataTypeLayoutComponentTypes.DASHBOARD_COMPONENT:
            dashboard_relation_type: ComponentRelationType = \
                ComponentRelationType[json_dct.get('dashboardRelationType')]
            dashboard_data_type_name: str = json_dct.get('dashboardDataTypeName')
            ret = DashboardComponent(component_name, display_name,
                                     dashboard_relation_type, dashboard_data_type_name)
        elif component_type == DataTypeLayoutComponentTypes.PROCESS_VIEW_COMPONENT:
            plugin_backed: bool = json_dct.get('pluginBacked')
            data_field_name: str = json_dct.get('dataFieldName')
            value_black_list: Optional[List[str]] = json_dct.get('valueBlackList')
            ret = ProcessViewComponent(component_name, display_name,
                                       plugin_backed=plugin_backed, data_field_name=data_field_name,
                                       value_black_list=value_black_list)
        elif component_type == DataTypeLayoutComponentTypes.CALENDAR_COMPONENT:
            hide_toolbar: bool = json_dct.get('hideToolbar')

            calendar_data_sources: Optional[List[AbstractCalendarDataSource]] = None
            if json_dct.get('calendarDataSources') is not None:
                calendar_source_pojo_list: List[Dict[str, Any]] = json_dct.get('calendarDataSources')
                calendar_data_sources = [DataTypeComponentParser.parse_calendar_data_source(x)
                                         for x in calendar_source_pojo_list]

            calendar_view: Optional[CalendarView] = None
            calendar_view_name: Optional[str] = json_dct.get('calendarView')
            if calendar_view_name is not None and len(calendar_view_name) > 0:
                calendar_view = CalendarView[calendar_view_name]

            calendar_default_start_time: Optional[int] = json_dct.get('calendarDefaultStartTime')
            show_integrated_calendar_events: bool = json_dct.get('showIntegratedCalendarEvents')
            ret = CalendarComponent(component_name, display_name,
                                    hide_toolbar=hide_toolbar, calendar_data_sources=calendar_data_sources,
                                    calendar_view=calendar_view,
                                    calendar_default_start_time=calendar_default_start_time,
                                    show_integrated_calendar_events=show_integrated_calendar_events)
        elif component_type == DataTypeLayoutComponentTypes.HIERARCHY_COMPONENT:
            hierarchy_node_data_types: List[str] = json_dct.get('hierarchyNodeDataTypeSet')
            toolbar_group_function_black_list: Optional[List[str]] = json_dct.get('toolbarGroupFunctionBlackList')
            fields_to_show_by_type: Optional[Dict[str, List[DataFieldDescriptor]]] = dict()
            if json_dct.get('fieldsToShowByType') is not None:
                fields_to_show_pojo_dict: Dict[str, List[Dict[str, Any]]] = json_dct.get('fieldsToShowByType')
                for key, pojo_list in fields_to_show_pojo_dict.items():
                    fields_list = [DataFieldDescriptorParser.parse_data_field_descriptor(x) for x in pojo_list]
                    fields_to_show_by_type[key] = fields_list
            ret = HierarchyComponent(component_name, display_name,
                                     hierarchy_node_data_types, toolbar_group_function_black_list,
                                     fields_to_show_by_type)
        elif component_type == DataTypeLayoutComponentTypes.FEED_COMPONENT:
            descendant_name_list: Optional[List[str]] = json_dct.get('descendantNameSet')
            ret = DataTypeFeedComponent(component_name, display_name,
                                        descendant_name_list)
        elif component_type == DataTypeLayoutComponentTypes.NEWS_FEED_COMPONENT:
            data_type_name: Optional[str] = json_dct.get('dataTypeName')
            relation_type: Optional[ComponentRelationType] = None
            relation_type_name: Optional[str] = json_dct.get('relationType')
            if relation_type_name is not None and len(relation_type_name) > 0:
                relation_type = ComponentRelationType[relation_type_name]
            data_field_name: Optional[str] = json_dct.get('dataFieldName')
            ret = DataTypeNewsFeedComponent(component_name, display_name,
                                            data_type_name=data_type_name, relation_type=relation_type,
                                            data_field_name=data_field_name)
        elif component_type == DataTypeLayoutComponentTypes.RELATED_RECORDS_COMPONENT:
            component_relation_type: Optional[ComponentRelationType] = None
            component_relation_type_name: Optional[str] = json_dct.get('componentRelationType')
            if component_relation_type_name is not None and len(component_relation_type_name) > 0:
                component_relation_type = ComponentRelationType[component_relation_type_name]
            related_data_type_name: str = json_dct.get('relatedDataTypeName')
            related_extension_type_name: Optional[str] = json_dct.get('relatedExtensionTypeName')
            show_key_fields_only: bool = json_dct.get('showKeyFieldsOnly')
            hide_toolbar: bool = json_dct.get('hideToolbar')
            ret = RelatedRecordLayoutComponent(component_name, display_name,
                                               component_relation_type=component_relation_type,
                                               related_data_type_name=related_data_type_name,
                                               related_extension_type_name=related_extension_type_name,
                                               show_key_fields_only=show_key_fields_only,
                                               hide_toolbar=hide_toolbar)
        elif component_type == DataTypeLayoutComponentTypes.SEARCH_COMPONENT:
            custom_report_name: str = json_dct.get('customReportName')
            hide_toolbar: bool = json_dct.get('hideToolbar')
            query_restriction: Optional[ComponentRelationType] = None
            query_restriction_name: Optional[str] = json_dct.get('queryRestriction')
            if query_restriction_name is not None and len(query_restriction_name) > 0:
                query_restriction = ComponentRelationType[query_restriction_name]
            ret = SearchLayoutComponent(component_name, display_name,
                                        custom_report_name=custom_report_name, hide_toolbar=hide_toolbar,
                                        query_restriction=query_restriction)
        elif component_type == DataTypeLayoutComponentTypes.RELATED_NOTEBOOK_EXPERIMENTS:
            related_types_to_aggregate: Optional[List[str]] = json_dct.get('relatedTypeToAggregateSet')
            ret = RelatedNotebookComponent(component_name, display_name,
                                           related_types_to_aggregate=related_types_to_aggregate)
        elif component_type == DataTypeLayoutComponentTypes.RECORD_IMAGE_COMPONENT:
            preview_display_type: PreviewDisplayType = PreviewDisplayType[json_dct.get('previewDisplayType')]
            ret = RecordImageComponent(component_name, display_name,
                                       preview_display_type)
        elif component_type == DataTypeLayoutComponentTypes.RELATED_SIDE_LINK_COMPONENT:
            related_side_link_field_name: str = json_dct.get('relatedSideLinkFieldName')
            related_data_type_name: str = json_dct.get('relatedDataTypeName')
            related_extension_type_name: Optional[str] = json_dct.get('relatedExtensionTypeName')
            show_key_fields_only: bool = json_dct.get('showKeyFieldsOnly')
            hide_toolbar: bool = json_dct.get('hideToolbar')
            ret = RelatedSideLinkLayoutComponent(component_name, display_name,
                                                 related_side_link_field_name,
                                                 related_data_type_name=related_data_type_name,
                                                 related_extension_type_name=related_extension_type_name,
                                                 show_key_fields_only=show_key_fields_only,
                                                 hide_toolbar=hide_toolbar)
        else:
            raise NotImplemented("Unexpected component type: " + component_type.name)
        ret.set_optional_fields_from_json(json_dct)
        return ret
