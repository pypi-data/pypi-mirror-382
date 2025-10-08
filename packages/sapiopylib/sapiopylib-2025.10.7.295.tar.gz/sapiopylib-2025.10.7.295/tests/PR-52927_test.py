import unittest

from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, RawReportTerm, CompositeReportTerm, \
    RawTermOperation, ReportColumn, FieldCompareReportTerm, ExplicitJoinDefinition, CompositeTermOperation

from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxDateRangeFieldDefinition, FieldType

from sapiopylib.rest.utils.FormBuilder import FormBuilder

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
report_man = DataMgmtServer.get_custom_report_manager(user)

class PR52780Test(unittest.TestCase):

    def test_report_join_criteria_args(self):
        sample_term = RawReportTerm('Sample', 'SampleId', RawTermOperation.EQUAL_TO_OPERATOR, '00001')
        receipt_term = RawReportTerm('SampleReceipt', 'RecordId', RawTermOperation.GREATER_THAN_OPERATOR, '0')
        root_term = CompositeReportTerm(sample_term, CompositeTermOperation.AND_OPERATOR, receipt_term)


        column_list = [ReportColumn('Sample', 'SampleId', FieldType.STRING), ReportColumn('SampleReceipt', 'SampleReceivedRejected', FieldType.PICKLIST),
                       ReportColumn('StorageUnit', 'OccupiedCount', FieldType.LONG), ReportColumn('StorageUnit', 'StorageUnitCapacity', FieldType.LONG)]

        storage_join_term = FieldCompareReportTerm('Sample', 'StorageLocationBarcode', RawTermOperation.EQUAL_TO_OPERATOR, 'StorageUnit', 'StorageUnitId')

        request = CustomReportCriteria(column_list=column_list, root_term=root_term, page_size= 10, page_number=0,
                                       join_list=[ExplicitJoinDefinition('StorageUnit', storage_join_term)])

        report = report_man.run_custom_report(request)
        self.assertEquals(request.join_list, report.join_list)
        self.assertEquals(request.page_number, report.page_number)
        self.assertEquals(request.page_size, report.page_size)
        self.assertEquals(request.column_list, report.column_list)
        self.assertEquals(request.root_term, report.root_term)
