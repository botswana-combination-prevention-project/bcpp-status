from arrow.arrow import Arrow
from faker import Faker
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase, tag

from edc_base.utils import get_utcnow
from edc_constants.constants import NEG, POS, UNK, YES, IND, NAIVE, NO
from edc_reference.tests import ReferenceTestHelper
from edc_reference import LongitudinalRefset, site_reference_configs

from ..status_helper import StatusHelper, DEFAULTER, ART_PRESCRIPTION, ON_ART
from .status_helper_test_mixin import StatusHelperTestMixin

MICROTUBE = 'Microtube'
T1 = 'T1'

fake = Faker()


class TestStatusHelper(StatusHelperTestMixin, TestCase):

    reference_helper_cls = ReferenceTestHelper
    visit_model = 'bcpp_subject.subjectvisit'
    reference_model = 'edc_reference.reference'

    def setUp(self):
        self.subject_identifier = '111111111'
        self.reference_helper = self.reference_helper_cls(
            visit_model='bcpp_subject.subjectvisit',
            subject_identifier=self.subject_identifier)

        report_datetime = Arrow.fromdatetime(
            datetime(2015, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=2), timepoint='T2')
        self.subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

    def test_final_hiv_status(self):
        self.prepare_art_status(
            visit=self.subject_visits[0], defaulter=True)
        status_helper = StatusHelper(visit=self.subject_visits[0])
        self.assertEqual(status_helper.final_hiv_status, POS)
        self.assertEqual(status_helper.final_arv_status, DEFAULTER)

    def test_final_hiv_status_1(self):
        self.prepare_art_status(
            visit=self.subject_visits[1], defaulter=True)
        status_helper = StatusHelper(visit=self.subject_visits[1])
        self.assertEqual(status_helper.final_hiv_status, POS)
        self.assertEqual(status_helper.final_arv_status, DEFAULTER)
        status_helper = StatusHelper(visit=self.subject_visits[2])
        self.assertEqual(status_helper.final_hiv_status, POS)
        self.assertEqual(status_helper.final_arv_status, DEFAULTER)

    def test_final_hiv_status_2(self):
        self.prepare_art_status(
            visit=self.subject_visits[2], defaulter=True)
        status_helper = StatusHelper(visit=self.subject_visits[2])
        self.assertEqual(status_helper.final_hiv_status, POS)
        self.assertEqual(status_helper.final_arv_status, DEFAULTER)

    def test_final_hiv_status_a(self):
        self.prepare_art_status(
            visit=self.subject_visits[2], defaulter=True)
        status_helper = StatusHelper(visit=self.subject_visits[0])
        self.assertEqual(status_helper.final_hiv_status, UNK)
        self.assertEqual(status_helper.final_arv_status, None)
        status_helper = StatusHelper(visit=self.subject_visits[1])
        self.assertEqual(status_helper.final_hiv_status, UNK)
        self.assertEqual(status_helper.final_arv_status, None)
