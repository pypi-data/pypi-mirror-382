# Emulates the Sapio Foundations accession service
from threading import RLock
from typing import Optional, Dict, Tuple, List

from sapiopylib.rest.AccessionService import AccessionDataFieldCriteriaPojo
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.utils.autopaging import QueryAllRecordsOfTypeAutoPager


class FoundationAccessionConfig:
    """
    This is the Sapio Foundations configuration for field accessioning.

    Deprecated. Use sapiopycommons new accession service utilities.
    """
    data_type_name: str
    data_field_name: str
    prefix: str
    suffix: str
    num_of_digits: Optional[int]
    start_number: Optional[int]

    def __init__(self, data_type_name: str, data_field_name: str,
                 prefix: Optional[str] = "", suffix: Optional[str] = "",
                 num_of_digits: Optional[int] = 6, start_number: Optional[int] = 1):
        if prefix is None:
            prefix = ""
        if suffix is None:
            suffix = ""
        if num_of_digits is None:
            num_of_digits = 6
        if start_number is None:
            start_number = 1
        self.data_type_name = data_type_name
        self.data_field_name = data_field_name
        self.prefix = prefix
        self.suffix = suffix
        self.num_of_digits = num_of_digits
        self.start_number = start_number

    def get_accessor_name(self) -> str:
        # PR-51537 sapiopylib: FoundationAccessionManager doesn't work properly as it wasn't using the same keys
        return (self.data_type_name + "." + self.data_field_name +
                "|" + "PREFIX_AND_SUFFIX" + "(" + self.prefix + "," + self.suffix + ")")

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, FoundationAccessionConfig):
            return False
        return (self.data_type_name, self.data_field_name) == (other.data_type_name, other.data_field_name)

    def __hash__(self):
        return hash((self.data_type_name, self.data_field_name))


class FoundationAccessionManager:
    """
    This manager will synchronize with Sapio Foundation accessioning logic.
    """
    user: SapioUser
    config_cache: Optional[Dict[Tuple[str, str], FoundationAccessionConfig]]
    lock: RLock

    def __init__(self, user: SapioUser):
        self.user = user
        self.config_cache = None
        self.lock = RLock()

    def invalidate(self) -> None:
        """
        Instruct the accession manager to invalidate the current LIMS data record config
        and re-retrieve next time it is needed.
        This should be called after any changes to the accession config records.
        """
        with self.lock:
            self.config_cache = None

    def _ensure_cache_loaded(self) -> None:
        """
        If the config cache is not loaded, load the cache now for all data types.
        """
        if self.config_cache is not None:
            return
        with self.lock:
            auto_pager = QueryAllRecordsOfTypeAutoPager('AccessionConfig', self.user)
            records = auto_pager.get_all_at_once()
            config_cache: Dict[Tuple[str, str], FoundationAccessionConfig] = {}
            for record in records:
                data_type: str = record.get_field_value('DataTypeField')
                data_field: str = record.get_field_value('DataFieldName')
                if not data_type or not data_field:
                    continue
                num_of_digits: Optional[int] = record.get_field_value('NumberOfDigits')
                start_number: Optional[int] = record.get_field_value('StartNumber')
                prefix: Optional[str] = record.get_field_value('PrefixField')
                suffix: Optional[str] = record.get_field_value('SuffixField')
                config = FoundationAccessionConfig(data_type, data_field, prefix, suffix, num_of_digits, start_number)
                config_cache[(data_type, data_field)] = config
            self.config_cache = config_cache

    @staticmethod
    def _parse_server_ids(server_ids: List[str], config: FoundationAccessionConfig) -> List[str]:
        """
        Convert server IDs with what the config format is.
        """
        if config.num_of_digits is None:
            return [config.prefix + x + config.suffix for x in server_ids]
        else:
            return [config.prefix + x.zfill(config.num_of_digits) + config.suffix for x in server_ids]

    def get_accession_with_config_list(self, data_type_name: str, data_field_name: str, num_of_ids: int) -> List[str]:
        """
        This method will return a list of Accessioned IDs using the LIMS data records of the type AccessionConfig to use
        the accession service. To control
        the specific accessioning parameters used, configure the AccessionConfigs in Exemplar Configurations to your
        Prefix, Suffix, Number of Digits preferences.
        By default, the number of digits it will accession for is 6

        Deprecated. Use sapiopycommons new accession service utilities.
        """
        self._ensure_cache_loaded()
        config: FoundationAccessionConfig
        with self.lock:
            if (data_type_name, data_field_name) in self.config_cache:
                config = self.config_cache[(data_type_name, data_field_name)]
            else:
                config = FoundationAccessionConfig(data_type_name, data_field_name)
        accession_service = DataMgmtServer.get_accession_manager(self.user)
        criteria = AccessionDataFieldCriteriaPojo(config.data_type_name, config.data_field_name,
                                                  config.get_accessor_name())
        criteria.initial_sequence_value = config.start_number
        criteria.suffix = config.suffix
        criteria.prefix = config.prefix
        server_ids = accession_service.accession_for_field(num_of_ids, criteria)
        return self._parse_server_ids(server_ids, config)
