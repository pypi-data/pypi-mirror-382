from typing import Optional, List, Dict, Any


class PickListConfig:
    """
    Represents a picklist configuration data.
    """
    picklist_id: int
    pick_list_name: str
    description: Optional[str]
    restricted: bool
    entry_list: Optional[List[str]]

    def __init__(self, picklist_id: int, pick_list_name: str, restricted: bool,
                 entry_list: Optional[List[str]] = None, description: Optional[str] = None):
        self.picklist_id = picklist_id
        self.pick_list_name = pick_list_name
        self.restricted = restricted
        self.entry_list = entry_list
        self.description = description

    def to_json(self) -> Dict[str, Any]:
        return {
            'id': self.picklist_id,
            'pickListName': self.pick_list_name,
            'description': self.description,
            'restricted': self.restricted,
            'entryList': self.entry_list
        }

    def __eq__(self, other):
        if not isinstance(other, PickListConfig):
            return False
        return other.picklist_id == self.picklist_id and other.pick_list_name == self.pick_list_name

    def __hash__(self):
        return hash((self.picklist_id, self.pick_list_name))

    def __str__(self):
        ret = self.pick_list_name
        if self.restricted:
            ret += ' [Hidden]'
        if self.entry_list is not None:
            ret += ': ' + ','.join(self.entry_list)
        return ret


class PicklistParser:
    @staticmethod
    def parse_picklist_config(json_dct: Dict[str, Any]) -> PickListConfig:
        pick_list_id: int = json_dct.get('id')
        pick_list_name: str = json_dct.get('pickListName')
        description: Optional[str] = json_dct.get('description')
        restricted: bool = json_dct.get('restricted')
        entry_list: Optional[List[str]] = json_dct.get('entryList')

        return PickListConfig(pick_list_id, pick_list_name,
                              restricted=restricted, entry_list=entry_list, description=description)


# Alias Classes
PicklistConfig: type = PickListConfig