from enum import Enum
from typing import Optional, List, Dict, Any


class OwnerAssignmentType(Enum):
    """
    Enum representing the different types of ownership that can be applied to records of a given data type.
    """
    NONE = "No Owner"
    SINGLE = "Single Owner"
    MULTIPLE = "Multiple Owners"

    display_name: str

    def __init__(self, display_name: str):
        self.display_name = display_name


class DataTypeHierarchy:
    """
    Describes a data type relationship between a parent and child data type.
    """
    parent_data_type_name: str
    child_data_type_name: str
    is_under_many: bool
    is_single_child: bool

    def __init__(self, parent_data_type_name: str, child_data_type_name: str,
                 is_under_many: bool, is_single_child: bool):
        self.parent_data_type_name = parent_data_type_name
        self.child_data_type_name = child_data_type_name
        self.is_under_many = is_under_many
        self.is_single_child = is_single_child

    def __str__(self):
        return self.parent_data_type_name + " -> " + self.child_data_type_name

    def __eq__(self, other):
        if not isinstance(other, DataTypeHierarchy):
            return False
        return self.parent_data_type_name == other.parent_data_type_name and \
            self.child_data_type_name == other.child_data_type_name and \
            self.is_under_many == other.is_under_many and \
            self.is_single_child == other.is_single_child

    def __hash__(self):
        return hash((self.parent_data_type_name, self.child_data_type_name, self.is_under_many, self.is_single_child))

    def to_json(self) -> dict[str, Any]:
        return {
            "parentDataTypeName": self.parent_data_type_name,
            "childDataTypeName": self.child_data_type_name,
            "underMany": self.is_under_many,
            "singleChild": self.is_single_child
        }


class DataTypeDefinition:
    """
    Describes a data type, but does not include its layout.
    """
    _data_type_name: str
    data_type_id: int
    display_name: str
    plural_display_name: str
    description: Optional[str]
    is_pseudo: bool
    is_high_volume: bool
    is_attachment: bool
    attachment_type: Optional[str]
    is_user_defined: bool
    is_record_image_assignable: bool
    is_extension_type: bool
    is_single_parent_type: bool
    owner_assignment_type: OwnerAssignmentType
    is_default_creator_ownership: bool
    parent_list: Optional[List[DataTypeHierarchy]]
    child_list: Optional[List[DataTypeHierarchy]]
    tag: str | None

    @property
    def data_type_name(self):
        """
        The data type name (identifier) of the data type definition.
        """
        return self._data_type_name

    def get_data_type_name(self):
        """
        Get the data type name of this data type.
        """
        return self._data_type_name

    def __init__(self, data_type_name: str, data_type_id: int = -1, display_name: str | None = None,
                 plural_display_name: str | None = None, description: Optional[str] = None,
                 is_pseudo: bool = False, is_high_volume: bool = False, is_attachment: bool = False,
                 attachment_type: Optional[str] = None, is_user_defined: bool = False,
                 is_record_image_assignable: bool = False,
                 is_extension_type: bool = False, is_single_parent_type: bool = False,
                 owner_assignment_type: OwnerAssignmentType = OwnerAssignmentType.NONE,
                 is_default_creator_ownership: bool = False,
                 parent_list: Optional[List[DataTypeHierarchy]] = None,
                 child_list: Optional[List[DataTypeHierarchy]] = None,
                 tag: str | None = None):
        self._data_type_name = data_type_name
        if not display_name:
            display_name = data_type_name
        if not plural_display_name:
            plural_display_name = display_name + "s"
        self.data_type_id = data_type_id
        self.display_name = display_name
        self.plural_display_name = plural_display_name
        self.description = description
        self.is_pseudo = is_pseudo
        self.is_high_volume = is_high_volume
        self.is_attachment = is_attachment
        self.attachment_type = attachment_type
        self.is_user_defined = is_user_defined
        self.is_record_image_assignable = is_record_image_assignable
        self.is_single_parent_type = is_single_parent_type
        self.is_extension_type = is_extension_type
        self.owner_assignment_type = owner_assignment_type
        self.is_default_creator_ownership = is_default_creator_ownership
        self.parent_list = parent_list
        self.child_list = child_list
        self.tag = tag

    def __eq__(self, other):
        if not isinstance(other, DataTypeDefinition):
            return False
        return self.get_data_type_name() == other.get_data_type_name() and self.data_type_id == other.data_type_id

    def __hash__(self):
        return hash((self.data_type_id, self.get_data_type_name()))

    def __str__(self):
        return self.display_name

    def to_json(self) -> dict[str, Any]:
        return {
            "dataTypeName": self._data_type_name,
            "dataTypeId": self.data_type_id,
            "displayName": self.display_name,
            "pluralDisplayName": self.plural_display_name,
            "description": self.description,
            "pseudo": self.is_pseudo,
            "highVolume": self.is_high_volume,
            "attachment": self.is_attachment,
            "attachmentType": self.attachment_type,
            "userDefined": self.is_user_defined,
            "recordImageAssignable": self.is_record_image_assignable,
            "extensionType": self.is_extension_type,
            "singleParentType": self.is_single_parent_type,
            "ownerAssignmentType": self.owner_assignment_type.name,
            "defaultCreatorOwnership": self.is_default_creator_ownership,
            "parentList": [x.to_json() for x in self.parent_list] if self.parent_list is not None else None,
            "childList": [x.to_json() for x in self.child_list] if self.child_list is not None else None,
            "tag": self.tag
        }


