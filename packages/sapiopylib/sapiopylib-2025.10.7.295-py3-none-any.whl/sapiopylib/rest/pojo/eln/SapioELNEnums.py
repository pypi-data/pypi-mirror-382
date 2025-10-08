from __future__ import annotations

from enum import Enum
from typing import Optional


class ElnEntryType(Enum):
    """
    Specify a type of ELN entry.
    """
    Table = 0
    Form = 1
    Attachment = 2
    Plugin = 3
    Dashboard = 4
    Text = 5
    TempData = 6


class ExperimentEntryStatus(Enum):
    """
    Statuses for experiment entries
    """
    Enabled = 'Enabled'
    Disabled = 'Disabled'
    LockedAwaitingApproval = 'Locked - Awaiting Approval'
    LockedRejected = 'Locked - Rejected By Approver'
    UnlockedChangesRequired = 'Unlocked - Approver Requires Changes'
    UnlockedElnAdministrator = 'Unlocked - ELN Administrator'
    CompletedApproved = 'Completed - Approved'
    Completed = 'Completed'

    description: str

    def __init__(self, description: str):
        self.description = description


class ElnExperimentStatus(Enum):
    """
    Statuses for ELN notebook experiments
    """
    New = 'New Notebook Experiment'
    LockedAwaitingApproval = 'Locked - Awaiting Approval'
    LockedRejected = 'Locked - Rejected By Approver'
    UnlockedChangesRequired = 'Unlocked - Approver Requires Changes'
    UnlockedElnAdministrator = 'Unlocked - ELN Administrator'
    CompletedApproved = 'Completed - Approved'
    Completed = 'Completed'
    Canceled = 'Canceled'

    description: str

    def __init__(self, description: str):
        self.description = description


class EntryAttachmentType(Enum):
    ElnExperimentEntryRecordAttachmentPojo = 0
    ElnExperimentEntryStaticAttachmentPojo = 1


class TemplateAccessLevel(Enum):
    PUBLIC = 0
    PRIVATE = 1

class LocationAssignmentType(Enum):
    REQUIRE_ASSIGNMENT = "Require Users to Provide a Location for New Experiments"
    OPTIONAL_ASSIGNMENT = "Optionally Allow Users to Provide a Location for New Experiments"
    PREVENT_ASSIGNMENT = "Do Not Associate Locations with New Experiments"

    text: str

    def __init__(self, text: str):
        self.text = text


class ElnBaseDataType(Enum):
    EXPERIMENT = 'ELNExperiment'
    EXPERIMENT_DETAIL = 'ELNExperimentDetail'
    SAMPLE_DETAIL = 'ELNSampleDetail'
    TEXT_ENTRY_DETAIL = 'ELNTextEntryDetail'

    data_type_name: str

    def __init__(self, data_type_name: str):
        self.data_type_name = data_type_name

    @staticmethod
    def is_eln_type(data_type: Optional[str]):
        """
        Tests whether a data type is of ELN type.
        """
        if data_type is None or not data_type:
            return False
        for base_type in ElnBaseDataType:
            if data_type.lower().startswith(base_type.data_type_name.lower()):
                return True
        return False

    @staticmethod
    def is_base_data_type(data_type: Optional[str]):
        if not data_type:
            return False
        for base_type in ElnBaseDataType:
            if base_type.data_type_name.lower() == data_type.lower():
                return True
        return False

    @staticmethod
    def get_base_type(data_type: Optional[str]) -> Optional[ElnBaseDataType]:
        """
        If the type is of ELN type, return the type category.
        If not, then return None.
        """
        if data_type is None or not data_type:
            return None
        for base_type in ElnBaseDataType:
            if (data_type.lower() == base_type.data_type_name.lower() or
                    data_type.lower().startswith(base_type.data_type_name.lower() + "_")):
                return base_type
        return None

    @staticmethod
    def get_text_entry_data_field_name():
        """
        Return the data field in the text entry data type that stores the text data as a string for the text entry.
        """
        return "TextField"


def get_eln_text_entry_field_name():
    """
    :return: The name of the only field on a ELN text field entry.
    """
    return 'TextField'
