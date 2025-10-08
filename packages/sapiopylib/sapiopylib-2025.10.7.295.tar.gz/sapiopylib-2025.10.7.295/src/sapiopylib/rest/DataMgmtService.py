from sapiopylib.rest.AccessionService import AccessionManager
from sapiopylib.rest.ClientCallbackService import ClientCallback
from sapiopylib.rest.CustomReportService import CustomReportManager
from sapiopylib.rest.DashboardManager import DashboardManager
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.DataService import DataManager
from sapiopylib.rest.DataTypeService import DataTypeManager
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.GroupManagerService import VeloxGroupManager
from sapiopylib.rest.MessengerService import SapioMessenger
from sapiopylib.rest.PicklistService import PicklistManager
from sapiopylib.rest.ReportManager import ReportManager
from sapiopylib.rest.SesssionManagerService import SessionManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.UserManagerService import VeloxUserManager


class DataMgmtServer:
    """
    Contains all service points for the current API.
    """

    @staticmethod
    def get_dashboard_manager(user: SapioUser) -> DashboardManager:
        """
        Get the dashboard manager service for the current context.

        :param user The user auth context.
        """
        return DashboardManager(user)

    @staticmethod
    def get_data_record_manager(user: SapioUser) -> DataRecordManager:
        """
        Get the data record manager service for the current context, which allows for the creation, reading, updating,
        and deleting of data records.

        :param user The user auth context.
        """
        return DataRecordManager(user)

    @staticmethod
    def get_accession_manager(user: SapioUser) -> AccessionManager:
        """
        Get the accession service manager for the current context, which allows for the accessioning of unique values.

        :param user: The user auth context.
        """
        return AccessionManager(user)

    @staticmethod
    def get_custom_report_manager(user: SapioUser) -> CustomReportManager:
        """
        Get the custom report manager for the current context, which allows for advanced searching of data records.

        :param user: The user auth context.
        """
        return CustomReportManager(user)

    @staticmethod
    def get_eln_manager(user: SapioUser) -> ElnManager:
        """
        Get the ELN (Notebook Experiment) manager for the current context, which allows for the creation and
        manipulation of ELN experiments.

        :param user: The user auth context.
        """
        return ElnManager(user)

    @staticmethod
    def get_picklist_manager(user: SapioUser) -> PicklistManager:
        """
        Get the picklist manager for the current context, which allows for the creation, reading, and updating of pick
        lists defined in the system.

        :param user: The user auth context.
        """
        return PicklistManager(user)

    @staticmethod
    def get_data_type_manager(user: SapioUser) -> DataTypeManager:
        """
        Get the data type manager for the current context, which allows for the querying of data type definitions from
        the system.

        :param user: The user auth context.
        """
        return DataTypeManager(user)

    @staticmethod
    def get_user_manager(user: SapioUser) -> VeloxUserManager:
        """
        Get the user manager that contains info about users in the system.

        :param user: The user auth context.
        """
        return VeloxUserManager(user)

    @staticmethod
    def get_group_manager(user: SapioUser) -> VeloxGroupManager:
        """
        Get the group manager that contains info about groups and user memberships into groups.

        :param user: The user auth context.
        """
        return VeloxGroupManager(user)

    @staticmethod
    def get_messenger(user: SapioUser) -> SapioMessenger:
        """
        Get the Sapio messanger that allows for the sending of emails and messages from the system.

        :param user: The user auth context.
        """
        return SapioMessenger(user)

    @staticmethod
    def get_data_manager(user: SapioUser) -> DataManager:
        """
        Get the data manager that helps import/export data to and from files.

        :param user: The user auth context.
        """
        return DataManager(user)

    @staticmethod
    def get_report_manager(user: SapioUser) -> ReportManager:
        """
        get the Sapio Report Manager that implements the report manager (addon) features.

        :param user: The user auth context.
        """
        return ReportManager(user)

    @staticmethod
    def get_client_callback(user: SapioUser) -> ClientCallback:
        """
        Get the client callback to interact with the human end user.
        """
        return ClientCallback(user)

    @staticmethod
    def get_session_manager(user: SapioUser) -> SessionManager:
        """
        Get the session manager to manage user sessions in the Sapio app.
        """
        return SessionManager(user)
