import warnings
from typing import Any

from sapiopylib.rest.pojo.TableColumn import TableColumn
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry, EntryAttachment
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnEntryType, ExperimentEntryStatus


# CR-53182: Create entry creation criteria classes for each entry type.
class AbstractElnEntryCriteria:
    """
    Criteria to specify the creation of a new ELN entry.
    """
    entry_type: ElnEntryType
    """The type of the entry. Includes Attachment, Dashboard, Form, Plugin, Table, Temp Data, and Text."""
    entry_name: str | None
    """The name of the entry."""
    data_type_name: str | None
    """The data type name of the entry. """
    order: int | None
    """The order of the entry in the experiment. Higher values result in the entry being further down in the
    experiment. Note: For the first tab, the first entry must be the title experiment entry."""
    is_shown_in_template: bool | None
    """Whether the entry will appear in the template if the experiment this entry is in is saved to a new template."""
    notebook_experiment_tab_id: int | None
    """The ID of the notebook experiment tab that the entry is within."""
    column_order: int | None
    """The column order of an entry. Higher values result in the entry being further to the right in the experiment."""
    column_span: int | None
    """The number of columns that the entry takes up. Lower values result in thinner entries. The maximum number of
    columns in an experiment tab is defined by the experiment tab itself, but is typically four."""
    is_removable: bool | None
    """Whether the entry can be removed by users."""
    is_renamable: bool | None
    """Whether the entry can be renamed by users."""
    is_static_view: bool | None
    """Whether the entry's attachment is static. For attachment entries only. Static attachment entries will store
    their attachment data in the template."""
    related_entry_set: list[int] | None
    """The IDs of the entries this entry is implicitly dependent on. If any of the entries are deleted then this entry
    is also deleted."""
    dependency_set: list[int] | None
    """The IDs of the entries this entry is dependent on. Requires the entries to be completed before this entry will
    be enabled."""
    requires_grabber_plugin: bool
    """Whether to run a grabber plugin when this entry is initialized."""
    entry_singleton_id: str | None
    """When this field is present (i.e. not null or blank) it will enforce that only one entry with this singleton
    value is present in the experiment. If you attempt to create an entry with the singletonId of an entry already
    present in the experiment it will return the existing entry instead of creating a new one. If an entry isn't
    present in the Notebook Experiment with a matching singletonId it will create a new entry like normal."""
    is_hidden: bool | None
    """Whether the user is able to visibly see this entry within the experiment."""
    entry_height: int | None
    """The height of this entry in pixels. Setting the height to 0 will cause the entry to auto-size to its contents."""
    description: str | None
    """The description of the entry."""
    is_initialization_required: bool | None
    """Whether the user must manually initialize this entry by clicking on it."""
    collapse_entry: bool | None
    """Whether the entry should be collapsed by default."""
    entry_status: ExperimentEntryStatus | None
    """The current status of the entry."""
    template_item_fulfilled_timestamp: int | None
    """The time in milliseconds since the epoch that this entry became initialized."""
    entry_options: dict[str, str] | None
    """The entry options of the entry."""

    def __init__(self, entry_type: ElnEntryType, entry_name: str, data_type_name: str, order: int):
        """
        INTERNAL ONLY. Use a constructor from a subclass!
        """
        self.entry_type = entry_type
        self.entry_name = entry_name
        self.data_type_name = data_type_name
        self.order = order
        self.is_shown_in_template = None
        self.notebook_experiment_tab_id = None
        self.column_order = None
        self.column_span = None
        self.is_removable = None
        self.is_renamable = None
        self.is_static_view = None
        self.related_entry_set = None
        self.dependency_set = None
        self.requires_grabber_plugin = False
        self.entry_singleton_id = None
        self.is_hidden = None
        self.entry_height = None
        self.description = None
        self.is_initialization_required = None
        self.collapse_entry = None
        self.entry_status = None
        self.template_item_fulfilled_timestamp = None
        self.entry_options = None

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            'entryType': self.entry_type.name,
            'dataTypeName': self.data_type_name,
            'order': self.order,
            'enbEntryName': self.entry_name,
            'isShownInTemplate': self.is_shown_in_template,
            'notebookExperimentTabId': self.notebook_experiment_tab_id,
            'columnOrder': self.column_order,
            'columnSpan': self.column_span,
            'isRemovable': self.is_removable,
            'isRenamable': self.is_renamable,
            'isStaticView': self.is_static_view,
            'relatedEntryIdSet': self.related_entry_set,
            'dependencySet': self.dependency_set,
            'requiresGrabberPlugin': self.requires_grabber_plugin,
            'entrySingletonId': self.entry_singleton_id,
            "hidden": self.is_hidden,
            "entryHeight": self.entry_height,
            "description": self.description,
            "initializationRequired": self.is_initialization_required,
            "collapsed": self.collapse_entry,
            "entryStatus": self.entry_status,
            "templateItemFulfilledTimestamp": self.template_item_fulfilled_timestamp,
            "entryOptionMap": self.entry_options
        }
        return ret


