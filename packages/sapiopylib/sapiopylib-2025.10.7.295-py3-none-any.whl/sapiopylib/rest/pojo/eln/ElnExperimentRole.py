from typing import Dict, Any


class AbstractElnExperimentRole:
    """
    Describes the role permissions a principal will have on a ELN notebook experiment.
    """
    is_author: bool
    is_witness: bool
    is_reviewer: bool
    is_approver: bool

    def __init__(self, is_author: bool, is_witness: bool, is_reviewer: bool, is_approver: bool):
        self.is_author = is_author
        self.is_witness = is_witness
        self.is_reviewer = is_reviewer
        self.is_approver = is_approver

    def to_json(self) -> dict[str, Any]:
        return {
            "author": self.is_author,
            "witness": self.is_witness,
            "reviewer": self.is_reviewer,
            "approver": self.is_approver
        }

    def __hash__(self):
        return hash((self.is_author, self.is_witness, self.is_approver, self.is_reviewer))

    def __eq__(self, other):
        if not isinstance(other, AbstractElnExperimentRole):
            return False
        return self.is_author == other.is_author and self.is_reviewer == other.is_reviewer and \
            self.is_witness == other.is_witness and self.is_approver == other.is_approver


class ElnUserExperimentRole(AbstractElnExperimentRole):
    """
    Describes the role permissions a user will have on a ELN notebook experiment.
    """
    username: str

    def __init__(self, is_author: bool, is_witness: bool, is_reviewer: bool, is_approver: bool,
                 username: str):
        super().__init__(is_author, is_witness, is_reviewer, is_approver)
        self.username = username

    def to_json(self):
        ret = super().to_json()
        ret['username'] = self.username
        return ret

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        if not isinstance(other, ElnUserExperimentRole):
            return False
        return self.username == other.username

    def __hash__(self):
        return super().__hash__() ^ hash(self.username)


class ElnGroupExperimentRole(AbstractElnExperimentRole):
    """
    Describes the role permissions a group will have on a ELN notebook experiment.
    """
    group_id: int

    def __init__(self, is_author: bool, is_witness: bool, is_reviewer: bool, is_approver: bool,
                 group_id: int):
        super().__init__(is_author, is_witness, is_reviewer, is_approver)
        self.group_id = group_id

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret['groupId'] = self.group_id
        return ret

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        if not isinstance(other, ElnGroupExperimentRole):
            return False
        return self.group_id == other.group_id

    def __hash__(self):
        return super().__hash__() ^ self.group_id

class ElnRoleAssignment:
    """
    Describes role assignments of a notebook experiment.
    """
    user_role_assignments: list[ElnUserExperimentRole]
    group_role_assignments: list[ElnGroupExperimentRole]

    def __init__(self, user_role_assignments: list[ElnUserExperimentRole] | None, group_role_assignments: list[ElnGroupExperimentRole] | None):
        if user_role_assignments is None:
            user_role_assignments = []
        if group_role_assignments is None:
            group_role_assignments = []
        self.user_role_assignments = user_role_assignments
        self.group_role_assignments = group_role_assignments

    def to_json(self):
        return {
            "userRoleAssignments": [x.to_json() for x in self.user_role_assignments],
            "groupRoleAssignments": [x.to_json() for x in self.group_role_assignments]
        }


class ElnExperimentRoleParser:
    @staticmethod
    def parse_user_role(json_dct: Dict[str, Any]) -> ElnUserExperimentRole:
        return _parse_user_role(json_dct)

    @staticmethod
    def parse_group_role(json_dct: Dict[str, Any]) -> ElnGroupExperimentRole:
        return _parse_group_role(json_dct)


def _parse_abstract_role(json_dct: Dict[str, Any]) -> AbstractElnExperimentRole:
    is_author: bool = json_dct.get('author')
    is_witness: bool = json_dct.get('witness')
    is_reviewer: bool = json_dct.get('reviewer')
    is_approver: bool = json_dct.get('approver')
    return AbstractElnExperimentRole(is_author=is_author, is_witness=is_witness,
                                     is_reviewer=is_reviewer, is_approver=is_approver)


def _parse_user_role(json_dct: Dict[str, Any]) -> ElnUserExperimentRole:
    abstract_role: AbstractElnExperimentRole = _parse_abstract_role(json_dct)
    username = json_dct.get('username')
    return ElnUserExperimentRole(is_author=abstract_role.is_author, is_witness=abstract_role.is_witness,
                                 is_reviewer=abstract_role.is_reviewer, is_approver=abstract_role.is_approver,
                                 username=username)


def _parse_group_role(json_dct: Dict[str, Any]) -> ElnGroupExperimentRole:
    abstract_role: AbstractElnExperimentRole = _parse_abstract_role(json_dct)
    group_id: int = json_dct.get('groupId')
    return ElnGroupExperimentRole(is_author=abstract_role.is_author, is_witness=abstract_role.is_witness,
                                  is_reviewer=abstract_role.is_reviewer, is_approver=abstract_role.is_approver,
                                  group_id=group_id)
