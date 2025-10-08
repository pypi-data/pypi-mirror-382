from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from functools import total_ordering
from typing import List, Dict, Optional, TypeVar, Generic

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnExperiment, ElnExperimentUpdateCriteria
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry, EntryAttachment, EntryRecordAttachment
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ExperimentEntryCriteriaUtil, \
    ElnAttachmentEntryUpdateCriteria, ElnFormEntryUpdateCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnExperimentStatus, ExperimentEntryStatus, ElnBaseDataType, \
    ElnEntryType
from sapiopylib.rest.utils.autopaging import GetElnEntryRecordAutoPager


@total_ordering
class AbstractStep(ABC):
    """
    The protocol/step interface provides natural workflow abstraction for Sapio workflows.
    A protocol is consisted of multiple steps, in a sequential order.
    It is also a single process step for process tracking.
    A step holds the data and presentation config for a part of workflow.
    A step may be completed, active or unlocked.
    The data records that are part of the step are said to be attached to the step.
    """

    @abstractmethod
    def get_id(self) -> int:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def set_name(self, new_name: str) -> None:
        pass

    @abstractmethod
    def get_data_type_names(self) -> List[str]:
        pass

    @abstractmethod
    def add_records(self, records_to_add: List[DataRecord]):
        """
        Add records to the current step.
        Throws an error if this operation is not supported.
        For ELN entry, only table entry steps can use this method.
        """
        pass

    @abstractmethod
    def remove_records(self, records_to_remove: List[DataRecord]):
        """
        Remove records from the current step.
        Throws an error if this operation is not supported.
        For ELN entry, only table entry steps can use this method.
        """
        pass

    @abstractmethod
    def set_records(self, records_to_set: List[DataRecord]):
        """
        Set records on the current step.
        Available for form, attachment, and table entries.
        However, for form and attachment, exactly one record must be specified here.
        """
        pass

    @abstractmethod
    def get_records(self) -> List[DataRecord]:
        pass

    @abstractmethod
    def get_options(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def set_options(self, new_options: Dict[str, str]) -> None:
        pass

    @abstractmethod
    def complete_step(self) -> None:
        pass

    @abstractmethod
    def unlock_step(self) -> None:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Returns true if user can make edits to the step right now.
        """
        pass

    def __hash__(self):
        return hash(self.get_id())

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, AbstractStep):
            return False
        return self.get_id() == other.get_id()

    @abstractmethod
    def __le__(self, other):
        pass


ProtocolStepType: ProtocolStepType = TypeVar("ProtocolStepType", bound=AbstractStep)


@total_ordering
class AbstractProtocol(Generic[ProtocolStepType], ABC):
    """
    The protocol/step interface provides natural workflow abstraction for Sapio workflows.
    A protocol is consisted of multiple steps, in a sequential order.
    It is also a single process step for process tracking.
    A protocol may be completed, cancelled, or in progress.
    A step holds the data and presentation config for a part of workflow.
    The data records that are part of the step are said to be attached to the step.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """
        Returns true if the protocol can still be edited (not submitted or cancelled).
        """
        pass

    @abstractmethod
    def get_record(self) -> Optional[DataRecord]:
        """
        Get the data record that stores data of the active protocol, if there are any.
        For ELN protocols, this is guaranteed to be non-trivial.
        """
        pass

    @abstractmethod
    def complete_protocol(self) -> None:
        """
        Completing the protocol will complete the current ELN workflow.
        If there are any process-tracking enabled records, these records will advance into the next process step.
        """
        pass

    @abstractmethod
    def cancel_protocol(self) -> None:
        """
        Cancel the protocol will fail the current ELN workflow.
        If there are any process-tracking enabled records, these records will return to the previous return point.
        A return point is a configured process step to return to, in case a tracked record has failed a process step.
        """
        pass

    @abstractmethod
    def get_sorted_step_list(self) -> List[ProtocolStepType]:
        """
        Get the steps within this protocol in sequential order.
        """
        pass

    @abstractmethod
    def get_data_type_name(self) -> str:
        """
        Get the data type that holds the metadata for this protocol.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the protocol.
        """
        pass

    @abstractmethod
    def set_name(self, new_name: str) -> None:
        """
        Set the name of the protocol.
        """
        pass

    @abstractmethod
    def get_id(self) -> int:
        """
        Get the unique, system-wide identifier for the protocol.
        """
        pass

    @abstractmethod
    def get_options(self) -> Dict[str, str]:
        """
        Get the user-invisible options for the protocol. These can be used for certain plugins.
        """
        pass

    @abstractmethod
    def set_options(self, new_options: Dict[str, str]) -> None:
        """
        Set the user-invisible options for the protocol. These can be used for certain plugins.
        """
        pass

    @abstractmethod
    def invalidate(self) -> None:
        """
        Invalidate the current cache, in case the data that is not part of the metadata has changed.
        """
        pass

    def get_first_step_of_type(self, data_type_name: str) -> Optional[ProtocolStepType]:
        """
        Get the first step in the protocol that attaches records of a particular data type.
        """
        target_base_type: ElnBaseDataType = ElnBaseDataType.get_base_type(data_type_name)
        steps = self.get_sorted_step_list()
        for step in steps:
            if data_type_name in step.get_data_type_names():
                return step
            if target_base_type is not None and \
                    target_base_type in [ElnBaseDataType.get_base_type(x) for x in step.get_data_type_names()]:
                return step
        return None

    def get_last_step_of_type(self, data_type_name: str) -> Optional[ProtocolStepType]:
        """
        Get the last step in the protocol that attaches records of a particular data type.
        """
        target_base_type: ElnBaseDataType = ElnBaseDataType.get_base_type(data_type_name)
        steps = reversed(self.get_sorted_step_list())
        for step in steps:
            if data_type_name in step.get_data_type_names():
                return step
            if target_base_type is not None and \
                    target_base_type in [ElnBaseDataType.get_base_type(x) for x in step.get_data_type_names()]:
                return step
        return None

    def get_next_step(self, current_step: AbstractStep, data_type_name: str) -> Optional[ProtocolStepType]:
        """
        Given the current step and a data type name to search for, find the next step after the current step by
        protocol's step sequential order that attaches records of the provided data type.
        This method will never return any steps before or at the provided step in the sequential order.
        """
        steps = self.get_sorted_step_list()
        # If this is the last step in the list, return nothing. Avoid wrapping around error when we +1.
        if steps[-1] == current_step:
            return None
        target_base_type: ElnBaseDataType = ElnBaseDataType.get_base_type(data_type_name)
        try:
            start_index = steps.index(current_step)
            for step in steps[start_index + 1:]:
                if data_type_name in step.get_data_type_names():
                    return step
                if target_base_type is not None and \
                        target_base_type in [ElnBaseDataType.get_base_type(x) for x in step.get_data_type_names()]:
                    return step
        except ValueError:
            return None
        return None

    def get_previous_step(self, current_step: AbstractStep, data_type_name: str) -> Optional[ProtocolStepType]:
        """
        Given the current step and a data type name to search for, find the previous step after the current step by
        protocol's step sequential order that attaches records of the provided data type.
        This method will never return any steps after or at the provided step in the sequential order.
        """
        steps = self.get_sorted_step_list()
        if steps[0] == current_step:
            return None
        target_base_type: ElnBaseDataType = ElnBaseDataType.get_base_type(data_type_name)
        try:
            end_index = steps.index(current_step)
            for step in steps[:end_index]:
                if data_type_name in step.get_data_type_names():
                    return step
                if target_base_type is not None and \
                        target_base_type in [ElnBaseDataType.get_base_type(x) for x in step.get_data_type_names()]:
                    return step
        except ValueError:
            return None
        return None

    def __hash__(self):
        return hash(self.get_id())

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, AbstractProtocol):
            return False
        return self.get_id() == other.get_id()

    def __le__(self, other):
        if other is None:
            return False
        if not isinstance(other, AbstractProtocol):
            return False
        return self.get_id() < other.get_id()

    def __str__(self):
        return self.get_name()

    def __len__(self):
        return self.get_sorted_step_list().__len__()

    def __iter__(self):
        return self.get_sorted_step_list().__iter__()