class ElnAttachmentEntryCriteria(AbstractElnEntryCriteria):
    """
    Criteria that specifies the creation of a new ELN Attachment entry.
    """
    entry_attachment_list: list[EntryAttachment] | None
    """A list of metadata for the sources of the attachments in this entry."""

    def __init__(self, entry_name: str, data_type_name: str, order: int):
        """
        :param entry_name: The name of the entry.
        :param data_type_name: Data type name of the experiment entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        """
        super().__init__(ElnEntryType.Attachment, entry_name, data_type_name, order)
        self.entry_attachment_list = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.entry_attachment_list:
            ret['entryAttachmentList'] = [x.to_json() for x in self.entry_attachment_list]
        return ret


class ElnDashboardEntryCriteria(AbstractElnEntryCriteria):
    """
    Criteria that specifies the creation of a new ELN Dashboard entry.
    """
    source_entry_id: int | None
    """The ID of the entry that contains the source data for this entry's dashboard(s)."""
    dashboard_guid_list: list[str] | None
    """The GUIDs of the dashboards to display in this entry."""

    def __init__(self, entry_name: str, data_type_name: str, order: int):
        """
        :param entry_name: The name of the entry.
        :param data_type_name: Data type name of the experiment entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        """
        super().__init__(ElnEntryType.Dashboard, entry_name, data_type_name, order)
        self.source_entry_id = None
        self.dashboard_guid_list = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.source_entry_id is not None:
            ret['sourceEntryId'] = self.source_entry_id
        if self.dashboard_guid_list:
            ret['dashboardGuidList'] = self.dashboard_guid_list
        return ret


class ElnFormEntryCriteria(AbstractElnEntryCriteria):
    """
    Criteria that specifies the creation of a new ELN Form entry.
    """
    form_name_list: list[str] | None
    """The names of the components in the chosen data type layout to display in this form. For global data type entries
    only."""
    data_type_layout_name: str | None
    """The name of the data type layout to be displayed in this form. The layout must be for the data type for this
    entry. For global data type entries only."""
    record_id: int | None
    """The record ID of the data record to populate the form entry with. For global data type entries only."""
    extension_type_list: list[str] | None
    """The names of the extension data types to display fields from within the form. For global data type entries
    only."""
    data_field_name_list: list[str] | None
    """A list of data field names for the fields to be displayed in the form. For global data type entries only."""

    is_field_addable: bool | None
    """Whether new fields can be added to the form by users. For ELN data type entries only."""
    is_existing_field_removable: bool | None
    """Whether existing fields on the form can be removed by users. For ELN data type entries only."""

    field_set_id_list: list[int] | None
    """The IDs of the predefined field sets to display in this form. For ELN data type entries only."""
    field_definition_list: list[AbstractVeloxFieldDefinition] | None
    """New fields to be created for this entry. These will appear in addition to any fields that come from the field
    set ID list. For ELN data type entries only."""
    field_map: dict[str, Any] | None
    """If provided, a new record will be created using this field map to populate the entry. The field names must be
    present in either the field sets specified by the field set ID list or be in the field definitions list.
    For ELN data type entries only."""

    def __init__(self, entry_name: str, data_type_name: str, order: int):
        """
        :param entry_name: The name of the entry.
        :param data_type_name: Data type name of the experiment entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        """
        super().__init__(ElnEntryType.Form, entry_name, data_type_name, order)
        self.form_name_list = None
        self.data_type_layout_name = None
        self.record_id = None
        self.extension_type_list = None
        self.data_field_name_list = None
        self.is_field_addable = None
        self.is_existing_field_removable = None
        self.field_set_id_list = None
        self.field_definition_list = None
        self.field_map = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.form_name_list:
            ret['formNameList'] = self.form_name_list
        if self.data_type_layout_name:
            ret['dataTypeLayoutName'] = self.data_type_layout_name
        if self.record_id is not None:
            ret['recordId'] = self.record_id
        if self.extension_type_list:
            ret['extensionTypeList'] = self.extension_type_list
        if self.data_field_name_list:
            ret['dataFieldNameList'] = self.data_field_name_list
        if self.is_field_addable is not None:
            ret['isFieldAddable'] = self.is_field_addable
        if self.is_existing_field_removable is not None:
            ret['isExistingFieldRemovable'] = self.is_existing_field_removable
        if self.field_set_id_list:
            ret['fieldSetIdList'] = self.field_set_id_list
        if self.field_map:
            ret['fieldMap'] = self.field_map
        if self.field_definition_list:
            ret['fieldDefinitionList'] = [x.to_json() for x in self.field_definition_list]
        return ret


