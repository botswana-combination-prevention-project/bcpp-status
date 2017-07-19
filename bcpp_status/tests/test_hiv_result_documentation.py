from dateutil.relativedelta import relativedelta
from django.test import tag

from edc_base.utils import get_utcnow
from edc_constants.constants import POS

from ..model_values import HivResultDocumentation
from .values_test_case import ValuesTestCase


class TestHivResultDocumentation(ValuesTestCase):

    def test_pos(self):
        """Asserts always picks the first POS.
        """
        self.longitudinal_values = dict(
            first={
                'result_recorded': (POS, 'CharField'),
                'result_doc_type': ('doc1', 'CharField'),
                'result_date': (
                    get_utcnow() - relativedelta(years=1), 'DateTimeField')},
            second={
                'result_recorded': (POS, 'CharField'),
                'result_doc_type': ('doc2', 'CharField'),
                'result_date': (
                    get_utcnow() - relativedelta(years=3), 'DateTimeField')},
            third={
                'result_recorded': (POS, 'CharField'),
                'result_doc_type': ('doc3', 'CharField'),
                'result_date': (
                    get_utcnow() - relativedelta(years=2), 'DateTimeField')})
        self.reference_helper.create(
            HivResultDocumentation.model, self.visits, self.longitudinal_values)
        values_obj = HivResultDocumentation(
            subject_identifier=self.subject_identifier,
            report_datetime=self.visits.get('third'))
        for key, value in self.longitudinal_values.get('second').items():
            self.assertEqual(value[0], values_obj.values.get(key))
