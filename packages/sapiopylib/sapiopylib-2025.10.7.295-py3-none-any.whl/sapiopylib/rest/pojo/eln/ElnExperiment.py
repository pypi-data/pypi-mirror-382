from datetime import datetime
from typing import Optional, List, Dict, Any

from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.eln.ElnExperimentRole import ElnUserExperimentRole, ElnGroupExperimentRole, \
    ElnExperimentRoleParser
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnExperimentStatus, TemplateAccessLevel, LocationAssignmentType
from sapiopylib.rest.utils.SapioDateUtils import java_millis_to_datetime


class ElnExperiment:
    """
    Holds info about one ELN notebook experiment.

    Attributes:
        notebook_experiment_id (int): The ID of the notebook experiment.

        notebook_experiment_name (str): The name of the notebook experiment.

        experiment_record_id (int): The record ID of the experiment.

        experiment_data_type_name (str): The data type name of the experiment.

        notebook_experiment_status (ElnExperimentStatus or None): The status of the notebook experiment.

        created_by (str or None): The user who created the experiment.

        date_created (int or None): The creation date of the experiment.

        last_modified_by (str or None): The user who last modified the experiment.

        last_modified_date (int or None): The modification date of the experiment.

        owner (str or None): The owner of the experiment.

        template_id (int or None): The ID of the experiment's template.

        approval_due_date (int or None): The approval due date of the experiment.

        modifiable (bool): Flag indicating if the experiment is modifiable.

        user_roles (Dict[str, ElnUserExperimentRole]): User roles in the experiment.

        group_roles (Dict[int, ElnGroupExperimentRole]): Group roles in the experiment.
    """
    notebook_experiment_id: int
    notebook_experiment_name: str
    experiment_record_id: int
    experiment_data_type_name: str
    # Note: the status "None" is mapped as None object in python as it is not a valid enum in python.
    notebook_experiment_status: Optional[ElnExperimentStatus]
    created_by: Optional[str]
    date_created: Optional[int]
    last_modified_by: Optional[str]
    last_modified_date: Optional[int]
    owner: Optional[str]
    template_id: Optional[int]
    approval_due_date: Optional[int]
    modifiable: bool
    user_roles: Dict[str, ElnUserExperimentRole]
    group_roles: Dict[int, ElnGroupExperimentRole]

    def __init__(self, notebook_experiment_id: int, notebook_experiment_name: str,
                 experiment_record_id: int):
        self.notebook_experiment_id = notebook_experiment_id
        self.notebook_experiment_name = notebook_experiment_name
        self.experiment_record_id = experiment_record_id

    def get_last_modified_date(self) -> Optional[datetime]:
        return java_millis_to_datetime(self.last_modified_date)

    def get_date_created(self) -> Optional[datetime]:
        return java_millis_to_datetime(self.date_created)

    def __eq__(self, other):
        if not isinstance(other, ElnExperiment):
            return False
        return self.notebook_experiment_id == other.notebook_experiment_id and \
            self.experiment_record_id == other.experiment_record_id

    def __hash__(self):
        return hash((self.notebook_experiment_id, self.experiment_record_id))

    def __str__(self):
        return self.notebook_experiment_name


NotebookExperiment = ElnExperiment