class ElnPluginEntryCriteria(AbstractElnEntryCriteria):
    """
    Criteria that specifies the creation of a new ELN Plugin entry.
    """
    csp_plugin_name: str | None
    """The client side plugin name to render this entry with."""
    using_template_data: bool | None
    """Whether this entry will use the data from the template."""
    provides_template_data: bool | None
    """Whether this entry can provide data to copy into a new template."""

    def __init__(self, entry_name: str, data_type_name: str, order: int):
        """
        :param entry_name: The name of the entry.
        :param data_type_name: Data type name of the experiment entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        """
        super().__init__(ElnEntryType.Plugin, entry_name, data_type_name, order)
        self.csp_plugin_name = None
        self.using_template_data = None
        self.provides_template_data = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.csp_plugin_name:
            ret['pluginName'] = self.csp_plugin_name
        if self.using_template_data is not None:
            ret['usingTemplateData'] = self.using_template_data
        if self.provides_template_data is not None:
            ret['providesTemplateData'] = self.provides_template_data
        return ret


class ElnTableEntryCriteria(AbstractElnEntryCriteria):
    """
    Criteria that specifies the creation of a new ELN Table entry.
    """
    data_type_layout_name: str | None
    """The name of the data type layout to display in this table. The layout must be for the data type for this
    entry. For global data type entries only."""
    extension_type_list: list[str] | None
    """The names of the extension data types to display fields from within the table. For global data type entries only."""
    table_column_list: list[TableColumn] | None
    """The columns to display in the table."""
    show_key_fields: bool | None
    """Whether the key fields of the data type should be shown in the entry."""

    is_field_addable: bool | None
    """Whether new fields can be added to the form by users. For ELN data type entries only."""
    is_existing_field_removable: bool | None
    """Whether existing fields on the form can be removed by users. For ELN data type entries only."""

    field_set_id_list: list[int] | None
    """The IDs of the predefined field sets to display in this table. For ELN data type entries only."""
    field_definition_list: list[AbstractVeloxFieldDefinition] | None
    """New fields to be created for this entry. These will appear in addition to any fields that come from the field
    set ID list. For ELN data type entries only."""
    field_map_list: list[dict[str, Any]] | None
    """If provided, new records will be created using these field maps to populate the entry. The field names must be
    present in either the field sets specified by the field set ID list or be in the field definitions list.
    For ELN data type entries only."""

    def __init__(self, entry_name: str, data_type_name: str, order: int):
        """
        :param entry_name: The name of the entry.
        :param data_type_name: Data type name of the experiment entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        """
        super().__init__(ElnEntryType.Table, entry_name, data_type_name, order)
        self.data_type_layout_name = None
        self.extension_type_list = None
        self.table_column_list = None
        self.show_key_fields = None
        self.is_field_addable = None
        self.is_existing_field_removable = None
        self.field_set_id_list = None
        self.field_definition_list = None
        self.field_map_list = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.data_type_layout_name:
            ret['dataTypeLayoutName'] = self.data_type_layout_name
        if self.extension_type_list:
            ret['extensionTypeList'] = self.extension_type_list
        if self.table_column_list:
            ret['tableColumnList'] = [x.to_json() for x in self.table_column_list]
        if self.show_key_fields is not None:
            ret['showKeyFields'] = self.show_key_fields
        if self.is_field_addable is not None:
            ret['isFieldAddable'] = self.is_field_addable
        if self.is_existing_field_removable is not None:
            ret['isExistingFieldRemovable'] = self.is_existing_field_removable
        if self.field_set_id_list:
            ret['fieldSetIdList'] = self.field_set_id_list
        if self.field_map_list:
            ret['fieldMapList'] = self.field_map_list
        if self.field_definition_list:
            ret['fieldDefinitionList'] = [x.to_json() for x in self.field_definition_list]
        return ret


class ElnTempDataEntryCriteria(AbstractElnEntryCriteria):
    """
    Criteria that specifies the creation of a new ELN Temp Data entry.
    """
    temp_data_plugin_path: str | None
    """The temp data plugin path to run to populate the entry."""

    def __init__(self, entry_name: str, data_type_name: str, order: int):
        """
        :param entry_name: The name of the entry.
        :param data_type_name: Data type name of the experiment entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        """
        super().__init__(ElnEntryType.TempData, entry_name, data_type_name, order)
        self.temp_data_plugin_path = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.temp_data_plugin_path:
            ret['pluginPath'] = self.temp_data_plugin_path
        return ret


class ElnTextEntryCriteria(AbstractElnEntryCriteria):
    """
    Criteria that specifies the creation of a new ELN Text entry.
    """

    def __init__(self, entry_name: str, data_type_name: str, order: int):
        """
        :param entry_name: The name of the entry.
        :param data_type_name: Data type name of the experiment entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        """
        super().__init__(ElnEntryType.Text, entry_name, data_type_name, order)


