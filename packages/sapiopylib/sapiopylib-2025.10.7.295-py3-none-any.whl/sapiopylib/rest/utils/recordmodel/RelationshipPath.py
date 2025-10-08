from __future__ import annotations

from enum import Enum
from typing import List, Type

from sapiopylib.rest.utils.recordmodel import RecordModelWrapper


class RelationshipNodeType(Enum):
    """
    The direction we are querying in along the path.
    """
    PARENT = 1
    CHILD = 2
    ANCESTOR = 3
    DESCENDANT = 4
    FORWARD_SIDE_LINK = 5
    REVERSE_SIDE_LINK = 6


RelationshipPathDir = RelationshipNodeType


class RelationshipNode:
    """
    For internal use.
    Tracks a node along with a relationship path.
    """
    direction: RelationshipNodeType
    data_type_name: str | None
    data_field_name: str | None

    def __init__(self, direction: RelationshipNodeType,
                 data_type_name: str | None = None, data_field_name: str | None = None):
        self.direction = direction
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name

    @staticmethod
    def create_child_node(child_type: str):
        return RelationshipNode(RelationshipNodeType.CHILD, child_type)

    @staticmethod
    def create_parent_node(parent_type: str):
        return RelationshipNode(RelationshipNodeType.PARENT, parent_type)

    @staticmethod
    def create_ancestor_node(ancestor_type: str):
        return RelationshipNode(RelationshipNodeType.ANCESTOR, ancestor_type)

    @staticmethod
    def create_descendant_node(descendant_type: str):
        return RelationshipNode(RelationshipNodeType.DESCENDANT, descendant_type)

    @staticmethod
    def create_forward_side_link_node(forward_side_link_field_name: str):
        return RelationshipNode(RelationshipNodeType.FORWARD_SIDE_LINK, data_field_name=forward_side_link_field_name)

    @staticmethod
    def create_backward_side_link_node(reverse_data_type_name: str, reverse_data_field_name: str):
        return RelationshipNode(RelationshipNodeType.REVERSE_SIDE_LINK, reverse_data_type_name, reverse_data_field_name)


class RelationshipPath:
    """
    Specifies a path of relationship to load, instead of simply loading a single parent/child type at a time.
    """
    path: List[RelationshipNode]

    def __init__(self):
        self.path = []

    def child_type(self, child_type: Type[RecordModelWrapper]) -> RelationshipPath:
        dt_name = child_type.get_wrapper_data_type_name()
        return self.child(dt_name)

    def parent_type(self, parent_type: Type[RecordModelWrapper]) -> RelationshipPath:
        dt_name = parent_type.get_wrapper_data_type_name()
        return self.parent(dt_name)

    def ancestor_type(self, ancestor_type: Type[RecordModelWrapper]) -> RelationshipPath:
        dt_name = ancestor_type.get_wrapper_data_type_name()
        return self.ancestor(dt_name)

    def descendant_type(self, descendant_type: Type[RecordModelWrapper]):
        dt_name = descendant_type.get_wrapper_data_type_name()
        return self.descendant(dt_name)

    def reverse_type(self, reverse_type: Type[RecordModelWrapper], reverse_field_name: str):
        dt_name = reverse_type.get_wrapper_data_type_name()
        return self.reverse_side_link(dt_name, reverse_field_name)

    def child(self, child_type: str) -> RelationshipPath:
        self.path.append(RelationshipNode.create_child_node(child_type))
        return self

    def parent(self, parent_type: str) -> RelationshipPath:
        self.path.append(RelationshipNode.create_parent_node(parent_type))
        return self

    def ancestor(self, ancestor_type: str) -> RelationshipPath:
        self.path.append(RelationshipNode.create_ancestor_node(ancestor_type))
        return self

    def descendant(self, descendant_type: str) -> RelationshipPath:
        self.path.append(RelationshipNode.create_descendant_node(descendant_type))
        return self

    def forward_side_link(self, forward_side_link_field_name: str) -> RelationshipPath:
        self.path.append(RelationshipNode.create_forward_side_link_node(forward_side_link_field_name))
        return self

    def reverse_side_link(self, reverse_data_type_name: str, reverse_data_field_name: str) -> RelationshipPath:
        self.path.append(
            RelationshipNode.create_backward_side_link_node(reverse_data_type_name, reverse_data_field_name))
        return self
