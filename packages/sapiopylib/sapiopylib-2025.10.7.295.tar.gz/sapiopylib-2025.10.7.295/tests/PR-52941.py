import unittest

from data_type_models import SampleModel


class PR52914Test(unittest.TestCase):
    def test_hash_wrapper_field(self):
        self.assertTrue(hash(SampleModel.SAMPLEID__FIELD_NAME))