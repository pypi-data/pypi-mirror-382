from __future__ import annotations
from functools import total_ordering
from typing import Dict, Any, List, Optional

from sapiopylib.rest.pojo.datatype.DataTypeComponent import AbstractDataTypeComponent, DataTypeTabComponent, \
    DataTypeComponentParser


@total_ordering
class DataTypeOuterTabDefinition:
    """
    This represents the outer tab of a data type layout.

    tab_name: The tab name of this outer tab for the SYSTEM. Must be unique in data type.
    tab_display_name: Display name of the tab that shows up in tab browser.
    tab_order: The order of this tab among outer tabs of this data type.
    """
    _layout_component_map: Dict[str, AbstractDataTypeComponent]
    tab_name: str
    tab_display_name: str
    tab_order: Optional[int]

    def to_pojo(self) -> Dict[str, Any]:
        layout_component_pojo_map: Dict[str, Dict[str, Any]] = dict()
        for key, value in self._layout_component_map.items():
            layout_component_pojo_map[key] = value.to_pojo()
        return {
            'tabName': self.tab_name,
            'tabDisplayName': self.tab_display_name,
            'tabOrder': self.tab_order,
            'layoutComponentMap': layout_component_pojo_map
        }

    def set_layout_component(self, layout_component: AbstractDataTypeComponent) -> None:
        """
        Set a layout component on the tab definition.  This will either add a new component to the current list
        or replace an existing component that matches the given component.
        Note: The original data will be changed to indicate it is part of this tab.
        :param layout_component: The layout component to be set onto this tab.
        """
        layout_component.parent_tab_name = self.tab_name
        if layout_component.order is None:
            layout_component.order = len(self._layout_component_map)
        self._layout_component_map[layout_component.component_name.upper()] = layout_component

    def set_layout_component_list(self, layout_component_list: List[AbstractDataTypeComponent]) -> None:
        """
        Set a list of data type layout components on this tab definition.  This will replace the current list of
        components with the new list.
        Note: The original data will be changed to indicate it is part of this tab.
        :param layout_component_list: The layout component list to replace existing components in this tab.
        """
        self._layout_component_map.clear()
        for component in layout_component_list:
            self.set_layout_component(component)

    def get_layout_component_list(self) -> List[AbstractDataTypeComponent]:
        """
        This will get the components set on this layout.
        This will not return components that are contained within (inner) tab components.
        """
        ret: List[AbstractDataTypeComponent] = list(self._layout_component_map.values())
        ret.sort()
        return ret

    def get_full_layout_component_list(self) -> List[AbstractDataTypeComponent]:
        """
        This will get all the components set on this layout including those that are nested inside tab components.
        """
        ret: List[AbstractDataTypeComponent] = list()
        for component in self._layout_component_map.values():
            ret.append(component)
            if isinstance(component, DataTypeTabComponent):
                ret.extend(component.get_component_list())
        return ret

    def find_component(self, component_name: str):
        """
        Find a component in the layout with the given component name.
        This will check both components on the tab and those nested inside tab components
        :param component_name: The component to search for.
        :return: None if not found, otherwise, the component object.
        """
        ret: Optional[AbstractDataTypeComponent] = self._layout_component_map.get(component_name.upper())
        if ret is not None:
            return ret
        for component in self.get_layout_component_list():
            if isinstance(component, DataTypeTabComponent):
                ret = component.find_component(component_name)
                if ret is not None:
                    return ret
        return None

    def __init__(self, tab_name: str, tab_display_name: str,
                 tab_order: Optional[int] = None,
                 layout_component_map: Optional[Dict[str, AbstractDataTypeComponent]] = None):
        self.tab_name = tab_name
        self.tab_display_name = tab_display_name
        self.tab_order = tab_order
        if layout_component_map is None:
            layout_component_map = dict()
        self._layout_component_map = layout_component_map

    def __hash__(self):
        return hash((self.tab_order, self.tab_display_name, self.tab_name))

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, DataTypeOuterTabDefinition):
            return False
        return (self.tab_order, self.tab_display_name, self.tab_name) == \
               (other.tab_order, other.tab_display_name, other.tab_name)

    def __le__(self, other):
        if other is None:
            return False
        if not isinstance(other, DataTypeOuterTabDefinition):
            return False
        if self.tab_order != other.tab_order:
            return self.tab_order < other.tab_order
        if self.tab_display_name != other.tab_display_name:
            return self.tab_display_name < other.tab_display_name
        return self.tab_name < other.tab_name

    def __str__(self):
        return self.tab_display_name