class ElnTemplate:
    """
    Includes metadata of an ELN Template Experiment.

    Attributes:
        template_id: The identifier of the Template Experiment this info object represents
        template_name: The underlying name of the Template Experiment this info object represents
        display_name: The display name of the Template Experiment this info object represents
        active: Whether or not this template is active
        created
        date_created
        last_modified_by
        last_modified_date
        access_level: How accessible this Template Experiment is.  If the template is PRIVATE, then only the user that created the template can see it.  If the template is PUBLIC, then all users in the system can see the template.
        modifiable: Whether or not users can modify the experiment created from this template through the UI.
        entry_addable: Whether or not users can add entries to the experiment created from this template through the UI.
        template_version: The version of this template.  Template versions are only set on public templates.
        classic_display: Whether or not this template will create experiments that use the classic ELN display.
        location_assignment_type: Specifies how the locations will be assigned to experiments created from this template.
        inherit_access_from_parents: Whether or not the experiments created from this template will inherit their access privileges  from their parent record.  When this is true the role assignments will not be used in the experiment.
    """
    template_id: int
    template_name: str
    display_name: Optional[str]
    description: Optional[str]
    active: bool
    created_by: Optional[str]
    date_created: Optional[int]
    last_modified_by: Optional[str]
    last_modified_date: Optional[int]
    access_level: TemplateAccessLevel | None
    modifiable: bool
    entry_addable: bool
    template_version: int | None
    classic_display: bool
    location_assignment_type: LocationAssignmentType | None
    inherit_access_from_parents: bool
    restricted: bool
    hide_embedded_chat: bool

    def __init__(self, template_id: int, template_name: str,
                 display_name: Optional[str], description: Optional[str],
                 active: bool, created_by: Optional[str], date_created: Optional[int],
                 last_modified_by: Optional[str], last_modified_date: Optional[int],
                 access_level: TemplateAccessLevel | None, modifiable: bool,
                 entry_addable: bool, template_version: int | None, classic_display: bool,
                 location_assignment_type: LocationAssignmentType | None, inherit_access_from_parents: bool,
                 restricted: bool, hide_embedded_chat: bool):
        self.template_id = template_id
        self.template_name = template_name
        self.display_name = display_name
        self.description = description
        self.active = active
        self.created_by = created_by
        self.date_created = date_created
        self.last_modified_by = last_modified_by
        self.last_modified_date = last_modified_date
        self.access_level = access_level
        self.modifiable = modifiable
        self.entry_addable = entry_addable
        self.template_version = template_version
        self.classic_display = classic_display
        self.location_assignment_type = location_assignment_type
        self.inherit_access_from_parents = inherit_access_from_parents
        self.restricted = restricted
        self.hide_embedded_chat = hide_embedded_chat

    def get_date_created(self) -> Optional[datetime]:
        return java_millis_to_datetime(self.date_created)

    def get_last_modified_date(self) -> Optional[datetime]:
        return java_millis_to_datetime(self.last_modified_date)

    def __eq__(self, other):
        if not isinstance(other, ElnTemplate):
            return False
        return self.template_id == other.template_id

    def __hash__(self):
        return hash(self.template_id)

    def __str__(self):
        return self.template_name + " (" + self.display_name + ")"


TemplateExperiment = ElnTemplate


class ELNExperimentParser:
    @staticmethod
    def parse_template_experiment(json_dct: Dict[str, Any]) -> ElnTemplate:
        template_id: int = int(json_dct.get('templateId'))
        template_name: str = json_dct.get('templateName')
        display_name: str = json_dct.get('displayName')
        description: Optional[str] = json_dct.get('description')
        active: bool = json_dct.get('active')
        created_by: Optional[str] = json_dct.get('createdBy')
        date_created: Optional[int] = json_dct.get('dateCreated')
        last_modified_by: Optional[str] = json_dct.get('lastModifiedBy')
        last_modified_date: Optional[int] = json_dct.get('lastModifiedDate')

        access_level: TemplateAccessLevel | None = None
        access_level_str: str = json_dct.get('accessLevel')
        if access_level_str:
            access_level = TemplateAccessLevel[access_level_str]
        modifiable: bool = json_dct.get('modifiable')
        entry_addable: bool = json_dct.get('entryAddable')
        template_version: int | None = json_dct.get("templateVersion")
        classic_display: bool = json_dct.get('classicDisplay')
        location_assignment_type: LocationAssignmentType | None = None
        location_assignment_type_str: str = json_dct.get("locationAssignmentType")
        if location_assignment_type_str:
            location_assignment_type = LocationAssignmentType[location_assignment_type_str]
        inherit_access_from_parents: bool = json_dct.get('inheritAccessFromParents')
        restricted: bool = json_dct.get('restricted')
        hide_embedded_chat: bool = json_dct.get('hideEmbeddedChat')

        return ElnTemplate(template_id, template_name,
                           display_name=display_name, description=description,
                           active=active, created_by=created_by, date_created=date_created,
                           last_modified_by=last_modified_by, last_modified_date=last_modified_date,
                           access_level=access_level, modifiable=modifiable,
                           entry_addable=entry_addable, template_version=template_version,
                           classic_display=classic_display, location_assignment_type=location_assignment_type,
                           inherit_access_from_parents=inherit_access_from_parents, restricted=restricted,
                           hide_embedded_chat=hide_embedded_chat)

    @staticmethod
    def parse_eln_experiment(json_dct: Dict[str, Any]) -> ElnExperiment:
        notebook_experiment_id: int = int(json_dct.get('notebookExperimentId'))
        notebook_experiment_name: str = json_dct.get('notebookExperimentName')
        experiment_record_id: int = int(json_dct.get('experimentRecordId'))
        ret: ElnExperiment = ElnExperiment(notebook_experiment_id, notebook_experiment_name, experiment_record_id)
        ret.experiment_data_type_name = json_dct.get('experimentDataTypeName')
        status_name = json_dct.get('notebookExperimentStatus')
        if status_name is None or 'None' == status_name:
            ret.notebook_experiment_status = None
        else:
            ret.notebook_experiment_status = ElnExperimentStatus[status_name]
        ret.created_by = json_dct.get('createdBy')
        ret.date_created = json_dct.get('dateCreated')
        ret.last_modified_by = json_dct.get('lastModifiedBy')
        ret.last_modified_date = json_dct.get('lastModifiedDate')
        ret.owner = json_dct.get('notebookExperimentOwner')
        ret.template_id = json_dct.get('sourceTemplateId')
        ret.approval_due_date = json_dct.get('approvalDueDate')
        ret.modifiable = json_dct.get('modifiable')

        user_roles_dict_dict: Optional[Dict[str, Dict[str, Any]]] = json_dct.get('userRoles')
        if user_roles_dict_dict is not None:
            user_roles: Dict[str, ElnUserExperimentRole] = dict()
            for username, role_dict in user_roles_dict_dict.items():
                user_roles[username] = ElnExperimentRoleParser.parse_user_role(role_dict)
            ret.user_roles = user_roles

        group_roles_dict_dict: Optional[Dict[str, Dict[str, Any]]] = json_dct.get('groupRoles')
        if group_roles_dict_dict is not None:
            group_roles: Dict[int, ElnGroupExperimentRole] = dict()
            for group_id, role_dict in group_roles_dict_dict.items():
                group_roles[int(group_id)] = ElnExperimentRoleParser.parse_group_role(role_dict)
            ret.group_roles = group_roles
        return ret