class ElnEntryStep(AbstractStep):
    """
    This is the ELN step implementation ELN-workflow.
    """
    eln_entry: ExperimentEntry
    protocol: ElnExperimentProtocol
    user: SapioUser

    _LOCKED_STATUSES = [ExperimentEntryStatus.Completed, ExperimentEntryStatus.CompletedApproved,
                        ExperimentEntryStatus.Disabled, ExperimentEntryStatus.LockedAwaitingApproval,
                        ExperimentEntryStatus.LockedRejected]

    def get_name(self) -> str:
        return self.eln_entry.entry_name

    def __init__(self, protocol: ElnExperimentProtocol,
                 eln_entry: ExperimentEntry):
        self.protocol = protocol
        self.user = protocol.user
        self.eln_entry = eln_entry

    def __le__(self, other):
        if other is None:
            return False
        if not isinstance(other, ElnEntryStep):
            return False
        protocol_step_list: List[AbstractStep] = self.protocol.get_sorted_step_list()
        try:
            return protocol_step_list.index(self) <= protocol_step_list.index(other)
        except ValueError:
            return False

    def get_id(self) -> int:
        return self.eln_entry.entry_id

    def get_data_type_names(self) -> List[str]:
        if self.eln_entry.data_type_name:
            return [self.eln_entry.data_type_name]
        return []

    def add_records(self, records_to_add: List[DataRecord]):
        if not records_to_add:
            return
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        if self.eln_entry.entry_type != ElnEntryType.Table:
            raise ValueError("ELN experiment entry must be a table entry when adding records to ELN step.")
        eln_manager.add_records_to_table_entry(self.protocol.eln_experiment.notebook_experiment_id,
                                               self.eln_entry.entry_id, records_to_add)

    def remove_records(self, records_to_remove: List[DataRecord]):
        if not records_to_remove:
            return
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        if self.eln_entry.entry_type != ElnEntryType.Table:
            raise ValueError("ELN experiment entry must be a table entry when removing records to ELN step.")
        eln_manager.remove_records_from_table_entry(self.protocol.eln_experiment.notebook_experiment_id,
                                                    self.eln_entry.entry_id, [x.record_id for x in records_to_remove])

    def set_records(self, records_to_set: List[DataRecord]) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        if self.eln_entry.entry_type == ElnEntryType.Table:
            cur_records = self.get_records()
            cur_record_id_set = [x.record_id for x in cur_records]
            record_id_to_set = [x.record_id for x in records_to_set]
            records_to_add: List[DataRecord] = []
            records_to_remove: List[DataRecord] = []
            for record_to_set in records_to_set:
                if record_to_set.record_id not in cur_record_id_set:
                    records_to_add.append(record_to_set)
            for cur_record in cur_records:
                if cur_record.record_id not in record_id_to_set:
                    records_to_remove.append(cur_record)
            if records_to_add:
                self.add_records(records_to_add)
            if records_to_remove:
                self.remove_records(records_to_remove)
        elif self.eln_entry.entry_type == ElnEntryType.Form:
            if len(records_to_set) != 1:
                raise ValueError("For form entries, there must be exactly one backing record.")
            record_id_to_set = records_to_set[0].record_id
            criteria: ElnFormEntryUpdateCriteria = ElnFormEntryUpdateCriteria()
            criteria.record_id = record_id_to_set
            eln_manager.update_experiment_entry(self.protocol.eln_experiment.notebook_experiment_id,
                                                self.eln_entry.entry_id, criteria)
        elif self.eln_entry.entry_type == ElnEntryType.Attachment:
            criteria: ElnAttachmentEntryUpdateCriteria = ElnAttachmentEntryUpdateCriteria()
            if records_to_set:
                entry_attachment_list: List[EntryAttachment] = []
                for rec in records_to_set:
                    file_path: str = rec.get_field_value("FilePath")
                    if not file_path:
                        raise ValueError("For record " + str(rec) + " the FilePath field must be set on the attachment record first, indicating its filename.")
                    record_id = rec.get_record_id()
                    if record_id < 0:
                        raise ValueError("Data record " + str(rec) + " is a temporary record.")
                    att: EntryRecordAttachment = EntryRecordAttachment(file_path, record_id)
                    entry_attachment_list.append(att)
                criteria.entry_attachment_list = entry_attachment_list
            eln_manager.update_experiment_entry(self.protocol.eln_experiment.notebook_experiment_id,
                                                self.eln_entry.entry_id, criteria)

        else:
            raise ValueError("The entry type does not support set records operation.")

    def get_records(self) -> List[DataRecord]:
        auto_pager = GetElnEntryRecordAutoPager(self.protocol.get_id(), self.get_id(), self.user)
        return auto_pager.get_all_at_once()

    def get_options(self) -> Dict[str, str]:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        return eln_manager.get_experiment_entry_options(self.protocol.eln_experiment.notebook_experiment_id,
                                                        self.eln_entry.entry_id)

    def set_options(self, new_options: Dict[str, str]) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        entry_update_criteria = ExperimentEntryCriteriaUtil.create_empty_criteria(self.eln_entry)
        entry_update_criteria.entry_options_map = new_options
        eln_manager.update_experiment_entry(self.protocol.eln_experiment.notebook_experiment_id,
                                            self.eln_entry.entry_id, entry_update_criteria)

    def complete_step(self) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        eln_manager.submit_experiment_entry(self.protocol.eln_experiment.notebook_experiment_id,
                                            self.eln_entry.entry_id)

    def unlock_step(self) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        entry_update_criteria = ExperimentEntryCriteriaUtil.create_empty_criteria(self.eln_entry)
        entry_update_criteria.entry_status = ExperimentEntryStatus.UnlockedChangesRequired
        eln_manager.update_experiment_entry(self.protocol.eln_experiment.notebook_experiment_id,
                                            self.eln_entry.entry_id, entry_update_criteria)

    def set_name(self, new_name: str) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        entry_update_criteria = ExperimentEntryCriteriaUtil.create_empty_criteria(self.eln_entry)
        entry_update_criteria.entry_name = new_name
        eln_manager.update_experiment_entry(self.protocol.eln_experiment.notebook_experiment_id,
                                            self.eln_entry.entry_id, entry_update_criteria)

    def is_available(self) -> bool:
        # ELN Experiment must not be submitted yet.
        if not self.protocol.is_available():
            return False
        # This entry must not be submitted yet.
        status = self.eln_entry.entry_status
        if status in self._LOCKED_STATUSES:
            return False
        # Either my current user is an author, or my current group is an author.
        user_assignments = self.protocol.eln_experiment.user_roles
        user_role = user_assignments.get(self.user.username)
        if user_role is not None:
            if user_role.is_author:
                return True
        current_group_id = self.user.session_additional_data.current_group_id
        if current_group_id is not None:
            group_assignments = self.protocol.eln_experiment.group_roles
            group_role = group_assignments.get(current_group_id)
            if group_role is not None:
                return group_role.is_author
        return False