# CR-53182: Deprecate the old ElnEntryCriteria class in favor of the new entry-specific classes.
class ElnEntryCriteria(AbstractElnEntryCriteria):
    """
    Criteria to specify the creation of a new ELN entry.
    """
    # ELN data type form/table specific fields:
    enb_field_set_id: int | None
    field_map_list: list[dict[str, Any] | None]
    field_definition_list: list[AbstractVeloxFieldDefinition] | None

    # Plugin entry specific:
    csp_plugin_name: str | None
    using_template_data: bool | None
    provides_template_data: bool | None

    # Dashboard entry specific:
    source_entry_id: int | None

    # Attachment entry specific:
    attachment_data_base64: str | None
    attachment_file_name: str | None

    # Temp Data entry specific:
    temp_data_plugin_path: str | None

    def __init__(self,
                 entry_type: ElnEntryType,
                 entry_name: str | None,
                 data_type_name: str | None,
                 order: int,
                 is_shown_in_template: bool | None = None,
                 notebook_experiment_tab_id: int | None = None,
                 column_order: int | None = None,
                 column_span: int | None = None,
                 is_removable: bool | None = None,
                 is_renamable: bool | None = None,
                 is_static_view: bool | None = None,
                 enb_field_set_id: int | None = None,
                 related_entry_set: list[int] | None = None,
                 dependency_set: list[int] | None = None,
                 requires_grabber_plugin: bool = False,
                 entry_singleton_id: str | None = None,
                 field_map_list: list[dict[str, Any] | None] = None,
                 field_definition_list: list[AbstractVeloxFieldDefinition] | None = None,
                 csp_plugin_name: str | None = None,
                 using_template_data: bool | None = None,
                 provides_template_data: bool | None = None,
                 source_entry_id: int | None = None,
                 attachment_data_base64: str | None = None,
                 attachment_file_name: str | None = None,
                 temp_data_plugin_path: str | None = None):
        """
        :param entry_type: The type of the entry.
        :param entry_name: The name of the entry.
        :param data_type_name: Data type name of the experiment entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        :param is_shown_in_template: Whether the entry will appear in the template if the experiment this entry is in
            is saved to a new template.
        :param notebook_experiment_tab_id: The ID of the notebook experiment tab that the entry is within.
        :param column_order: The column order of an entry. Higher values result in the entry being further to the right
            in the experiment.
        :param column_span: The number of columns that the entry takes up. Lower values result in thinner entries.
            The maximum number of columns in an experiment is defined by the experiment itself, but is typically four.
        :param is_removable: Whether the entry can be removed by users.
        :param is_renamable: Whether the entry can be renamed by users.
        :param is_static_view: Whether the entry's attachment is static. For attachment entries only.
        :param enb_field_set_id: The IDs of the field sets in the entry. For ELN data type form and table entries only.
        :param related_entry_set: The IDs of the entries this entry is implicitly dependent on. If any of the entries
            are deleted then this entry is also deleted.
        :param dependency_set: The IDs of the entries this entry is dependent on. Requires the entries to be completed
            before this entry will be enabled.
        :param requires_grabber_plugin: Whether to run a grabber plugin when this entry is initialized.
        :param entry_singleton_id: When this field is present (i.e. not null or blank) it will enforce that only one
            entry with this singleton value is present in the experiment. If you attempt to create an entry with the
            singletonId of an entry already present in the experiment it will return the existing entry instead of
            creating a new one. If an entry isn't present in the Notebook Experiment with a matching singletonId it
            will create a new entry like normal.
        :param field_map_list: If provided, new records will be created using these field maps to populate the entry.
            The field names must be present in either the field sets specified by the field set ID list or be in the
            field definitions list. For ELN data type form and table entries only. If the entry type being created is a
            Form entry, then only the first field map will be used if multiple are provided.
        :param field_definition_list: New fields to be created for this entry. These will appear in addition to any
            fields that come from the field set ID list. For ELN data type form and table entries only.
        :param csp_plugin_name: The client side plugin name to render this entry with. For plugin entries only.
        :param using_template_data: Whether this entry will use the data from the template. For plugin entries only.
        :param provides_template_data: Whether this entry can provide data to copy into a new template. For plugin
            entries only.
        :param source_entry_id: The ID of the entry that contains the source data for this entry's dashboard(s).
            For dashboard entries only.
        :param attachment_data_base64: The base 64 attachment payload to directly inject into the entry. For attachment
            entries only.
        :param attachment_file_name: The file name of the attachment. For attachment entries only.
        :param temp_data_plugin_path: The temp data plugin path to run to populate the entry. For temp data
            entries only.
        """
        warnings.warn("Replaced with AbstractElnEntryCriteria and the type-specific classes.", PendingDeprecationWarning)
        super().__init__(entry_type, entry_name, data_type_name, order)
        self.is_shown_in_template = is_shown_in_template
        self.notebook_experiment_tab_id = notebook_experiment_tab_id
        self.column_order = column_order
        self.column_span = column_span
        self.is_removable = is_removable
        self.is_renamable = is_renamable
        self.is_static_view = is_static_view
        self.enb_field_set_id = enb_field_set_id
        self.related_entry_set = related_entry_set
        self.dependency_set = dependency_set
        self.requires_grabber_plugin = requires_grabber_plugin
        self.entry_singleton_id = entry_singleton_id
        self.field_map_list = field_map_list
        self.field_definition_list = field_definition_list
        self.csp_plugin_name = csp_plugin_name
        self.using_template_data = using_template_data
        self.provides_template_data = provides_template_data
        self.source_entry_id = source_entry_id
        self.attachment_data_base64 = attachment_data_base64
        self.attachment_file_name = attachment_file_name
        self.temp_data_plugin_path = temp_data_plugin_path

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = super().to_json()

        field_def_list_pojo_list: list[dict[str, Any]] | None = None
        if self.field_definition_list is not None:
            field_def_list_pojo_list = [x.to_json() for x in self.field_definition_list]
        ret.update({
            'entryType': self.entry_type.name,
            'dataTypeName': self.data_type_name,
            'order': self.order,
            'enbEntryName': self.entry_name,
            'isShownInTemplate': self.is_shown_in_template,
            'notebookExperimentTabId': self.notebook_experiment_tab_id,
            'columnOrder': self.column_order,
            'columnSpan': self.column_span,
            'isRemovable': self.is_removable,
            'isRenamable': self.is_renamable,
            'isStaticView': self.is_static_view,
            'enbFieldSetId': self.enb_field_set_id,
            'relatedEntryIdSet': self.related_entry_set,
            'dependencySet': self.dependency_set,
            'requiresGrabberPlugin': self.requires_grabber_plugin,
            'entrySingletonId': self.entry_singleton_id,
            'fieldMapList': self.field_map_list,
            'fieldDefinitionList': field_def_list_pojo_list,
            'pluginName': self.csp_plugin_name,
            'usingTemplateData': self.using_template_data,
            'providesTemplateData': self.provides_template_data,
            'sourceEntryId': self.source_entry_id,
            'attachmentData': self.attachment_data_base64,
            'attachmentFileName': self.attachment_file_name,
            'pluginPath': self.temp_data_plugin_path
        })
        return ret


