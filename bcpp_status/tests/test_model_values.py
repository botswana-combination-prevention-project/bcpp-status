from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_reference.tests import ReferenceTestHelper

from ..model_data import ModelData


class TestModelValues(TestCase):

    reference_helper_cls = ReferenceTestHelper

    def setUp(self):
        self.subject_identifier = '111111111'
        self.reference_helper = self.reference_helper_cls(
            visit_model='bcpp_subject.subjectvisit',
            subject_identifier=self.subject_identifier)

    def test_assert_attrs_exist(self):
        self.reference_helper.create_visit(
            report_datetime=get_utcnow(), timepoint='first')
        model_data = ModelData(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            baseline=True)
        attrs = {
            'arv_evidence': None,
            'elisa_hiv_result': None,
            'elisa_hiv_result_date': None,
            'ever_taken_arv': None,
            'has_tested': None,
            'on_arv': None,
            'other_record': None,
            'recorded_hiv_result': None,
            'recorded_hiv_result_date': None,
            'result_recorded': None,
            'result_recorded_date': None,
            'result_recorded_document': None,
            'self_reported_result': None,
            'today_hiv_result': None,
            'today_hiv_result_date': None,
        }
        for attr in attrs:
            self.assertIn(attr, model_data.values)
