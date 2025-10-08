from __future__ import annotations

from typing import Optional, Type, List, Union, Iterable, TypeVar, Generic

from sapiopylib.rest.utils.recordmodel.PyRecordModel import AbstractRecordModelPropertyGetter, PyRecordModel, \
    AbstractRecordModelPropertyAdder, \
    AbstractRecordModelPropertyRemover, AbstractRecordModelPropertySetter
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedRecordModel, \
    AbstractRecordModel
from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager

# Record Model Specific Property Type. This is known from static constructors of each property.
_RMSPT = TypeVar("_RMSPT", bound=Union[PyRecordModel, AbstractRecordModel])


class _ParentsGetterProperty(AbstractRecordModelPropertyGetter[List[_RMSPT]], Generic[_RMSPT]):
    _parent_type_name: str
    wrap_results_type: Optional[Type[_RMSPT]]

    def __init__(self, parent_type_name: str, wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._parent_type_name = parent_type_name
        self.wrap_results_type = wrap_results_type

    def get_value(self, model: PyRecordModel) -> List[_RMSPT]:
        models: List[PyRecordModel] = model.get_parents_of_type(self._parent_type_name)
        if not self.wrap_results_type:
            return models
        return RecordModelInstanceManager.wrap_list(models, self.wrap_results_type)


class _ParentsModProperty(AbstractRecordModelPropertyAdder[None], AbstractRecordModelPropertyRemover[None]):
    value_list: List[PyRecordModel]

    def __init__(self, value_list: Iterable[Union[PyRecordModel, AbstractRecordModel]]):
        self.value_list = RecordModelInstanceManager.unwrap_list(value_list)
        self.original_values = value_list

    def remove_value(self, remove_from: PyRecordModel) -> None:
        if self.value_list:
            remove_from.remove_parents(self.value_list)

    def add_value(self, add_to: PyRecordModel) -> None:
        if self.value_list:
            add_to.add_parents(self.value_list)


class _ParentsCreatorProperty(AbstractRecordModelPropertyAdder[List[_RMSPT]], Generic[_RMSPT]):
    """
    Create new parents of data type name with number of records.
    """
    _parent_data_type_name: str
    _num_to_create: int
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, parent_type_name: str, num_to_create: int,
                 wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._parent_data_type_name = parent_type_name
        self._num_to_create = num_to_create
        self.wrap_results_type = wrap_results_type

    def add_value(self, add_to: PyRecordModel) -> List[_RMSPT]:
        inst_man = add_to.record_model_manager.instance_manager
        new_records = inst_man.add_new_records(self._parent_data_type_name, self._num_to_create)
        add_to.add_parents(new_records)
        if self.wrap_results_type:
            return inst_man.wrap_list(new_records, self.wrap_results_type)
        return new_records


class Parents:
    """
    Property getters to obtain or modify parents of record model
    """

    @staticmethod
    def of_type(parent_type: Type[WrappedRecordModel]):
        """
        Get the property getter of parent of specified wrapped record model's data type represented in wrapper class.
        """
        return _ParentsGetterProperty[parent_type](parent_type.get_wrapper_data_type_name(), parent_type)

    @staticmethod
    def of_type_name(parent_type_name: str) -> _ParentsGetterProperty:
        """
        Get the property getter of specified parent data type name.
        """
        return _ParentsGetterProperty[PyRecordModel](parent_type_name=parent_type_name)

    @staticmethod
    def refs(parent_list: Iterable[Union[PyRecordModel, AbstractRecordModel]]):
        """
        Setter/Adder/Remover of parents.
        """
        return _ParentsModProperty(parent_list)

    @staticmethod
    def create_by_name(parent_type_name: str, num_records_to_create: int) -> _ParentsCreatorProperty[PyRecordModel]:
        """
        Creator of new parents
        """
        return _ParentsCreatorProperty[PyRecordModel](parent_type_name, num_records_to_create)

    @staticmethod
    def create(parent_type: Type[WrappedRecordModel], num_records_to_create: int):
        return _ParentsCreatorProperty[parent_type](parent_type.get_wrapper_data_type_name(),
                                                    num_records_to_create, parent_type)


class _ParentGetterProperty(AbstractRecordModelPropertyGetter[_RMSPT], Generic[_RMSPT]):
    _parent_type_name: str
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, parent_type_name: str, wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._parent_type_name = parent_type_name
        self.wrap_results_type = wrap_results_type

    def get_value(self, model: PyRecordModel) -> Optional[_RMSPT]:
        model: Optional[PyRecordModel] = model.get_parent_of_type(self._parent_type_name)
        if not model:
            return None
        if not self.wrap_results_type:
            return model
        return RecordModelInstanceManager.wrap(model, self.wrap_results_type)


class _ParentModProperty(AbstractRecordModelPropertyAdder[None], AbstractRecordModelPropertyRemover[None]):
    value: PyRecordModel

    def __init__(self, value: Union[PyRecordModel, AbstractRecordModel]):
        self.value = RecordModelInstanceManager.unwrap_list([value])[0]

    def remove_value(self, remove_from: PyRecordModel) -> None:
        remove_from.remove_parent(self.value)

    def add_value(self, add_to: PyRecordModel) -> None:
        add_to.add_parent(self.value)


class _ParentCreatorProperty(AbstractRecordModelPropertyAdder[_RMSPT]):
    _parent_type_name: str
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, parent_type_name: str, wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._parent_type_name = parent_type_name
        self.wrap_results_type = wrap_results_type

    def add_value(self, add_to: PyRecordModel) -> _RMSPT:
        rec_man: RecordModelManager = add_to.record_model_manager
        inst_man = rec_man.instance_manager
        new_record = inst_man.add_new_record(self._parent_type_name)
        add_to.add_parent(new_record)
        if self.wrap_results_type:
            return RecordModelInstanceManager.wrap(new_record, self.wrap_results_type)
        return new_record


class Parent:
    """
    Property getters to obtain or modify single parent of record model
    """

    @staticmethod
    def of_type(parent_type: Type[WrappedRecordModel]):
        """
        Get the property getter of parent of specified wrapped record model's data type represented in wrapper class.
        """
        return _ParentGetterProperty[parent_type](parent_type.get_wrapper_data_type_name(), parent_type)

    @staticmethod
    def of_type_name(parent_type_name: str) -> _ParentGetterProperty[PyRecordModel]:
        """
        Get the property getter of specified parent data type name.
        """
        return _ParentGetterProperty[PyRecordModel](parent_type_name=parent_type_name)

    @staticmethod
    def ref(parent: Union[PyRecordModel, AbstractRecordModel]) -> _ParentModProperty:
        """
        Setter/Adder/Remover of parent.
        """
        return _ParentModProperty(parent)

    @staticmethod
    def create_by_name(parent_type_name: str) -> _ParentCreatorProperty[PyRecordModel]:
        """
        Creator of new parent.
        """
        return _ParentCreatorProperty[PyRecordModel](parent_type_name)

    @staticmethod
    def create(parent_type: Type[WrappedRecordModel]):
        """
        Creator of new parent.
        """
        return _ParentCreatorProperty[parent_type](parent_type.get_wrapper_data_type_name(), parent_type)


class _ChildrenGetterProperty(AbstractRecordModelPropertyGetter[List[_RMSPT]]):
    _children_type_name: str
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, children_type_name: str, wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._children_type_name = children_type_name
        self.wrap_results_type = wrap_results_type

    def get_value(self, model: PyRecordModel) -> List[_RMSPT]:
        models: List[PyRecordModel] = model.get_children_of_type(self._children_type_name)
        if not self.wrap_results_type:
            return models
        return RecordModelInstanceManager.wrap_list(models, self.wrap_results_type)


class _ChildrenModProperty(AbstractRecordModelPropertyAdder[None], AbstractRecordModelPropertyRemover[None]):
    value_list: List[PyRecordModel]

    def __init__(self, value_list: Iterable[Union[PyRecordModel, AbstractRecordModel]]):
        self.value_list = RecordModelInstanceManager.unwrap_list(value_list)

    def remove_value(self, remove_from: PyRecordModel) -> None:
        if self.value_list:
            remove_from.remove_children(self.value_list)

    def add_value(self, add_to: PyRecordModel) -> None:
        if self.value_list:
            add_to.add_children(self.value_list)


class _ChildrenCreatorProperty(AbstractRecordModelPropertyAdder[List[_RMSPT]]):
    """
    Create new parents of data type name with number of records.
    """
    _children_data_type_name: str
    _num_to_create: int
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, parent_type_name: str, num_to_create: int,
                 wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._children_data_type_name = parent_type_name
        self._num_to_create = num_to_create
        self.wrap_results_type = wrap_results_type

    def add_value(self, add_to: PyRecordModel) -> List[_RMSPT]:
        inst_man = add_to.record_model_manager.instance_manager
        new_records = inst_man.add_new_records(self._children_data_type_name, self._num_to_create)
        add_to.add_children(new_records)
        if self.wrap_results_type:
            return inst_man.wrap_list(new_records, self.wrap_results_type)
        return new_records


class Children:
    """
    Property getters to obtain or modify children of record model
    """

    @staticmethod
    def of_type(child_type: Type[WrappedRecordModel]):
        """
        Get the property getter of child of specified wrapped record model's data type represented in wrapper class.
        """
        return _ChildrenGetterProperty[child_type](child_type.get_wrapper_data_type_name(), child_type)

    @staticmethod
    def of_type_name(child_type_name: str) -> _ChildrenGetterProperty[PyRecordModel]:
        """
        Get the property getter of specified child data type name.
        """
        return _ChildrenGetterProperty[PyRecordModel](child_type_name)

    @staticmethod
    def refs(children_list: Iterable[Union[PyRecordModel, AbstractRecordModel]]) -> _ChildrenModProperty:
        """
        Setter/Adder/Remover of children.
        """
        return _ChildrenModProperty(children_list)

    @staticmethod
    def create_by_name(children_type_name: str, num_records_to_create: int) -> _ChildrenCreatorProperty[PyRecordModel]:
        """
        Creator of new children
        """
        return _ChildrenCreatorProperty[PyRecordModel](children_type_name, num_records_to_create)

    @staticmethod
    def create(children_type: Type[WrappedRecordModel], num_records_to_create: int):
        """
        Creator of new children.
        """
        return _ChildrenCreatorProperty[children_type](children_type.get_wrapper_data_type_name(),
                                                       num_records_to_create, children_type)


class _ChildGetterProperty(AbstractRecordModelPropertyGetter[_RMSPT]):
    _child_type_name: str
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, child_type_name: str, wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._child_type_name = child_type_name
        self.wrap_results_type = wrap_results_type

    def get_value(self, model: PyRecordModel) -> Optional[_RMSPT]:
        model: Optional[PyRecordModel] = model.get_child_of_type(self._child_type_name)
        if not model:
            return None
        if not self.wrap_results_type:
            return model
        return RecordModelInstanceManager.wrap(model, self.wrap_results_type)


class _ChildModProperty(AbstractRecordModelPropertyAdder[None], AbstractRecordModelPropertyRemover[None]):
    value: PyRecordModel

    def __init__(self, value: Union[PyRecordModel, AbstractRecordModel]):
        self.value = RecordModelInstanceManager.unwrap_list([value])[0]

    def remove_value(self, remove_from: PyRecordModel) -> None:
        remove_from.remove_child(self.value)

    def add_value(self, add_to: PyRecordModel) -> None:
        add_to.add_child(self.value)


class _ChildCreatorProperty(AbstractRecordModelPropertyAdder[_RMSPT]):
    _child_type_name: str
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, child_type_name: str, wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._child_type_name = child_type_name
        self.wrap_results_type = wrap_results_type

    def add_value(self, add_to: PyRecordModel) -> _RMSPT:
        rec_man: RecordModelManager = add_to.record_model_manager
        inst_man = rec_man.instance_manager
        new_record = inst_man.add_new_record(self._child_type_name)
        add_to.add_child(new_record)
        if self.wrap_results_type:
            return RecordModelInstanceManager.wrap(new_record, self.wrap_results_type)
        return new_record


class Child:
    """
    Property getters to obtain or modify single child of record model
    """

    @staticmethod
    def of_type(child_type: Type[WrappedRecordModel]):
        """
        Get the property getter of child of specified wrapped record model's data type represented in wrapper class.
        """
        return _ChildGetterProperty[child_type](child_type.get_wrapper_data_type_name(), child_type)

    @staticmethod
    def of_type_name(child_type_name: str) -> _ChildGetterProperty[PyRecordModel]:
        """
        Get the property getter of specified child data type name.
        """
        return _ChildGetterProperty[PyRecordModel](child_type_name)

    @staticmethod
    def ref(child: Union[PyRecordModel, AbstractRecordModel]) -> _ChildModProperty:
        """
        Setter/Adder/Remover of child.
        """
        return _ChildModProperty(child)

    @staticmethod
    def create_by_name(child_type_name: str) -> _ChildCreatorProperty[PyRecordModel]:
        """
        Creator of new child.
        """
        return _ChildCreatorProperty[PyRecordModel](child_type_name)

    @staticmethod
    def create(child_type: Type[WrappedRecordModel]):
        """
        Creator of new child.
        """
        return _ChildCreatorProperty[child_type](child_type.get_wrapper_data_type_name(), child_type)


class Ancestors(AbstractRecordModelPropertyGetter[List[_RMSPT]]):
    """
    Property getters to obtain ancestors of record model
    """
    _ancestors_type_name: str
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, ancestor_type_name: str, wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._ancestors_type_name = ancestor_type_name
        self.wrap_results_type = wrap_results_type

    @staticmethod
    def of_type(ancestor_type: Type[WrappedRecordModel]):
        """
        Get the property getter of ancestors of specified wrapped record model's data type represented in wrapper class.
        """
        return Ancestors[ancestor_type](ancestor_type.get_wrapper_data_type_name(), ancestor_type)

    @staticmethod
    def of_type_name(ancestor_type_name: str) -> Ancestors[PyRecordModel]:
        """
        Get the property getter of specified ancestors data type name.
        """
        return Ancestors[PyRecordModel](ancestor_type_name=ancestor_type_name)

    def get_value(self, model: PyRecordModel) -> List[_RMSPT]:
        ancestor_man = RecordModelAncestorManager(model.record_model_manager)
        models: List[PyRecordModel] = list(ancestor_man.get_ancestors_of_type(model, self._ancestors_type_name))
        if not self.wrap_results_type:
            return models
        return RecordModelInstanceManager.wrap_list(models, self.wrap_results_type)


class Descendants(AbstractRecordModelPropertyGetter[List[_RMSPT]]):
    """
    Property getters to obtain descendants of record model
    """
    _desc_type_name: str
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, desc_type_name: str, wrap_results_type: Optional[Type[WrappedRecordModel]] = None):
        self._desc_type_name = desc_type_name
        self.wrap_results_type = wrap_results_type

    @staticmethod
    def of_type(desc_type: Type[WrappedRecordModel]):
        """
        Get the property getter of descendants of specified wrapped record model's data type represented in wrapper class.
        """
        return Descendants[desc_type](desc_type.get_wrapper_data_type_name(), desc_type)

    @staticmethod
    def of_type_name(desc_type_name: str) -> Descendants[PyRecordModel]:
        """
        Get the property getter of specified descendants data type name.
        """
        return Descendants[PyRecordModel](desc_type_name=desc_type_name)

    def get_value(self, model: PyRecordModel) -> List[_RMSPT]:
        ancestor_man = RecordModelAncestorManager(model.record_model_manager)
        models: List[PyRecordModel] = list(ancestor_man.get_descendant_of_type(model, self._desc_type_name))
        if not self.wrap_results_type:
            return models
        return RecordModelInstanceManager.wrap_list(models, self.wrap_results_type)