class AbstractElnEntryUpdateCriteria:
    """
    Abstract criteria to specify supported update payload to an existing entry.

    This is an abstract class and serves as a base for the classes providing different
    types of entry updates. You should use a constructor from a subclass. Use ExperimentEntryCriteriaUtil
    to cleanly get an update criteria for any entry type.
    """
    entry_type: ElnEntryType
    """The type of the entry."""
    entry_name: str | None
    """The name of the entry."""
    related_entry_set: list[int] | None
    """The IDs of the entries this entry is implicitly dependent on. If any of the entries are deleted then this entry
    is also deleted."""
    dependency_set: list[int] | None
    """The IDs of the entries this entry is dependent on. Requires the entries to be completed before this entry will be
    enabled."""
    entry_status: ExperimentEntryStatus | None
    """The current status of the entry."""
    order: int | None
    """The order of the entry in the experiment. Higher values result in the entry being further down in the experiment.
    Note: For the first tab, the first entry must be the title experiment entry."""
    description: str | None
    """The description of the entry."""
    requires_grabber_plugin: bool | None
    """Whether to run a grabber plugin when this entry is initialized."""
    is_initialization_required: bool | None
    """Whether the user must manually initialize this entry by clicking on it."""
    notebook_experiment_tab_id: int | None
    """The ID of the notebook experiment tab that the entry is within."""
    entry_height: int | None
    """The height of this entry. Setting the height to 0 will cause the entry to auto-size to its contents."""
    column_order: int | None
    """The column order of an entry. Higher values result in the entry being further to the right in the experiment."""
    column_span: int | None
    """The number of columns that the entry takes up. Lower values result in thinner entries. The maximum number of
    columns in an experiment is defined by the experiment itself, but is typically four."""
    is_removable: bool | None
    """Whether the entry can be removed by users."""
    is_renamable: bool | None
    """Whether the entry can be renamed by users."""
    source_entry_id: int | None
    """The ID of the template entry that this entry is created from."""
    clear_source_entry_id: bool | None
    """Whether the source entry ID of the entry should be cleared."""
    is_hidden: bool | None
    """Whether the user is able to visibly see this entry within the experiment."""
    is_static_View: bool | None
    """Whether the entry's attachment is static. For attachment entries only."""
    is_shown_in_template: bool | None
    """Whether the entry will appear in the template if the experiment this entry is in is saved to a new template."""
    template_item_fulfilled_timestamp: int | None
    """The time in milliseconds since the epoch that this entry became initialized."""
    clear_template_item_fulfilled_timestamp: bool | None
    """Whether the timestamp for when the entry was initialized should be cleared."""
    entry_options_map: dict[str, str] | None
    """The entry options of the entry."""

    def __init__(self, entry_type: ElnEntryType):
        """
        INTERNAL ONLY. USE a constructor from a subclass!
        """
        self.entry_type = entry_type
        self.entry_name = None
        self.related_entry_set = None
        self.dependency_set = None
        self.entry_status = None
        self.order = None
        self.description = None
        self.requires_grabber_plugin = None
        self.is_initialization_required = None
        self.notebook_experiment_tab_id = None
        self.entry_height = None
        self.column_order = None
        self.column_span = None
        self.is_removable = None
        self.is_renamable = None
        self.source_entry_id = None
        self.clear_source_entry_id = None
        self.is_hidden = None
        self.is_static_View = None
        self.is_shown_in_template = None
        self.template_item_fulfilled_timestamp = None
        self.clear_template_item_fulfilled_timestamp = None
        self.entry_options_map = None

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            'entryType': self.entry_type.name,
        }
        if self.entry_name is not None:
            ret['experimentEntryName'] = self.entry_name
        if self.dependency_set is not None:
            ret['dependencySet'] = self.dependency_set
        if self.related_entry_set is not None:
            ret['relatedEntrySet'] = self.related_entry_set
        if self.entry_status is not None:
            ret['entryStatus'] = self.entry_status.name
        if self.order is not None:
            ret['order'] = self.order
        if self.description is not None:
            ret['description'] = self.description
        if self.requires_grabber_plugin is not None:
            ret['requiresGrabberPlugin'] = self.requires_grabber_plugin
        if self.is_initialization_required is not None:
            ret['isInitializationRequired'] = self.is_initialization_required
        if self.notebook_experiment_tab_id is not None:
            ret['notebookExperimentTabId'] = self.notebook_experiment_tab_id
        if self.entry_height is not None:
            ret['entryHeight'] = self.entry_height
        if self.column_order is not None:
            ret['columnOrder'] = self.column_order
        if self.column_span is not None:
            ret['columnSpan'] = self.column_span
        if self.is_removable is not None:
            ret['isRemovable'] = self.is_removable
        if self.is_renamable is not None:
            ret['isRenamable'] = self.is_renamable
        if self.source_entry_id is not None:
            ret['sourceEntryId'] = self.source_entry_id
        if self.clear_source_entry_id is not None:
            ret['clearSourceEntryId'] = self.clear_source_entry_id
        if self.is_hidden is not None:
            ret['isHidden'] = self.is_hidden
        if self.is_static_View is not None:
            ret['isStaticView'] = self.is_static_View
        if self.is_shown_in_template is not None:
            ret['isShownInTemplate'] = self.is_shown_in_template
        if self.template_item_fulfilled_timestamp is not None:
            ret['templateItemFulfilledTimestamp'] = self.template_item_fulfilled_timestamp
        if self.clear_template_item_fulfilled_timestamp is not None:
            ret['clearTemplateItemFulfilledTimestamp'] = self.clear_template_item_fulfilled_timestamp
        if self.entry_options_map is not None:
            ret['entryOptionMap'] = self.entry_options_map
        return ret


