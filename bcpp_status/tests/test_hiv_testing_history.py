from django.test import tag
from edc_constants.constants import POS, NEG, YES, NO

from ..model_data import HivTestingHistory
from .values_test_case import ValuesTestCase


class TestHivTestingHistory(ValuesTestCase):

    def test_pos(self):
        """Asserts always picks last.
        """
        self.longitudinal_values = dict(
            first={
                'verbal_hiv_result': (NEG, 'CharField'),
                'has_tested': (NO, 'CharField'),
                'has_tested': (NO, 'CharField')},
            second={
                'verbal_hiv_result': (NEG, 'CharField'),
                'has_tested': (NO, 'CharField'),
                'has_tested': (NO, 'CharField')},
            third={
                'verbal_hiv_result': (POS, 'CharField'),
                'has_tested': (YES, 'CharField'),
                'has_tested': (YES, 'CharField')})
        self.reference_helper.create(
            HivTestingHistory.model, self.visits, self.longitudinal_values)
        values_obj = HivTestingHistory(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('third'))
        for key, value in self.longitudinal_values.get('third').items():
            self.assertEqual(value[0], values_obj.values.get(key))