class _ForwardSideLinkGetterProperty(AbstractRecordModelPropertyGetter[_RMSPT | None]):
    """
    Property to obtain a forward side link record.
    """
    forward_field_name: str
    wrap_results_type: Optional[Type[WrappedRecordModel]]

    def __init__(self, forward_field_name: str, wrap_result_type: Type[WrappedRecordModel] | None = None):
        self.forward_field_name = forward_field_name
        self.wrap_results_type = wrap_result_type

    @staticmethod
    def of_field(field_name: str, side_link_type: Type[WrappedRecordModel] | None = None):
        return _ForwardSideLinkGetterProperty(field_name, side_link_type)

    def get_value(self, model: PyRecordModel) -> _RMSPT | None:
        ret: PyRecordModel | None = model.get_forward_side_link(self.forward_field_name)
        if not ret or not self.wrap_results_type:
            return ret
        return RecordModelInstanceManager.wrap(ret, self.wrap_results_type)


class _ForwardSideLinkSetterProperty(AbstractRecordModelPropertySetter[None]):
    field_name: str
    value: PyRecordModel | None

    def __init__(self, field_name: str, value: PyRecordModel | None):
        self.field_name = field_name
        self.value = value

    def set_value(self, set_to: PyRecordModel) -> None:
        # PR-53250: Call the existing set_side_link method so that the side link is set correctly.
        set_to.set_side_link(self.field_name, self.value)