class InitializeNotebookExperimentPojo:
    """
    The class that creates the initial data for notebook experiment.
    """
    experiment_name: str
    template_experiment_id: Optional[int]
    parent_data_record: Optional[DataRecord]

    def __init__(self, experiment_name: str, template_experiment_id: Optional[int] = None,
                 parent_data_record: Optional[DataRecord] = None):
        """
        Create a new experiment's payload data for creation method.
        :param experiment_name: The new experiment's name.
        :param template_experiment_id: The template ID to source the original experiment.
        Can be None if not from template.
        :param parent_data_record: The parent record to attach this experiment under.
        Must be eligible by data type relations. Use 'None' if no parent record (stored in aether)
        """
        self.experiment_name = experiment_name
        self.template_experiment_id = template_experiment_id
        self.parent_data_record = parent_data_record

    def to_json(self) -> Dict[str, Any]:
        parent_record = None
        if self.parent_data_record is not None:
            parent_record = self.parent_data_record.to_json()
        return {
            'notebookExperimentName': self.experiment_name,
            'templateExperimentId': self.template_experiment_id,
            'parentDataRecord': parent_record
        }


class TemplateExperimentQueryPojo:
    """
    The search criteria used to look for Template in the system.
    """
    template_id_white_list: Optional[List[int]]
    template_id_black_list: Optional[List[int]]
    latest_version_only: bool
    access_level_white_list: Optional[List[TemplateAccessLevel]]
    active_templates_only: bool

    def __init__(self, template_id_white_list: Optional[List[int]] = None,
                 template_id_black_list: Optional[List[int]] = None, latest_version_only: bool = True,
                 access_level_white_list: Optional[List[TemplateAccessLevel]] = None,
                 active_templates_only=True):
        self.template_id_white_list = template_id_white_list
        self.template_id_black_list = template_id_black_list
        self.latest_version_only = latest_version_only
        self.access_level_white_list = access_level_white_list
        self.active_templates_only = active_templates_only

    def to_json(self) -> Dict[str, Any]:
        access_level_white_list = None
        if self.access_level_white_list is not None:
            access_level_white_list = [x.name for x in self.access_level_white_list]
        return {
            'templateExperimentIdWhiteList': self.template_id_white_list,
            'templateExperimentIdBlackList': self.template_id_black_list,
            'latestVersionOnly': self.latest_version_only,
            'accessLevelWhiteList': access_level_white_list,
            'activeTemplatesOnly': self.active_templates_only
        }


