from __future__ import annotations

from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import *


class CustomReportManager:
    """
    A suite to run a simple or complex query with conditions across a linage of records.
    """

    user: SapioUser
    __instances: WeakValueDictionary[SapioUser, CustomReportManager] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, user: SapioUser):
        """
        Observes singleton pattern per record model manager object.

        :param user: The user that will make the webservice request to the application.
        """
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, user: SapioUser):
        """
        Obtain a custom report manager to run advanced searches for a user context.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def run_system_report_by_name(self, system_report_name: str,
                                  page_size: Optional[int] = None, page_number: Optional[int] = None) -> CustomReport | None:
        """
        Given the name of a predefined search in the system, run it and return the results.

        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.

        :param system_report_name: The system report name to search for. This report must be defined as a predefined
            search in the data designer. Saved searched created by users will not function here.
        :param page_size: The page size of this report. If this is greater than the license limit, it will be limited
            by the license on request.
        :param page_number: The page number of this report.
        :return: The report, unless it does not exist. If it does not exist, then None is returned.
        """
        sub_path = self.user.build_url(['report', 'runSystemReportByName', system_report_name])
        params = dict()
        if page_size is not None:
            params['pageSize'] = page_size
        if page_number is not None:
            params['pageNumber'] = page_number
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        if response.status_code == 204:
            return None
        json_dct = response.json()
        return CustomReport.from_json(json_dct)

    def run_custom_report(self, custom_report_request: CustomReportCriteria) -> CustomReport:
        """
        Given the criteria of a custom report, run it and return the results.

        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.

        :param custom_report_request: The custom report request object containing all attributes about the request.
        :return: The report results for the given search criteria.
        """
        sub_path = self.user.build_url(['report', 'runCustomReport'])
        payload = custom_report_request.to_json()
        response = self.user.post(sub_path, payload=payload)
        self.user.raise_for_status(response)
        json_dct = response.json()
        return CustomReport.from_json(json_dct)

    def run_quick_report(self, report_term: RawReportTerm,
                         page_size: Optional[int] = None, page_number: Optional[int] = None) -> CustomReport:
        """
        Given a singular term of a custom report, run it and return the results.

        :param report_term: A singular custom report term to search on.
        :param page_size: The page size of this report. If this is greater than the license limit, it will be limited
            by the license on request.
        :param page_number: The page number of this report.
        :return: The report results for the given search criteria.
        """
        sub_path = self.user.build_url(['report', 'runQuickReport'])
        payload = report_term.to_json()
        params = dict()
        if page_size is not None:
            params['pageSize'] = page_size
        if page_number is not None:
            params['pageNumber'] = page_number
        response = self.user.post(sub_path, params=params, payload=payload)
        self.user.raise_for_status(response)
        json_dct = response.json()
        return CustomReport.from_json(json_dct)