class ForwardSideLink:
    """
    Obtaining properties for forward side links.
    """

    @staticmethod
    def of(forward_field_name: str, wrap_result_type: Type[WrappedRecordModel] | None = None):
        """
        Obtain a getter property for the forward side link on this record's particular field.
        """
        return _ForwardSideLinkGetterProperty(forward_field_name, wrap_result_type)

    @staticmethod
    def ref(forward_field_name: str, value: PyRecordModel | WrappedRecordModel | None):
        """
        Obtain a setter property for the forward side link on tihs record's particular field.
        """
        if value is None:
            return _ForwardSideLinkSetterProperty(forward_field_name, None)
        return _ForwardSideLinkSetterProperty(forward_field_name, RecordModelInstanceManager.unwrap(value))


class _ReverseSideLinkGetterProperty(AbstractRecordModelPropertyGetter[list[_RMSPT]]):
    reverse_data_type_name: str
    reverse_field_name: str
    wrap_results_type: Type[WrappedRecordModel] | None

    def __init__(self, reverse_data_type_name: str, reverse_field_name: str,
                 wrap_results_type: Type[WrappedRecordModel] | None = None):
        self.reverse_data_type_name = reverse_data_type_name
        self.reverse_field_name = reverse_field_name
        self.wrap_results_type = wrap_results_type

    def get_value(self, model: PyRecordModel) -> list[_RMSPT]:
        reverse_side_links = model.get_reverse_side_link(self.reverse_data_type_name, self.reverse_field_name)
        if not self.wrap_results_type:
            return reverse_side_links
        return RecordModelInstanceManager.wrap_list(reverse_side_links, self.wrap_results_type)


class ReverseSideLink:
    """
    Getter for reverse side link property.
    """
    @staticmethod
    def of(reverse_data_type_name: str, reverse_data_field_name: str):
        return _ReverseSideLinkGetterProperty(reverse_data_type_name, reverse_data_field_name)

    @staticmethod
    def of_type(reverse_data_type: Type[WrappedRecordModel], reverse_data_field_name: str):
        return _ReverseSideLinkGetterProperty(reverse_data_type.get_wrapper_data_type_name(), reverse_data_field_name, reverse_data_type)