TemplateExperimentQuery = TemplateExperimentQueryPojo


class ElnExperimentUpdateCriteria:
    """
    Payload containing new data to update ELN Experiment already exists in Sapio.
    Only specify the values that are to be changed. Leave unchanged values as None.

    Attributes:
        new_experiment_name (str or None): The new name of the experiment.

        new_experiment_status (ElnExperimentStatus or None): The new status of the experiment.

        experiment_option_map (Dict[str, str] or None): Mapping of the experiment options.
    """
    new_experiment_name: Optional[str]
    new_experiment_status: Optional[ElnExperimentStatus]
    experiment_option_map: Optional[Dict[str, str]]

    def __init__(self, new_experiment_name: Optional[str] = None,
                 new_experiment_status: Optional[ElnExperimentStatus] = None,
                 experiment_option_map: Optional[Dict[str, str]] = None):
        self.new_experiment_name = new_experiment_name
        self.new_experiment_status = new_experiment_status
        self.experiment_option_map = experiment_option_map

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = dict()
        if self.new_experiment_name is not None:
            ret['newExperimentName'] = self.new_experiment_name
        if self.new_experiment_status is not None:
            ret['newExperimentStatus'] = self.new_experiment_status.name
        if self.experiment_option_map is not None:
            ret['experimentOptionMap'] = self.experiment_option_map
        return ret


class ElnExperimentQueryCriteria:
    """
    Find the ELN experiments by a complex query search object.
    """
    owned_by_white_list: Optional[List[str]]
    owned_by_black_list: Optional[List[str]]
    status_white_list: Optional[List[ElnExperimentStatus]]
    notebook_experiment_id_white_list: Optional[List[int]]
    notebook_experiment_id_black_list: Optional[List[int]]
    ancestor_record_id_white_list: Optional[List[int]]
    source_template_id_white_list: Optional[List[int]]
    limit: int = 0

    def __init__(self, owned_by_white_list: Optional[List[str]] = None, owned_by_black_list: Optional[List[str]] = None,
                 status_white_list: Optional[List[ElnExperimentStatus]] = None,
                 notebook_experiment_id_white_list: Optional[List[int]] = None,
                 notebook_experiment_id_black_list: Optional[List[int]] = None,
                 ancestor_record_id_white_list: Optional[List[int]] = None,
                 source_template_id_white_list: Optional[List[int]] = None,
                 limit: int = 0):
        """
        Create a new ELN query criteria to search a list of ELN experiments in ELN service.
        :param owned_by_white_list: The whitelist of owners for returned experiments.
        :param owned_by_black_list: The blacklist of owners for returned experiments.
        :param status_white_list: The status white list for returned experiments.
        :param notebook_experiment_id_white_list: The ELN ID whitelist for returned experiments.
        :param notebook_experiment_id_black_list: The ELN ID blacklist for returned experiments.
        :param ancestor_record_id_white_list: The ancestor record ID whitelist for returned experiments.
        :param source_template_id_white_list: The source template ID whitelist for returned experiments.
        :param limit: Default is unlimited with value of 0. Decides maximum number of results for this request.
        """
        self.owned_by_white_list = owned_by_white_list
        self.owned_by_black_list = owned_by_black_list
        self.status_white_list = status_white_list
        self.notebook_experiment_id_white_list = notebook_experiment_id_white_list
        self.notebook_experiment_id_black_list = notebook_experiment_id_black_list
        self.ancestor_record_id_white_list = ancestor_record_id_white_list
        self.source_template_id_white_list = source_template_id_white_list
        self.limit = limit

    def to_json(self) -> Dict[str, Any]:
        status_name_white_list: Optional[List[str]] = None
        if self.status_white_list:
            status_name_white_list = [x.name for x in self.status_white_list]
        return {
            "ownedByWhitelist": self.owned_by_white_list,
            "ownedByBlacklist": self.owned_by_black_list,
            'statusWhitelist': status_name_white_list,
            "notebookExperimentIdWhitelist": self.notebook_experiment_id_white_list,
            "notebookExperimentIdBlacklist": self.notebook_experiment_id_black_list,
            "ancestorRecordIdWhitelist": self.ancestor_record_id_white_list,
            "sourceTemplateIdWhiteList": self.source_template_id_white_list,
            "limit": self.limit
        }
