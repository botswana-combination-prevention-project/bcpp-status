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
from bcpp_status.status_db_helper import StatusDbHelper

MICROTUBE = 'Microtube'
T1 = 'T1'

fake = Faker()


class TestStatusHelper(TestCase):

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

    def test(self):
        self.assertIn('hiv_result', site_reference_configs.get_fields(
            'bcpp_subject.hivresult'))
        self.assertIn('arv_evidence', site_reference_configs.get_fields(
            'bcpp_subject.HivCareAdherence'))

    def test_visit(self):
        """Assert picks up the correct visit.
        """
        report_datetime = get_utcnow()

        self.reference_helper.create_visit(
            report_datetime=report_datetime - relativedelta(years=1), timepoint='bhs')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='ahs')

        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        status_helper = StatusHelper(
            visit=subject_visits[0], update_history=True)
        self.assertEqual(status_helper.subject_visit, subject_visits[0])

        # from StatusDbHelper
        status_helper = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(status_helper.subject_visit, subject_visits[0])

        status_helper = StatusHelper(
            visit=subject_visits[1], update_history=True)
        self.assertEqual(status_helper.subject_visit, subject_visits[1])

        # from StatusDbHelper
        status_helper = StatusDbHelper(visit=subject_visits[1])
        self.assertEqual(status_helper.subject_visit, subject_visits[1])

    def test_init_with_data(self):
        report_datetime = get_utcnow()

        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='bhs')

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='hivcareadherence', visit_code='bhs',
            arv_evidence=(YES, 'CharField'),
            on_arv=(YES, 'CharField'),
            ever_taken_arv=(YES, 'CharField'))

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='hivtestinghistory', visit_code='bhs',
            verbal_hiv_result=(POS, 'CharField'),
            has_tested=(YES, 'CharField'),
            other_record=(YES, 'CharField'),
        )

        # elisahivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='elisahivresult', visit_code='bhs',
            hiv_result=(POS, 'CharField'),
            hiv_result_datetime=(get_utcnow(), 'DateTimeField'))

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='hivresultdocumentation', visit_code='bhs',
            result_recorded=(POS, 'CharField'),
            result_date=(get_utcnow(), 'DateTimeField'),
            result_doc_type=(YES, 'CharField'))

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='hivtestreview', visit_code='bhs',
            recorded_hiv_result=(POS, 'CharField'),
            hiv_test_date=(get_utcnow(), 'DateTimeField'),
            result_doc_type=(YES, 'CharField'))

        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        self.assertTrue(StatusHelper(
            visit=subject_visits[0], update_history=True))

        self.assertTrue(StatusDbHelper(visit=subject_visits[0]))

    def test_init_with_data_and_db_helper_creates(self):
        report_datetime = get_utcnow()

        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='bhs')

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='hivcareadherence', visit_code='bhs',
            arv_evidence=(YES, 'CharField'),
            on_arv=(YES, 'CharField'),
            ever_taken_arv=(YES, 'CharField'))

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='hivtestinghistory', visit_code='bhs',
            verbal_hiv_result=(POS, 'CharField'),
            has_tested=(YES, 'CharField'),
            other_record=(YES, 'CharField'),
        )

        # elisahivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='elisahivresult', visit_code='bhs',
            hiv_result=(POS, 'CharField'),
            hiv_result_datetime=(get_utcnow(), 'DateTimeField'))

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='hivresultdocumentation', visit_code='bhs',
            result_recorded=(POS, 'CharField'),
            result_date=(get_utcnow(), 'DateTimeField'),
            result_doc_type=(YES, 'CharField'))

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime, model='hivtestreview', visit_code='bhs',
            recorded_hiv_result=(POS, 'CharField'),
            hiv_test_date=(get_utcnow(), 'DateTimeField'),
            result_doc_type=(YES, 'CharField'))

        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        self.assertTrue(StatusHelper(visit=subject_visits[0]))
        self.assertTrue(StatusDbHelper(visit=subject_visits[0]))

    def test_assert_baseline_pos(self):
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
            model_values=self.model_values, update_history=True)
        self.assertEqual(status_helper.final_hiv_status, POS)
        self.assertEqual(status_helper.final_arv_status, NAIVE)
        self.assertEqual(status_helper.prev_result_known, YES)
        self.assertEqual(status_helper.prev_result, NEG)

        status_helper = StatusDbHelper(
            subject_identifier=self.subject_identifier)
        self.assertEqual(status_helper.final_hiv_status, POS)
        self.assertEqual(status_helper.final_arv_status, NAIVE)
        self.assertEqual(status_helper.prev_result_known, YES)
        self.assertEqual(status_helper.prev_result, NEG)

    def test1(self):
        report_datetime = get_utcnow()

        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='subjectrequisition',
            visit_code='T0',
            panel_name=MICROTUBE,
            is_drawn=YES)

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=UNK,
            has_tested=YES,
            verbal_hiv_result=NEG)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=(report_datetime - relativedelta(days=10)).date())

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # Create a year 2 subject visit.
        report_datetime = report_datetime + timedelta(hours=1)
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='subjectrequisition',
            visit_code='T1',
            panel_name=MICROTUBE,
            is_drawn=YES)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T1',
            other_record=UNK,
            has_tested=YES,
            verbal_hiv_result=POS)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivcareadherence',
            visit_code='T1',
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=NO)

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T1',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        obj = StatusHelper(visit=subject_visits[1], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_arv_status, NAIVE)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

        obj = StatusDbHelper(visit=subject_visits[1])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_arv_status, NAIVE)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

    def test_final_hiv_status_date(self):
        """Assert date is today's hiv result date."""
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertIsNone(obj.prev_result_known)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertIsNone(obj.prev_result_known)

    def test_final_hiv_status_date2(self):
        """Assert date is today's hiv result date."""
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='subjectrequisition',
            visit_code='T0',
            panel_name=MICROTUBE,
            is_drawn=YES)

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=POS)

        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_known)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_known)

    def test_final_hiv_status_date1(self):
        """Assert date comes from result_recorded_date for
        recorded_hiv_result NEG and DEFAULTER .
        """
        self.model_values.update(
            recorded_hiv_result=NEG,
            recorded_hiv_result_date=date(2013, 5, 6),
            result_recorded=POS,
            result_recorded_date=date(2013, 5, 7),
            ever_taken_arv=NO,
            on_arv=NO,
            result_recorded_document=ART_PRESCRIPTION)
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + timedelta(days=365), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=Arrow.fromdate(date(2013, 5, 7)).date())

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=POS,
            result_date=Arrow.fromdate(date(2013, 5, 7)).date(),
            result_doc_type=ART_PRESCRIPTION)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivcareadherence',
            visit_code='T0',
            ever_taken_arv=NO,
            on_arv=NO)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_arv_status, DEFAULTER)
        self.assertEqual(obj.final_hiv_status_date, date(2013, 5, 7))
        self.assertEqual(obj.prev_result_date, date(2013, 5, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_arv_status, DEFAULTER)
        self.assertEqual(obj.final_hiv_status_date, date(2013, 5, 7))
        self.assertEqual(obj.prev_result_date, date(2013, 5, 7))

    def test_final_hiv_status_date12(self):
        """Assert date comes from result_recorded_date for
        recorded_hiv_result NEG and DEFAULTER .
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + timedelta(days=365), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        self.reference_helper.create_for_model(
            report_datetime=subject_visits[0].report_datetime,
            model='subjectrequisition',
            visit_code='T0',
            panel_name=MICROTUBE,
            is_drawn=YES)

        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='subjectrequisition',
            visit_code='T1',
            panel_name=MICROTUBE,
            is_drawn=YES)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=NEG)

        hiv_test_date = Arrow.fromdatetime(
            subject_visits[0].report_datetime - relativedelta(days=10)).date()

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=hiv_test_date)

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        report_datetime + timedelta(hours=10)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivtestinghistory',
            visit_code='T1',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=POS)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivcareadherence',
            visit_code='T1',
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=YES)

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivresult',
            visit_code='T1',
            hiv_result=POS,
            hiv_result_datetime=subject_visits[1].report_datetime)

        obj = StatusHelper(visit=subject_visits[1], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2017, 1, 6))
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2016, 1, 7))
        self.assertEqual(obj.final_arv_status, DEFAULTER)

        obj = StatusDbHelper(visit=subject_visits[1])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2017, 1, 6))
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2016, 1, 7))
        self.assertEqual(obj.final_arv_status, DEFAULTER)

    def test_prev_result_pos(self):
        """Assert prev_result POS taken from recorded_hiv_result
        /recorded_hiv_result_date.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + timedelta(days=365), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[0].report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=Arrow.fromdatetime(datetime(2016, 1, 7)).datetime)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date,
                         Arrow.fromdate(date(2015, 1, 7)).date())
        self.assertEqual(obj.prev_result_known, YES)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date,
                         Arrow.fromdate(date(2015, 1, 7)).date())
        self.assertEqual(obj.prev_result_known, YES)

    def test_prev_result_pos1(self):
        """Assert prev_result POS taken from recorded_hiv_result
        /recorded_hiv_result_date.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=POS)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=(report_datetime - relativedelta(days=10)).date())

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_known, YES)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_known, YES)

    def test_first_pos_date(self):
        """Assert uses recorded_hiv_result_date as final date since
        this is the date first POS.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=Arrow.fromdate(date(2016, 1, 7)).datetime)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

    def test_first_pos_date1(self):
        """Assert prev_result POS taken from recorded_hiv_result
        /recorded_hiv_result_date.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=POS)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=Arrow.fromdatetime(
                report_datetime - relativedelta(days=10)).date())

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=Arrow.fromdate(date(2016, 1, 7)).datetime)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_known, YES)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_known, YES)

    def test_prev_result_neg(self):
        """Assert prev_result NEG from recorded_hiv_result.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_neg1(self):
        """Assert prev_result NEG from recorded_hiv_result.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=NEG)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

    def test_prev_result_pos2(self):
        """Assert prev_result POS if recorded_hiv_result,
        result_recorded are discordant.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=POS,
            result_date=Arrow.fromdate(date(2014, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2014, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2014, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2014, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2014, 1, 7))

    def test_prev_result_pos21(self):
        """Assert prev_result POS if recorded_hiv_result,
        result_recorded are discordant.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=POS,
            result_date=Arrow.fromdate(date(2014, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2014, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2014, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2014, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2014, 1, 7))

    def test_prev_result_neg2(self):
        """Assert prev_result NEG if recorded_hiv_result,
        result_recorded are discordant.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2014, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_flips_if_absurd1(self):
        """Assert assumes prev_result is wrong based on final
        hiv result, flips result value from POS to NEG.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_flips_if_absurd2(self):
        """Assert assumes prev_result is wrong based on final hiv result,
        flips result value from POS to NEG.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=POS,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_none_if_absurd2(self):
        """Assert assumes prev_result is wrong based on final
        hiv result, flips result value from POS to NEG.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=POS,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_neg_ignores_absurd_result_recorded(self):
        """Assert prev_result NEG from recorded_hiv_result, ignores
        result_recorded eventhough it is absurd.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=POS,
            result_date=Arrow.fromdate(date(2014, 1, 7)).date(),
            result_doc_type='PIMS')

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status, NEG)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status, NEG)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))

    def test_prev_result_pos3(self):
        """Assert sets prev_result POS and uses prev result date
        for final date.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=POS,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

    def test_prev_result_neg3(self):
        """Assert sets prev_result NEG and uses today's result date
        for final date.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_neg31(self):
        """Assert sets prev_result NEG and uses today's result date
        for final date.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_missing(self):
        """Assert all previous result values are None.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertIsNone(obj.prev_result_known)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertEqual(obj.final_hiv_status, NEG)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertIsNone(obj.prev_result_known)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertEqual(obj.final_hiv_status, NEG)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_missing1(self):
        """Assert all previous result values are None.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=NEG)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertIsNone(obj.prev_result_known)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertEqual(obj.final_hiv_status, NEG)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertIsNone(obj.prev_result_known)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertEqual(obj.final_hiv_status, NEG)

    def test_prev_result_pos4(self):
        """Assert takes recorded_hiv_result over result_recorded.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=Arrow.fromdate(date(2015, 1, 7)).date())

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

    def test_prev_result_neg4(self):
        """Assert takes recorded_hiv_result over result_recorded.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_neg41(self):
        """Assert takes recorded_hiv_result over result_recorded.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='PIMS')

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

    def test_arv_status_overrides_neg_rev_result(self):
        """Assert evidence of arv treatment overrides a NEG previous
        result.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type=ART_PRESCRIPTION)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivcareadherence',
            visit_code='T1',
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=NO)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current_arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, DEFAULTER)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current_arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, DEFAULTER)

    def test_arv_status_naive(self):
        """Assert if ever_taken_arv = NO and no response for evidence
        of ARV treatment, final_arv_status=NAIVE.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='?')

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivcareadherence',
            visit_code='T0',
            ever_taken_arv=NO,
            on_arv=NO)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertIsNone(obj.current_arv_evidence)
        self.assertEqual(obj.final_arv_status, NAIVE)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertIsNone(obj.current_arv_evidence)
        self.assertEqual(obj.final_arv_status, NAIVE)

    def test_arv_status_naive1(self):
        """Assert evidence of arv treatment overrides a NEG previous
        result.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=NEG)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=(report_datetime - relativedelta(days=10)).date())

        # T1
        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivresult',
            visit_code='T1',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivtestinghistory',
            visit_code='T1',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=POS)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivcareadherence',
            visit_code='T1',
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=NO)

        obj = StatusHelper(visit=subject_visits[1], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current_arv_evidence, NO)
        self.assertEqual(obj.final_arv_status, NAIVE)

        obj = StatusDbHelper(visit=subject_visits[1])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current_arv_evidence, NO)
        self.assertEqual(obj.final_arv_status, NAIVE)

    def test_arv_status_with_evidence(self):
        """Assert final_arv_status is DEFAULTER for POS if responded as
        never having taken ARV but we found evidence.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='?')

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivcareadherence',
            visit_code='T0',
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=YES)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current_arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, DEFAULTER)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current_arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, DEFAULTER)

    def test_arv_status_with_evidence1(self):
        """Assert final_arv_status is DEFAULTER for POS if responded as
        never having taken ARV but we found evidence.
        """

        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=NEG)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=(report_datetime - relativedelta(days=10)).date())

        # T1

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivresult',
            visit_code='T1',
            hiv_result=POS,
            hiv_result_datetime=subject_visits[1].report_datetime)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivtestinghistory',
            visit_code='T1',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=POS)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivcareadherence',
            visit_code='T1',
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=NO)

        obj = StatusHelper(visit=subject_visits[1], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, NO)
        self.assertEqual(obj.final_arv_status, NAIVE)

        obj = StatusDbHelper(visit=subject_visits[1])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, NO)
        self.assertEqual(obj.final_arv_status, NAIVE)

    def test_arv_status_on_art(self):
        """Assert POS on ART.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=report_datetime)

        # hivresultdocumentation
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresultdocumentation',
            visit_code='T0',
            result_recorded=NEG,
            result_date=Arrow.fromdate(date(2015, 1, 7)).date(),
            result_doc_type='?')

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivcareadherence',
            visit_code='T0',
            ever_taken_arv=YES,
            on_arv=YES,
            arv_evidence=YES)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, ON_ART)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, ON_ART)

    def test_arv_status_on_art1(self):
        """Assert final_arv_status is DEFAULTER for POS if responded as
        never having taken ARV but we found evidence.
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=NEG,
            hiv_test_date=(report_datetime - relativedelta(days=10)).date())

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=NEG)

        # T1

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivresult',
            visit_code='T1',
            hiv_result=POS,
            hiv_result_datetime=subject_visits[1].report_datetime)

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivtestinghistory',
            visit_code='T1',
            other_record=NO,
            has_tested=YES,
            verbal_hiv_result=POS)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivcareadherence',
            visit_code='T1',
            ever_taken_arv=YES,
            on_arv=YES,
            arv_evidence=YES)

        obj = StatusHelper(visit=subject_visits[1], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, ON_ART)

        obj = StatusDbHelper(visit=subject_visits[1])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, ON_ART)

    def test_prev_result_pos5(self):

        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='T0',
            hiv_result=IND,
            hiv_result_datetime=report_datetime)

        # elisaresult
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='elisahivresult',
            visit_code='T0',
            hiv_result=POS,
            hiv_result_datetime=Arrow.fromdate(date(2015, 11, 4)).datetime)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2015, 11, 4))

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2015, 11, 4))

    def test_default_at_enrollment(self):
        """Previously enrollees at t0, t1 who are HIV-positive
        but were on ART, (i.e not arv_naive) at the time of enrollment.
        HivLinkageToCare NOT_REQUIRED 066-01990054-8
        """
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=YES,
            has_tested=YES,
            verbal_hiv_result=POS)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=(report_datetime - relativedelta(days=50)).date())

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivcareadherence',
            visit_code='T0',
            ever_taken_arv=YES,
            on_arv=NO,
            arv_evidence=YES)

        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertTrue(obj.defaulter_at_baseline)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertTrue(obj.defaulter_at_baseline)

        obj = StatusHelper(visit=subject_visits[1], update_history=True)
        self.assertTrue(obj.defaulter_at_baseline)

        obj = StatusDbHelper(visit=subject_visits[1])
        self.assertTrue(obj.defaulter_at_baseline)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=subject_visits[1].report_datetime,
            model='hivcareadherence',
            visit_code='T1',
            ever_taken_arv=YES,
            on_arv=YES,
            arv_evidence=YES)

        obj = StatusHelper(visit=subject_visits[1], update_history=True)
        self.assertEqual(obj.final_arv_status, ON_ART)
        self.assertTrue(obj.defaulter_at_baseline)
        self.assertEqual(obj.final_arv_status_baseline, DEFAULTER)
        self.assertFalse(obj.naive_at_baseline)

        obj = StatusDbHelper(visit=subject_visits[1])
        self.assertEqual(obj.final_arv_status, ON_ART)
        self.assertTrue(obj.defaulter_at_baseline)
        self.assertEqual(obj.final_arv_status_baseline, DEFAULTER)
        self.assertFalse(obj.naive_at_baseline)

    def test_known_positive(self):
        report_datetime = Arrow.fromdatetime(datetime(2016, 1, 7)).datetime
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='T0')
        self.reference_helper.create_visit(
            report_datetime=report_datetime + relativedelta(years=1), timepoint='T1')
        subject_visits = LongitudinalRefset(
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            model=self.visit_model,
            reference_model_cls=self.reference_model
        ).order_by('report_datetime')

        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=YES,
            has_tested=YES,
            verbal_hiv_result=POS)
        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertFalse(obj.known_positive)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertFalse(obj.known_positive)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=(report_datetime - relativedelta(days=50)).date())
        obj = StatusHelper(visit=subject_visits[0], update_history=True)
        self.assertTrue(obj.known_positive)

        obj = StatusDbHelper(visit=subject_visits[0])
        self.assertTrue(obj.known_positive)