class ElnExperimentProtocol(AbstractProtocol[ElnEntryStep]):
    """
    This is an ELN-workflow implementation of the workflow protocol.
    """
    sorted_step_list: Optional[List[ElnEntryStep]]
    eln_experiment: ElnExperiment
    user: SapioUser
    lock: threading.RLock

    _protocol_record_cache: Optional[DataRecord]
    _LOCKED_STATUSES = [ElnExperimentStatus.Completed, ElnExperimentStatus.CompletedApproved,
                        ElnExperimentStatus.LockedRejected, ElnExperimentStatus.LockedAwaitingApproval,
                        ElnExperimentStatus.Canceled]

    def get_record(self) -> Optional[DataRecord]:
        # Keep a cache so continued retrieval over and over again will not cause re-query of DB.
        if self._protocol_record_cache is not None:
            return self._protocol_record_cache
        record_id = self.eln_experiment.experiment_record_id
        self._protocol_record_cache = DataMgmtServer.get_data_record_manager(self.user).query_system_for_record(
            ElnBaseDataType.EXPERIMENT.data_type_name, record_id)
        return self._protocol_record_cache

    def __init__(self, eln_experiment: ElnExperiment, user: SapioUser):
        self.lock = threading.RLock()
        self.eln_experiment = eln_experiment
        self.user = user
        self.sorted_step_list = None
        self._protocol_record_cache = None

    def invalidate(self) -> None:
        with self.lock:
            self.sorted_step_list = None

    def get_data_type_name(self) -> str:
        return self.eln_experiment.experiment_data_type_name

    def get_name(self) -> str:
        return self.eln_experiment.notebook_experiment_name

    def set_name(self, new_name: str) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        update_criteria: ElnExperimentUpdateCriteria = ElnExperimentUpdateCriteria(new_experiment_name=new_name)
        eln_manager.update_notebook_experiment(self.eln_experiment.notebook_experiment_id, update_criteria)

    def get_id(self) -> int:
        return self.eln_experiment.notebook_experiment_id

    def get_options(self) -> Dict[str, str]:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        return eln_manager.get_notebook_experiment_options(self.eln_experiment.notebook_experiment_id)

    def set_options(self, new_options: Dict[str, str]) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        update_criteria: ElnExperimentUpdateCriteria = ElnExperimentUpdateCriteria(experiment_option_map=new_options)
        eln_manager.update_notebook_experiment(self.eln_experiment.notebook_experiment_id, update_criteria)

    def get_sorted_step_list(self) -> List[ElnEntryStep]:
        with self.lock:
            if self.sorted_step_list is not None:
                return self.sorted_step_list
            else:
                eln_manager = DataMgmtServer.get_eln_manager(self.user)
                entry_list = eln_manager.get_experiment_entry_list(self.eln_experiment.notebook_experiment_id,
                                                                   to_retrieve_field_definitions=False)
                sorted_step_list = []
                for entry in entry_list:
                    step = ElnEntryStep(self, entry)
                    sorted_step_list.append(step)
                self.sorted_step_list = sorted_step_list
                return self.sorted_step_list

    def complete_protocol(self) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        update_criteria: ElnExperimentUpdateCriteria = ElnExperimentUpdateCriteria(
            new_experiment_status=ElnExperimentStatus.Completed)
        eln_manager.update_notebook_experiment(self.eln_experiment.notebook_experiment_id, update_criteria)

    def cancel_protocol(self) -> None:
        eln_manager = DataMgmtServer.get_eln_manager(self.user)
        update_criteria: ElnExperimentUpdateCriteria = ElnExperimentUpdateCriteria(
            new_experiment_status=ElnExperimentStatus.Canceled)
        eln_manager.update_notebook_experiment(self.eln_experiment.notebook_experiment_id, update_criteria)

    def is_available(self) -> bool:
        status: ElnExperimentStatus = self.eln_experiment.notebook_experiment_status
        return status not in self._LOCKED_STATUSES