class DataTypeParser:
    @staticmethod
    def parse_data_type_definition(json_dct: Dict[str, Any]) -> DataTypeDefinition:
        data_type_name: str = json_dct.get('dataTypeName')
        data_type_id: int = json_dct.get('dataTypeId')
        display_name: str = json_dct.get('displayName')
        plural_display_name: str = json_dct.get('pluralDisplayName')
        description: Optional[str] = json_dct.get('description')
        is_pseudo: bool = json_dct.get('pseudo')
        is_high_volume: bool = json_dct.get('highVolume')
        is_attachment: bool = json_dct.get('attachment')
        attachment_type: Optional[str] = json_dct.get('attachmentType')
        is_user_defined: bool = json_dct.get('userDefined')
        is_record_image_assignable: bool = json_dct.get('recordImageAssignable')
        is_extension_type: bool = json_dct.get('extensionType')
        is_single_parent_type: bool = json_dct.get('singleParentType')
        owner_assignment_type: OwnerAssignmentType = OwnerAssignmentType.NONE
        owner_assignment_name = json_dct.get('ownerAssignmentType')
        if owner_assignment_name is not None and len(owner_assignment_name) > 0:
            owner_assignment_type = OwnerAssignmentType[owner_assignment_name]
        is_default_creator_ownership: bool = json_dct.get('defaultCreatorOwnership')
        parent_list: Optional[List[DataTypeHierarchy]] = None
        if json_dct.get('parentList') is not None:
            parent_list = [DataTypeParser.parse_data_type_hierarchy(x) for x in json_dct.get('parentList')]
        child_list: Optional[List[DataTypeHierarchy]] = None
        if json_dct.get('childList') is not None:
            child_list = [DataTypeParser.parse_data_type_hierarchy(x) for x in json_dct.get('childList')]
        tag: str | None = json_dct.get('tag')
        return DataTypeDefinition(data_type_name, data_type_id, display_name, plural_display_name,
                                  description=description, is_pseudo=is_pseudo, is_high_volume=is_high_volume,
                                  is_attachment=is_attachment, attachment_type=attachment_type,
                                  is_user_defined=is_user_defined,
                                  is_record_image_assignable=is_record_image_assignable,
                                  is_extension_type=is_extension_type,
                                  is_single_parent_type=is_single_parent_type,
                                  owner_assignment_type=owner_assignment_type,
                                  is_default_creator_ownership=is_default_creator_ownership,
                                  parent_list=parent_list, child_list=child_list, tag=tag)

    @staticmethod
    def parse_data_type_hierarchy(json_dct: Dict[str, Any]) -> DataTypeHierarchy:
        parent_data_type_name: str = json_dct.get('parentDataTypeName')
        child_data_type_name: str = json_dct.get('childDataTypeName')
        is_under_many: bool = json_dct.get('underMany')
        is_single_child: bool = json_dct.get('singleChild')
        return DataTypeHierarchy(parent_data_type_name, child_data_type_name, is_under_many, is_single_child)
