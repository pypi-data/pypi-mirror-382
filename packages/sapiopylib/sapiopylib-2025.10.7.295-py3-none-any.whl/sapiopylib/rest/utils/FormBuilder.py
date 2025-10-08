from typing import List

from sapiopylib.rest.pojo.datatype.DataTypeComponent import AbstractDataTypeComponent, FieldDefinitionPosition, \
    DataFormComponent
from sapiopylib.rest.pojo.datatype.DataTypeLayout import DataTypeOuterTabDefinition, DataTypeLayout
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, VeloxEnumFieldDefinition
from sapiopylib.rest.pojo.datatype.TemporaryDataType import TemporaryDataType


class _FieldDefPosPair:
    field_def: AbstractVeloxFieldDefinition
    field_pos: FieldDefinitionPosition

    def __init__(self, field_def: AbstractVeloxFieldDefinition, field_pos: FieldDefinitionPosition):
        self.field_pos = field_pos
        self.field_def = field_def


class FormBuilder:
    """
    This is a custom form builder class, that allows any form to be built based on the specified parameters.
    """
    _temp_data_type: TemporaryDataType
    data_form_list: List[AbstractDataTypeComponent]
    tabs: List[DataTypeOuterTabDefinition]
    field_list: List[_FieldDefPosPair]
    tab_counter: int
    form_counter: int
    field_form_order: int

    @property
    def data_type_name(self) -> str:
        return self.get_data_type_name()

    def get_data_type_name(self) -> str:
        """
        Get the data type name of this form.
        """
        return self._temp_data_type.data_type_name

    def __init__(self, data_type_name='UNDEFINED', display_name='UNDEFINED', plural_display_name='UNDEFINED'):
        self._temp_data_type = TemporaryDataType(data_type_name, display_name, plural_display_name)
        self.data_form_list = list()
        self.tabs = list()
        self.field_list = list()
        self.tab_counter = 0
        self.form_counter = 0
        self.field_form_order = 0

    def _add_field_definitions(self, field_def_list: List[_FieldDefPosPair],
                               form_display_name: str, form_col: int, form_col_span: int) -> DataFormComponent:
        form_name: str = "Form_" + str(self.form_counter)
        form: DataFormComponent = DataFormComponent(form_name, form_display_name)
        self.data_form_list.append(form)

        form.hide_heading = True
        form.collapsed = False
        form.column = form_col
        form.column_span = form_col_span
        form.order = self.form_counter
        self.form_counter += 1
        form.height = 10

        for field_def_pos in field_def_list:
            self._temp_data_type.set_field_definition(field_def_pos.field_def)
            pos: FieldDefinitionPosition = field_def_pos.field_pos
            # It is possible that field name has changed while it is building the form.
            pos.data_field_name = field_def_pos.field_def.get_data_field_name()
            pos.form_name = form_name
            if pos.form_column + pos.form_column_span > form_col_span:
                pos.form_column = 0
                pos.form_column_span = form_col_span
            form.set_field_definition_position(pos)
            if isinstance(field_def_pos.field_def, VeloxEnumFieldDefinition):
                enum_field: VeloxEnumFieldDefinition = field_def_pos.field_def
                if enum_field._default_value is None and enum_field.values is not None and \
                        len(enum_field.values) > 0:
                    enum_field._default_value = 0
        return form

    def add_field(self, field_def: AbstractVeloxFieldDefinition,
                  column: int = 0, column_span: int = 4) -> FieldDefinitionPosition:
        """
        Add a new field definition to this form builder.
        If a form has not been created, it will be created automatically.
        :param field_def: The field definition to be added.
        :param column: The column starting index within the form component.
        :param column_span: The column span within the form component.
        :return: The new field definition position.
        """
        pos: FieldDefinitionPosition = FieldDefinitionPosition(field_def.get_data_field_name(),
                                                               form_column=column, form_column_span=column_span,
                                                               order=self.field_form_order)
        self.field_form_order += 1
        def_pos: _FieldDefPosPair = _FieldDefPosPair(field_def, pos)
        self.field_list.append(def_pos)
        self._temp_data_type.set_field_definition(field_def)
        return pos

    def complete_form(self, form_display_name: str, form_column: int = 0, form_column_span: int = 4) \
            -> DataFormComponent:
        """
        Complete the form in preparation to either begin working on the next form or to generate the
        final result of the TemporaryDataType
        :param form_display_name: Display name that the form should have.
        :param form_column: The starting column of the form in the layout.
        :param form_column_span: The width of the forum in layout positions.
        """
        ret: DataFormComponent = self._add_field_definitions(self.field_list, form_display_name,
                                                             form_column, form_column_span)
        self.field_list.clear()
        self.field_form_order = 0
        return ret

    def complete_tab(self, tab_name: str) -> DataTypeOuterTabDefinition:
        """
        Complete the tab in preparation to begin adding components for the next tab.
        Note: All forms that are expected to be on this tab must be completed as well.
        :param tab_name: The name of the tab t obe completed.
        """
        tab_def: DataTypeOuterTabDefinition = DataTypeOuterTabDefinition("Tab_" + str(self.tab_counter), tab_name,
                                                                         tab_order=self.tab_counter)
        self.tab_counter += 1
        tab_def.set_layout_component_list(self.data_form_list)
        self.data_form_list.clear()
        self.tabs.append(tab_def)
        return tab_def

    def get_temporary_data_type(self) -> TemporaryDataType:
        """
        Return the final data field definitions.
        """
        if len(self.data_form_list) == 0:
            self.complete_form("Details")
        if len(self.tabs) == 0:
            self.complete_tab("Details")

        layout: DataTypeLayout = DataTypeLayout("Default", "Default", "Auto-Generated by FormBuilder")
        layout.set_data_type_tab_definition_list(self.tabs)
        layout.data_type_name = self.get_data_type_name()

        self._temp_data_type.data_type_layout = layout
        return self._temp_data_type