class ElnAttachmentEntryUpdateCriteria(AbstractElnEntryUpdateCriteria):
    """
    Update data payload for an attachment ELN entry.

    This class serves as a data holder for making attachment ELN entry updates.
    Create an instance of this class, set the attributes you want to update,
    and then use the instance to send the request.
    """
    attachment_name: str | None
    """(DEPRECATED: Make use of entry_attachment_list now.) The name of the attachment in this entry."""
    record_id: int | None
    """(DEPRECATED: Make use of entry_attachment_list now.) The record ID of the attachment data record in this
    entry."""
    entry_attachment_list: list[EntryAttachment] | None
    """A list of metadata for the sources of the attachments in this entry."""

    def __init__(self):
        super().__init__(ElnEntryType.Attachment)
        self.attachment_name = None
        self.record_id = None
        self.entry_attachment_list = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.attachment_name is not None:
            ret['attachmentName'] = self.attachment_name
        if self.record_id is not None:
            ret['recordId'] = self.record_id
        if self.entry_attachment_list:
            ret['entryAttachmentList'] = [x.to_json() for x in self.entry_attachment_list]
        return ret


class ElnDashboardEntryUpdateCriteria(AbstractElnEntryUpdateCriteria):
    """
    Dashboard Entry Update Request Payload Data.

    This class serves as a data holder for making dashboard entry updates. Create an instance
    of this class, set the attributes you want to update, and then use the instance
    to send the request.
    """
    dashboard_guid: str | None
    """(DEPRECATED: Make use of dashboard_guid_list now.) The GUID of the dashboard to display in this entry."""
    dashboard_guid_list: list[str] | None
    """The GUIDs of the dashboards to display in this entry."""
    data_source_entry_id: int | None
    """The ID of the entry that contains the source data for this entry's dashboard(s)."""

    def __init__(self):
        super().__init__(ElnEntryType.Dashboard)
        self.dashboard_guid = None
        self.dashboard_guid_list = None
        self.data_source_entry_id = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.dashboard_guid is not None:
            ret['dashboardGuid'] = self.dashboard_guid
        if self.dashboard_guid_list:
            ret['dashboardGuidList'] = self.dashboard_guid_list
        if self.data_source_entry_id is not None:
            ret['dataSourceEntryId'] = self.data_source_entry_id
        return ret


