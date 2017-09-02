from faker import Faker
from datetime import date
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import NEG, POS, UNK, YES, NAIVE
from edc_reference.tests import ReferenceTestHelper

from ..status_helper import StatusHelper
from ..models import StatusHistory

fake = Faker()


class TestStatusHistory(TestCase):

    reference_helper_cls = ReferenceTestHelper
    visit_model = 'bcpp_subject.subjectvisit'
    reference_model = 'edc_reference.reference'

    def setUp(self):
        self.subject_identifier = '111111111'
        self.reference_helper = self.reference_helper_cls(
            visit_model='bcpp_subject.subjectvisit',
            subject_identifier=self.subject_identifier)
        self.model_values = {
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

    def test_updates(self):
        report_datetime = get_utcnow()
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='bhs')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='bhs',
            hiv_result=POS,
            hiv_result_date=date(2016, 1, 7))

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='bhs',
            recorded_hiv_result=NEG,
            hiv_test_date=date(2013, 5, 7))

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='bhs',
            other_record=UNK,
            has_tested=YES,
            verbal_hiv_result=NEG)

        status_helper = StatusHelper(
            subject_identifier=self.subject_identifier,
            model_values=self.model_values,
            update_history=True)

        self.assertGreater(StatusHistory.objects.all().count(), 0)

        obj = StatusHistory.objects.get(
            subject_identifier=status_helper.subject_identifier)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_arv_status, NAIVE)
