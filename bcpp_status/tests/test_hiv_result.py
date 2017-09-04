from dateutil.relativedelta import relativedelta
from django.test import tag
from edc_base.utils import get_utcnow
from edc_constants.constants import POS, NEG, DECLINED

from ..model_data import HivResult
from .values_test_case import ValuesTestCase


class TestHivResult(ValuesTestCase):

    def test_pos(self):
        """Asserts always picks the first POS.
        """
        self.longitudinal_values = dict(
            first={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=4), 'DateTimeField')},
            second={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=3), 'DateTimeField')},
            third={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')})
        self.reference_helper.create(
            HivResult.model, self.visits, self.longitudinal_values)
        for visit_code in self.longitudinal_values:
            with self.subTest(visit_code=visit_code):
                values_obj = HivResult(
                    subject_identifier=self.subject_identifier,
                    report_datetime=self.visits.get(visit_code))
                for key, value in self.longitudinal_values.get('first').items():
                    self.assertEqual(value[0], values_obj.values.get(key))

    def test_pos2(self):
        """Asserts always picks the first POS.
        """
        self.longitudinal_values = dict(
            first={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=4), 'DateTimeField')},
            second={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=3), 'DateTimeField')},
            third={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')})
        self.reference_helper.create(
            HivResult.model, self.visits, self.longitudinal_values)
        # first is NEG
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('first'))
        for key, value in self.longitudinal_values.get('first').items():
            self.assertEqual(value[0], values_obj.values.get(key))
        # second is POS
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('second'))
        for key, value in self.longitudinal_values.get('second').items():
            self.assertEqual(value[0], values_obj.values.get(key))
        # third takes second POS (e.g. the first POS)
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('third'))
        for key, value in self.longitudinal_values.get('second').items():
            self.assertEqual(value[0], values_obj.values.get(key))

    def test_pos3(self):
        """Asserts always picks the first POS.
        """
        self.longitudinal_values = dict(
            first={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=4), 'DateTimeField')},
            second={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=3), 'DateTimeField')},
            third={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')})
        self.reference_helper.create(
            HivResult.model, self.visits, self.longitudinal_values)
        # first is POS
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('first'))
        for key, value in self.longitudinal_values.get('first').items():
            self.assertEqual(value[0], values_obj.values.get(key))
        # second takes first  POS
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('second'))
        for key, value in self.longitudinal_values.get('first').items():
            self.assertEqual(value[0], values_obj.values.get(key))
        # third takes first  POS
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('third'))
        for key, value in self.longitudinal_values.get('first').items():
            self.assertEqual(value[0], values_obj.values.get(key))

    def test_declined1(self):
        """Asserts always picks the first POS.
        """
        self.longitudinal_values = dict(
            first={
                'hiv_result': (DECLINED, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=4), 'DateTimeField')},
            second={
                'hiv_result': (DECLINED, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=3), 'DateTimeField')},
            third={
                'hiv_result': (DECLINED, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')})
        self.reference_helper.create(
            HivResult.model, self.visits, self.longitudinal_values)
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('first'))
        for key, value in self.longitudinal_values.get('first').items():
            self.assertEqual(value[0], values_obj.values.get(key))

    def test_declined2(self):
        """Asserts always picks the first POS.
        """
        self.longitudinal_values = dict(
            first={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=4), 'DateTimeField')},
            second={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=3), 'DateTimeField')},
            third={
                'hiv_result': (DECLINED, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')})
        self.reference_helper.create(
            HivResult.model, self.visits, self.longitudinal_values)
        # first is NEG
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('first'))
        for key, value in self.longitudinal_values.get('first').items():
            self.assertEqual(value[0], values_obj.values.get(key))
        # second is NEG
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('second'))
        for key, value in self.longitudinal_values.get('second').items():
            self.assertEqual(value[0], values_obj.values.get(key))
        # third is DECLINED
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('third'))
        for key, value in self.longitudinal_values.get('third').items():
            self.assertEqual(value[0], values_obj.values.get(key))

    def test_baseline(self):
        """Asserts baseline picks first result.
        """
        self.longitudinal_values = dict(
            first={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=4), 'DateTimeField')},
            second={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=3), 'DateTimeField')},
            third={
                'hiv_result': (DECLINED, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')})
        self.reference_helper.create(
            HivResult.model, self.visits, self.longitudinal_values)
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            baseline=True)
        for key, value in self.longitudinal_values.get('first').items():
            self.assertEqual(value[0], values_obj.values.get(key))

    def test_ordering(self):
        """Asserts picks first POS.
        """
        self.longitudinal_values = dict(
            first={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=1), 'DateTimeField')},
            second={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')},
            third={
                'hiv_result': (POS, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=1), 'DateTimeField')})
        self.reference_helper.create(
            HivResult.model, self.visits, self.longitudinal_values)
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('third'))
        for key, value in self.longitudinal_values.get('second').items():
            self.assertEqual(value[0], values_obj.values.get(key))

    def test_ordering_neg(self):
        """Asserts picks last NEG.
        """
        self.longitudinal_values = dict(
            first={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=1), 'DateTimeField')},
            second={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')},
            third={
                'hiv_result': (NEG, 'CharField'),
                'hiv_result_datetime': (
                    get_utcnow() - relativedelta(years=1), 'DateTimeField')})
        self.reference_helper.create(
            HivResult.model, self.visits, self.longitudinal_values)
        values_obj = HivResult(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('third'))
        for key, value in self.longitudinal_values.get('third').items():
            self.assertEqual(value[0], values_obj.values.get(key))
