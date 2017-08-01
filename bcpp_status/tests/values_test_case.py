from dateutil.relativedelta import relativedelta
from django.test.testcases import TestCase

from edc_base.utils import get_utcnow

from .reference_test_helper import ReferenceTestHelper


class ValuesTestCase(TestCase):

    subject_identifier = '111111111'
    visits = dict(
        first=get_utcnow() - relativedelta(years=2),
        second=get_utcnow() - relativedelta(years=1),
        third=get_utcnow())
    reference_helper = ReferenceTestHelper(
        visit_model='bcpp_subject.subjectvisit',
        subject_identifier='111111111')