class ElnFormEntryUpdateCriteria(AbstractElnEntryUpdateCriteria):
    """
    Form Entry Update Request payload data.

    This class serves as a data holder for making form entry updates. Create an instance
    of this class, set the attributes you want to update, and then use the instance to
    send the request.
    """
    form_name_list: list[str] | None
    """The names of the components in the chosen data type layout to display in this form. For global data type
    entries only."""
    data_type_layout_name: str | None
    """The name of the data type layout to be displayed in this form. The layout must be for the data type for this
    entry. For global data type entries only."""
    record_id: int | None
    """The record ID of the data record to populate the form entry with. For global data type entries only."""
    field_set_id_list: list[int] | None
    """The IDs of the predefined field sets to display in this form. For ELN data type entries only."""
    extension_type_list: list[str] | None
    """The names of the extension data types to display fields from within the form. For global data type entries
    only."""
    data_field_name_list: list[str] | None
    """A list of data field names for the fields to be displayed in the form. For global data type entries only."""
    is_field_addable: bool | None
    """Whether new fields can be added to the form by users. For ELN data type entries only."""
    is_existing_field_removable: bool | None
    """Whether existing fields on the form can be removed by users. For ELN data type entries only."""

    def __init__(self):
        super().__init__(ElnEntryType.Form)
        self.form_name_list = None
        self.data_type_layout_name = None
        self.record_id = None
        self.field_set_id_list = None
        self.extension_type_list = None
        self.data_field_name_list = None
        self.is_field_addable = None
        self.is_existing_field_removable = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.form_name_list is not None:
            ret['formNameList'] = self.form_name_list
        if self.data_type_layout_name is not None:
            ret['dataTypeLayoutName'] = self.data_type_layout_name
        if self.record_id is not None:
            ret['recordId'] = self.record_id
        if self.field_set_id_list is not None:
            ret['fieldSetIdList'] = self.field_set_id_list
        if self.extension_type_list is not None:
            ret['extensionTypeList'] = self.extension_type_list
        if self.data_field_name_list is not None:
            ret['dataFieldNameList'] = self.data_field_name_list
        if self.is_field_addable is not None:
            ret['isFieldAddable'] = self.is_field_addable
        if self.is_existing_field_removable is not None:
            ret['isExistingFieldRemovable'] = self.is_existing_field_removable
        return ret


class ElnPluginEntryUpdateCriteria(AbstractElnEntryUpdateCriteria):
    """
    Plugin Entry Update Data Payload.

    This class serves as a data holder for making plugin entry updates.
    Create an instance of this class, set the attributes you want to update,
    and then use the instance to send the request.
    """
    plugin_name: str | None
    """The client side plugin name to render this entry with."""
    using_template_data: bool | None
    """Whether this entry will use the data from the template."""
    provides_template_data: bool | None
    """Whether this entry can provide data to copy into a new template."""

    def __init__(self):
        super().__init__(ElnEntryType.Plugin)
        self.plugin_name = None
        self.using_template_data = None
        self.provides_template_data = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.plugin_name is not None:
            ret['pluginName'] = self.plugin_name
        if self.using_template_data is not None:
            ret['usingTemplateData'] = self.using_template_data
        if self.provides_template_data is not None:
            ret['provides_template_data'] = self.provides_template_data
        return ret


class ElnTableEntryUpdateCriteria(AbstractElnEntryUpdateCriteria):
    """
    Table Entry Update Criteria Payload.

    This class serves as a data holder for making table entry updates. Create an instance
    of this class, set the attributes you want to update, and then use the instance to
    send the request.
    """
    data_type_layout_name: str | None
    """The name of the data type layout to display in this table. The layout must be for the data type for this
    entry. For global data type entries only."""
    field_set_id_list: list[int] | None
    """The IDs of the predefined field sets to display in this table. For ELN data type entries only."""
    extension_type_list: list[str] | None
    """The names of the extension data types to display fields from within the table. For global data type entries
    only."""
    table_column_list: list[TableColumn] | None
    """The columns to display in the table."""
    show_key_fields: bool | None
    """Whether the key fields of the data type should be shown in the entry."""
    is_field_addable: bool | None
    """Whether new fields can be added to the form by users. For ELN data type entries only."""
    is_existing_field_removable: bool | None
    """Whether existing fields on the form can be removed by users. For ELN data type entries only."""

    def __init__(self):
        super().__init__(ElnEntryType.Table)
        self.data_type_layout_name = None
        self.field_set_id_list = None
        self.extension_type_list = None
        self.table_column_list = None
        self.show_key_fields = None
        self.is_field_addable = None
        self.is_existing_field_removable = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.data_type_layout_name is not None:
            ret['dataTypeLayoutName'] = self.data_type_layout_name
        if self.field_set_id_list is not None:
            ret['fieldSetIdList'] = self.field_set_id_list
        if self.extension_type_list is not None:
            ret['extensionTypeList'] = self.extension_type_list
        if self.table_column_list is not None:
            ret['tableColumnList'] = [x.to_json() for x in self.table_column_list]
        if self.show_key_fields is not None:
            ret['showKeyFields'] = self.show_key_fields
        if self.is_field_addable is not None:
            ret['isFieldAddable'] = self.is_field_addable
        if self.is_existing_field_removable is not None:
            ret['isExistingFieldRemovable'] = self.is_existing_field_removable
        return ret


