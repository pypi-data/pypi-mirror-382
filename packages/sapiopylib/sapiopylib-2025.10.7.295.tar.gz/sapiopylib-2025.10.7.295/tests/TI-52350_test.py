import unittest

from data_type_models import DirectoryModel
from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, ReportColumn
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.pojo.eln.ElnExperiment import TemplateExperimentQueryPojo, TemplateExperiment

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
report_man = DataMgmtServer.get_custom_report_manager(user)
eln_man = DataMgmtServer.get_eln_manager(user)

class TestTI52350(unittest.TestCase):
    def test_group_by_column(self):
        report_criteria = CustomReportCriteria(
            [ReportColumn(DirectoryModel.DATA_TYPE_NAME, DirectoryModel.DIRECTORYNAME__FIELD_NAME.field_name,
                          FieldType.STRING, group_by=True),
             ReportColumn(DirectoryModel.DATA_TYPE_NAME, "RecordId", FieldType.LONG, group_by=False)])
        report = report_man.run_custom_report(report_criteria)
        self.assertTrue(report.column_list[0].group_by)
        self.assertFalse(report.column_list[1].group_by)

    def test_template_info(self):
        info_list: list[TemplateExperiment] = eln_man.get_template_experiment_list(TemplateExperimentQueryPojo())
        for info in info_list:
            self.assertTrue(hasattr(info, "hide_embedded_chat"))
            print(info.template_name + ": " + str(info.hide_embedded_chat))
