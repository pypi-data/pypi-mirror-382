import unittest
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType

'''
I'm only going to test group auth and no oauth2 since dereck voluenteered t otest oauth2.
'''
class TestFR52452(unittest.TestCase):

    def test_regression(self):
        """
        In here we test with no group auth at all.
        """
        user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                         guid="ae4e92e1-34c6-4336-8d80-7f6804d3e51c",
                         username="yqiao_api", password="Password1!")
        additional_data = user.session_additional_data
        print("Regression Case Login Group: " + additional_data.current_group_name)

    def test_group_log(self):
        """
        In here we will be testing user login session for different groups.
        """
        user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                         guid="ae4e92e1-34c6-4336-8d80-7f6804d3e51c", group_name="Admin",
                         username="yqiao_api", password="Password1!")
        additional_data = user.session_additional_data
        self.assertEqual("Admin", additional_data.current_group_name)

        user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                         guid="ae4e92e1-34c6-4336-8d80-7f6804d3e51c", group_name="Seamless ELN",
                         username="yqiao_api", password="Password1!")
        additional_data = user.session_additional_data
        self.assertEqual("Seamless ELN", additional_data.current_group_name)

    def test_base_type_eval(self):
        self.assertEqual(ElnBaseDataType.get_base_type("ElnExperiment"), ElnBaseDataType.EXPERIMENT)
        self.assertEqual(ElnBaseDataType.get_base_type("ElnExperimentDetail"), ElnBaseDataType.EXPERIMENT_DETAIL)
        self.assertEqual(ElnBaseDataType.get_base_type("ElnSampleDetail"), ElnBaseDataType.SAMPLE_DETAIL)
        self.assertEqual(ElnBaseDataType.get_base_type("ElnExperiment_12345"), ElnBaseDataType.EXPERIMENT)
        self.assertEqual(ElnBaseDataType.get_base_type("ElnExperimentDetail_12345"), ElnBaseDataType.EXPERIMENT_DETAIL)
        self.assertEqual(ElnBaseDataType.get_base_type("ElnSampleDetail_12345"), ElnBaseDataType.SAMPLE_DETAIL)
