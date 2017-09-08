from django.test import tag
from edc_constants.constants import NO, YES, NOT_APPLICABLE, DWTA

from ..model_data import HivCareAdherence
from .values_test_case import ValuesTestCase


class TestHivCareAdherence(ValuesTestCase):

    def setUp(self):
        self.longitudinal_values = dict(
            first={
                'arv_evidence': (NO, 'CharField'),
                'ever_taken_arv': (NO, 'CharField'),
                'on_arv': (NO, 'CharField')},
            second={
                'arv_evidence': (YES, 'CharField'),
                'ever_taken_arv': (YES, 'CharField'),
                'on_arv': (YES, 'CharField')},
            third={
                'arv_evidence': ('MAYBE', 'CharField'),
                'ever_taken_arv': ('MAYBE', 'CharField'),
                'on_arv': ('MAYBE', 'CharField')})

    def test_hivcareadherence_values(self):
        self.reference_helper.create(
            reference_name=HivCareAdherence.model,
            visits=self.visits, longitudinal_values=self.longitudinal_values)
        for visit_code in self.longitudinal_values:
            with self.subTest(visit_code=visit_code):
                values_obj = HivCareAdherence(
                    subject_identifier=self.subject_identifier,
                    report_datetime=self.visits.get(visit_code))
                for key, value in self.longitudinal_values.get(visit_code).items():
                    self.assertEqual(value[0], values_obj.values.get(key))

    def test_hivcareadherence_baseline(self):
        self.reference_helper.create(
            reference_name=HivCareAdherence.model,
            visits=self.visits, longitudinal_values=self.longitudinal_values)
        values_obj = HivCareAdherence(
            subject_identifier=self.subject_identifier,
            baseline=True)
        for key, value in self.longitudinal_values.get('first').items():
            self.assertEqual(value[0], values_obj.values.get(key))

    def test_hivcareadherence_values2(self):
        self.longitudinal_values.update(first={
            'arv_evidence': (NOT_APPLICABLE, 'CharField'),
            'ever_taken_arv': (DWTA, 'CharField'),
            'on_arv': (NOT_APPLICABLE, 'CharField')})
        self.reference_helper.create(
            reference_name=HivCareAdherence.model,
            visits=self.visits, longitudinal_values=self.longitudinal_values)
        values_obj = HivCareAdherence(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('first'))
        self.assertEqual(None, values_obj.values.get('arv_evidence'))
        self.assertEqual(NO, values_obj.values.get('ever_taken_arv'))
        self.assertEqual(None, values_obj.values.get('on_arv'))

    def test_hivcareadherence_values3(self):
        self.longitudinal_values.update(first={
            'arv_evidence': (NO, 'CharField'),
            'ever_taken_arv': (NO, 'CharField'),
            'on_arv': (DWTA, 'CharField')})
        self.reference_helper.create(
            reference_name=HivCareAdherence.model,
            visits=self.visits, longitudinal_values=self.longitudinal_values)
        values_obj = HivCareAdherence(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('first'))
        self.assertEqual(NO, values_obj.values.get('on_arv'))