class ElnTempDataEntryUpdateCriteria(AbstractElnEntryUpdateCriteria):
    """
    Temporary Data Entry Update Data Payload.

    This class serves as a data holder for updating temporary data entry.
    Create an instance of this class, set the attributes you want to update,
    and then use the instance to send the request.
    """
    plugin_path: str | None
    """The temp data plugin path to run to populate the entry."""

    def __init__(self):
        super().__init__(ElnEntryType.TempData)
        self.plugin_path = None

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.plugin_path is not None:
            ret['pluginPath'] = self.plugin_path
        return ret


class ElnTextEntryUpdateCriteria(AbstractElnEntryUpdateCriteria):
    """
    Text Entry Update Data Payload
    Create this payload object and set the attributes you want to update before sending the request.
    """
    def __init__(self):
        super().__init__(ElnEntryType.Text)

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        return ret


class ExperimentEntryCriteriaUtil:
    """
    Common utilities for ELN Experiment Entry Criteria
    """
    @staticmethod
    def create_empty_criteria(entry: ExperimentEntry) -> AbstractElnEntryUpdateCriteria:
        """
        Create an empty ELN entry criteria object based on the entry passed in.

        :param entry: The experiment entry that you will be updating.
        :return: An entry update criteria matching the entry type of the input experiment entry.
        """
        entry_update_criteria: AbstractElnEntryUpdateCriteria
        if entry.entry_type == ElnEntryType.Attachment:
            entry_update_criteria = ElnAttachmentEntryUpdateCriteria()
        elif entry.entry_type == ElnEntryType.Dashboard:
            entry_update_criteria = ElnDashboardEntryUpdateCriteria()
        elif entry.entry_type == ElnEntryType.Form:
            entry_update_criteria = ElnFormEntryUpdateCriteria()
        elif entry.entry_type == ElnEntryType.Plugin:
            entry_update_criteria = ElnPluginEntryUpdateCriteria()
        elif entry.entry_type == ElnEntryType.Table:
            entry_update_criteria = ElnTableEntryUpdateCriteria()
        elif entry.entry_type == ElnEntryType.TempData:
            entry_update_criteria = ElnTempDataEntryUpdateCriteria()
        elif entry.entry_type == ElnEntryType.Text:
            entry_update_criteria = ElnTextEntryUpdateCriteria()
        else:
            raise ValueError("Unexpected entry type: " + entry.entry_type.name)
        return entry_update_criteria

    # CR-53182: Added method to support use of the entry type-specific classes.
    @staticmethod
    def get_entry_creation_criteria(entry_type: ElnEntryType, entry_name: str, data_type: str, order: int) \
            -> AbstractElnEntryCriteria:
        """
        Create an entry creation criteria object based on the entry type passed in.

        :param entry_type: The type of the entry.
        :param entry_name: The name of the entry.
        :param data_type: The data type name of the entry.
        :param order: The order of the entry in the experiment. Higher values result in the entry being further down
            in the experiment. Note: For the first tab, the first entry must be the title experiment entry.
        :return: An entry creation criteria matching the input entry type.
        """
        match entry_type:
            case ElnEntryType.Attachment:
                return ElnAttachmentEntryCriteria(entry_name, data_type, order)
            case ElnEntryType.Dashboard:
                return ElnDashboardEntryCriteria(entry_name, data_type, order)
            case ElnEntryType.Form:
                return ElnFormEntryCriteria(entry_name, data_type, order)
            case ElnEntryType.Plugin:
                return ElnPluginEntryCriteria(entry_name, data_type, order)
            case ElnEntryType.Table:
                return ElnTableEntryCriteria(entry_name, data_type, order)
            case ElnEntryType.TempData:
                return ElnTempDataEntryCriteria(entry_name, data_type, order)
            case ElnEntryType.Text:
                return ElnTextEntryCriteria(entry_name, data_type, order)
            case _:
                raise ValueError("Unexpected entry type: " + entry_type.name)