def _parse_outer_tab_definition(json_dct: Dict[str, Any]) -> DataTypeOuterTabDefinition:
    layout_component_pojo_map: Dict[str, Dict[str, Any]] = json_dct.get('layoutComponentMap')
    layout_component_map: Dict[str, AbstractDataTypeComponent] = dict()
    for key, pojo in layout_component_pojo_map.items():
        layout_component_map[key] = DataTypeComponentParser.parse_data_type_component(pojo)
    tab_name: str = json_dct.get('tabName')
    tab_display_name: str = json_dct.get('tabDisplayName')
    tab_order: Optional[int] = json_dct.get('tabOrder')
    return DataTypeOuterTabDefinition(tab_name=tab_name, tab_display_name=tab_display_name,
                                      tab_order=tab_order, layout_component_map=layout_component_map)

class TableLayout:
    """
    A layout that defines how a table of the associated type will be displayed.
    Attributes:
        cell_size: The size of the cell in the table grid presented to user.
        record_image_width: The width of the image in the record table grid, if the record's data type allows data record image.
        table_column_definition_list: The list of columns that will be displayed in the table. If this is empty, the table column will be using the order from the form component list in their natural order (by tab order, form component order, field order within form component.).
    """
    cell_size: Optional[int]
    record_image_width: Optional[int]
    table_column_definition_list: List[Any]

    def __init__(self, cell_size: Optional[int] = None, record_image_width: Optional[int] = None,
                 table_column_definition_list: Optional[List[Any]] = None):
        self.cell_size = cell_size
        self.record_image_width = record_image_width
        if table_column_definition_list is None:
            table_column_definition_list = list()
        self.table_column_definition_list = table_column_definition_list

    def to_pojo(self) -> Dict[str, Any]:
        return {
            'cellSize': self.cell_size,
            'recordImageWidth': self.record_image_width,
            'tableColumnDefinitionList': self.table_column_definition_list
        }

    @staticmethod
    def from_json(json_dct: Dict[str, Any]) -> TableLayout:
        return TableLayout(
            cell_size=json_dct.get('cellSize'),
            record_image_width=json_dct.get('recordImageWidth'),
            table_column_definition_list=json_dct.get('tableColumnDefinitionList')
        )

class DataTypeLayout:
    """
    Describes a single data type layout.
    """
    layout_name: str
    display_name: str
    description: Optional[str]
    number_of_columns: int
    default_layout: bool
    fill_view: bool
    data_type_name: Optional[str]
    _data_type_tab_def_map: Dict[str, DataTypeOuterTabDefinition]
    link_panel_hidden: bool
    hidden_data_type_names: List[str]
    always_shown_data_type_names: List[str]
    hide_key_fields: bool
    table_layout: Optional[TableLayout]

    def __hash__(self):
        return hash((self.data_type_name, self.layout_name))

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, DataTypeLayout):
            return False
        return (self.data_type_name, self.layout_name) == (other.data_type_name, other.layout_name)

    def __str__(self):
        return self.display_name

    def to_pojo(self) -> Dict[str, Any]:
        data_type_pojo_map: Dict[str, Dict[str, Any]] = dict()
        for key, value in self._data_type_tab_def_map.items():
            data_type_pojo_map[key] = value.to_pojo()
        return {
            'layoutName': self.layout_name,
            'displayName': self.display_name,
            'description': self.description,
            'numberOfColumns': self.number_of_columns,
            'defaultLayout': self.default_layout,
            'fillView': self.fill_view,
            'dataTypeName': self.data_type_name,
            'dataTypeTabDefinitionMap': data_type_pojo_map,
            'linkPanelHidden': self.link_panel_hidden,
            'hiddenDataTypeNameSet': self.hidden_data_type_names,
            'alwaysShownDataTypeNameSet': self.always_shown_data_type_names,
            'hideKeyFields': self.hide_key_fields,
            'tableLayout': self.table_layout.to_pojo() if self.table_layout is not None else None
        }

    def set_data_type_tab_definition(self, tab_def: DataTypeOuterTabDefinition) -> None:
        """
        Add or replace the tab at this layout for the tab's name (ignore casing differences)
        :param tab_def: The outer tab to be set on this data type layout.
        """
        if tab_def.tab_order is None:
            tab_def.tab_order = len(self._data_type_tab_def_map)
        self._data_type_tab_def_map[tab_def.tab_name.upper()] = tab_def

    def remove_data_type_tab_definition(self, tab_name: str) -> Optional[DataTypeOuterTabDefinition]:
        """
        Remove the DataTypeTabDefinition that matches the given tab name.
        This method then returns the removed tab definition object.
        :param tab_name: The tab to be removed.
        :return: None if nothing was removed. Otherwise, return the tab that was removed from this layout.
        """
        if self._data_type_tab_def_map.get(tab_name.upper()) is not None:
            ret = self._data_type_tab_def_map.get(tab_name.upper())
            del self._data_type_tab_def_map[tab_name.upper()]
            return ret
        return None

    def set_data_type_tab_definition_list(self, tab_def_list: List[DataTypeOuterTabDefinition]) -> None:
        """
        Set the list of DataTypeTabDefinitions on this layout.  This will replace the existing list of tabs.
        :param tab_def_list: The new list of tabs to be replacing all existing tabs on this data type layout.
        """
        self._data_type_tab_def_map.clear()
        for tab_def in tab_def_list:
            self.set_data_type_tab_definition(tab_def)

    def get_data_type_tab_definition_list(self) -> List[DataTypeOuterTabDefinition]:
        """
        Get the list of DataTypeTabDefinitions that are on this layout.
        """
        ret = list(self._data_type_tab_def_map.values())
        ret.sort()
        return ret

    def get_data_type_tab_definition(self, tab_name: str) -> Optional[DataTypeOuterTabDefinition]:
        """
        Get the outer tab object in this layout by a tab name.
        Return None if this tab does not exist in the layout.
        Note: does not search inner tabs.
        """
        return self._data_type_tab_def_map.get(tab_name.upper())

    def get_data_type_layout_component(self, component_name: str):
        """
        Get a specific component within this layout. It can be of any depth.
        :param component_name: The component name to search for.
        :return: None if not found, otherwise, the component object.
        """
        for tab in self.get_data_type_tab_definition_list():
            component = tab.find_component(component_name)
            if component is not None:
                return component
        return None

    def __init__(self, layout_name: str, display_name: str, description: Optional[str] = None,
                 number_of_columns: int = 4, default_layout: bool = False, fill_view: bool = True,
                 data_type_name: Optional[str] = None,
                 data_type_tab_def_map: Optional[Dict[str, DataTypeOuterTabDefinition]] = None,
                 link_panel_hidden: bool = False, hidden_data_type_names: Optional[List[str]] = None,
                 always_shown_data_type_names: Optional[List[str]] = None, hide_key_fields: bool = False,
                 table_layout: Optional[TableLayout] = None):
        self.layout_name = layout_name
        self.display_name = display_name
        self.description = description
        self.number_of_columns = number_of_columns
        self.default_layout = default_layout
        self.fill_view = fill_view
        self.data_type_name = data_type_name
        if data_type_tab_def_map is None:
            data_type_tab_def_map = dict()
        self._data_type_tab_def_map = data_type_tab_def_map
        self.link_panel_hidden = link_panel_hidden
        if hidden_data_type_names is None:
            hidden_data_type_names = list()
        self.hidden_data_type_names = hidden_data_type_names
        if always_shown_data_type_names is None:
            always_shown_data_type_names = list()
        self.always_shown_data_type_names = always_shown_data_type_names
        self.hide_key_fields = hide_key_fields
        self.table_layout = table_layout


