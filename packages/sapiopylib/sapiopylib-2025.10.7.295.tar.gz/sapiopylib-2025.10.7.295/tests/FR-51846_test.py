import unittest

from sapiopylib.rest.pojo.reportbuilder.VeloxReportBuilder import ReportDataContext

from sapiopylib.rest.utils.recordmodel.properties import Child

from data_type_models import SampleModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

from sapiopylib.rest.DataMgmtService import DataMgmtServer

from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
report_man = DataMgmtServer.get_report_manager(user)
rec_man = RecordModelManager(user)
inst_man = rec_man.instance_manager

class FR51846Test(unittest.TestCase):
    def test_template_info_list(self):
        info_list = report_man.get_report_template_info_list()
        self.assertTrue(info_list)
        self.assertTrue([x for x in info_list if x.template_id == 'Test Template'])

    def test_entry_info_list(self):
        entry_info_list = report_man.get_report_entry_info_list('Test Template')
        self.assertTrue(entry_info_list)

    def test_report_template_maker(self):
        all_samples = []
        children_samples = []
        master_sample = inst_man.add_new_record_of_type(SampleModel)
        master_sample.set_Volume_field(500)
        all_samples.append(master_sample)
        for i in range(5):
            child_sample: SampleModel = master_sample.add(Child.create(SampleModel))
            child_sample.set_Volume_field(i)
            all_samples.append(child_sample)
            children_samples.append(child_sample)
        rec_man.store_and_commit()
        data_context = report_man.initialize_report_data_context(all_samples, 'Test Template')
        self.assertTrue(data_context.field_map_by_record_id_by_type)
        self.assertTrue(data_context.entry_data_context_map)
        data_context.entry_data_context_map['Form1'].set_records([master_sample])
        data_context.entry_data_context_map['Table1'].set_records(children_samples)
        report_man.generate_report_pdf('Test Template', 'Attachment', data_context)
