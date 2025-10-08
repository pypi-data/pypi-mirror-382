import unittest

from data_type_models import SampleModel
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, ReportColumn, RawReportTerm, RawTermOperation
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType


class PR51856Test(unittest.TestCase):
    def test_no_report_term_report(self):
        report_criteria = CustomReportCriteria([ReportColumn(
            SampleModel.DATA_TYPE_NAME, SampleModel.SAMPLEID__FIELD_NAME.field_name, FieldType.STRING)])
        CustomReportCriteria.from_json(report_criteria.to_json())

    def test_with_root_term_report(self):
        root_term = RawReportTerm(SampleModel.DATA_TYPE_NAME, SampleModel.SAMPLEID__FIELD_NAME.field_name, RawTermOperation.EQUAL_TO_OPERATOR, "12345")
        report_criteria = CustomReportCriteria([ReportColumn(
            SampleModel.DATA_TYPE_NAME, SampleModel.SAMPLEID__FIELD_NAME.field_name, FieldType.STRING)], root_term)
        test_criteria = CustomReportCriteria.from_json(report_criteria.to_json())
        test_root_term = test_criteria.root_term
        self.assertEqual(root_term, test_root_term)