class DataTypeLayoutParser:
    @staticmethod
    def parse_outer_tab_definition(json_dct: Dict[str, Any]) -> DataTypeOuterTabDefinition:
        return _parse_outer_tab_definition(json_dct)

    @staticmethod
    def parse_layout(json_dct: Dict[str, Any]) -> DataTypeLayout:
        layout_name: str = json_dct.get('layoutName')
        display_name: str = json_dct.get('displayName')
        description: Optional[str] = json_dct.get('description')
        number_of_columns: int = json_dct.get('numberOfColumns')
        default_layout: bool = json_dct.get('defaultLayout')
        fill_view: bool = json_dct.get('fillView')
        data_type_name: Optional[str] = json_dct.get('dataTypeName')

        data_type_tab_def_map: Dict[str, DataTypeOuterTabDefinition] = dict()
        data_type_pojo_map: Dict[str, Dict[str, Any]] = json_dct.get('dataTypeTabDefinitionMap')
        for key, pojo in data_type_pojo_map.items():
            data_type_tab_def_map[key] = DataTypeLayoutParser.parse_outer_tab_definition(pojo)

        link_panel_hidden: bool = json_dct.get('linkPanelHidden')
        hidden_data_type_names: List[str] = json_dct.get('hiddenDataTypeNameSet')
        always_shown_data_type_names: List[str] = json_dct.get('alwaysShownDataTypeNameSet')
        hide_key_fields: bool = json_dct.get('hideKeyFields')
        table_layout: TableLayout = TableLayout.from_json(json_dct.get('tableLayout')) if json_dct.get('tableLayout') is not None else None

        return DataTypeLayout(layout_name, display_name,
                              description=description, number_of_columns=number_of_columns,
                              default_layout=default_layout, fill_view=fill_view,
                              data_type_name=data_type_name, data_type_tab_def_map=data_type_tab_def_map,
                              link_panel_hidden=link_panel_hidden, hidden_data_type_names=hidden_data_type_names,
                              always_shown_data_type_names=always_shown_data_type_names,
                              hide_key_fields=hide_key_fields, table_layout=table_layout)
