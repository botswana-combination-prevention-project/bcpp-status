from faker import Faker
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.test import TestCase, tag

from edc_base.utils import get_utcnow
from edc_constants.constants import NEG, POS, UNK, YES, IND, NAIVE, NO, MALE
from edc_reference.tests import ReferenceTestHelper
from edc_reference import LongitudinalRefset, site_reference_configs

from ..model_values import ModelValues
from ..status_helper import StatusHelper, DEFAULTER, ART_PRESCRIPTION, ON_ART

from pprint import pprint
from edc_reference.tests.models import SubjectVisit

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

    @tag('1')
    def test(self):
        self.assertIn('hiv_result', site_reference_configs.get_fields(
            'bcpp_subject.hivresult'))
        self.assertIn('arv_evidence', site_reference_configs.get_fields(
            'bcpp_subject.HivCareAdherence'))

    @tag('3')
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

        status_helper = StatusHelper(visit=subject_visits[0])
        self.assertEqual(status_helper.subject_visit, subject_visits[0])
        status_helper = StatusHelper(visit=subject_visits[1])
        self.assertEqual(status_helper.subject_visit, subject_visits[1])

    @tag('3')
    def test2(self):
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

    @tag('3')
    def test3(self):
        report_datetime = get_utcnow()
        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='bhs')

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='bhs',
            hiv_result=POS,
            hiv_result_date=date(2016, 1, 7)
        )
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='bhs',
            recorded_hiv_result=NEG,
            hiv_test_date=date(2013, 5, 7))

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='bhs',
            other_record=UNK,
            has_tested=YES,
            verbal_hiv_result=NEG)

        obj = StatusHelper(
            subject_identifier=self.subject_identifier,
            model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_arv_status, NAIVE)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

    @tag('3')
    def test1(self):
        report_datetime = get_utcnow()

        self.reference_helper.create_visit(
            report_datetime=report_datetime, timepoint='bhs')
        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='subjectrequisition',
            visit_code='bhs',
            panel_name=MICROTUBE,
            is_drawn=YES)

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestinghistory',
            visit_code='bhs',
            other_record=UNK,
            has_tested=YES,
            verbal_hiv_result=NEG)

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivtestreview',
            visit_code='bhs',
            recorded_hiv_result=NEG,
            hiv_test_date=(report_datetime - relativedelta(days=10)).date())

        self.reference_helper.create_for_model(
            report_datetime=report_datetime,
            model='hivresult',
            visit_code='bhs',
            hiv_result=NEG,
            hiv_result_datetime=report_datetime)

        # Create a year 2 subject visit.
        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        report_datetime = subject_visit.report_datetime + timedelta(hours=1)
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=UNK)

        mommy.make_recipe(
            'bcpp_subject.hivcareadherence',
            first_positive=subject_visit.report_datetime -
            relativedelta(days=100),
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            medical_care=NO,
            ever_recommended_arv=NO,
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=NO)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            hiv_result=POS,
            insufficient_vol=NO)

        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_arv_status, NAIVE)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

    def test_final_hiv_status_date(self):
        """Assert date is today's hiv result date."""
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertIsNone(obj.prev_result_known)

    @tag("model_data")
    def test_final_hiv_status_date2(self):
        """Assert date is today's hiv result date."""
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
        )
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=NO
        )
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=POS,
            insufficient_vol=NO)

        obj = StatusHelper(self.subject_visit_male_t0)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_known)

    @tag('confirm???erik')
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
            result_recorded_document=ART_PRESCRIPTION,
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_arv_status, DEFAULTER)
        self.assertEqual(obj.final_hiv_status_date, date(2013, 5, 7))
        self.assertEqual(obj.prev_result_date, date(2013, 5, 7))

    @tag('model_data')
    def test_final_hiv_status_date12(self):
        """Assert date comes from result_recorded_date for
        recorded_hiv_result NEG and DEFAULTER .
        """
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=NEG)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        subject_visit.report_datetime + timedelta(hours=10)

        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=NO
        )
        mommy.make_recipe(
            'bcpp_subject.hivcareadherence',
            first_positive=subject_visit.report_datetime -
            relativedelta(days=100),
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            medical_care=NO,
            ever_recommended_arv=NO,
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=NO)

        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            hiv_result_datetime=subject_visit.report_datetime,
            hiv_result=POS,
            insufficient_vol=NO)

        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.final_arv_status, DEFAULTER)
        self.assertEqual(obj.final_hiv_status_date, date(2013, 5, 7))
        self.assertEqual(obj.prev_result_date, date(2013, 5, 7))

    def test_prev_result_pos(self):
        """Assert prev_result POS taken from recorded_hiv_result
        /recorded_hiv_result_date.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=POS,
            recorded_hiv_result_date=date(2015, 1, 7),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.prev_result_known, YES)

    @tag('model_data')
    def test_prev_result_pos1(self):
        """Assert prev_result POS taken from recorded_hiv_result
        /recorded_hiv_result_date.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=POS,
            recorded_hiv_result_date=date(2015, 1, 7),
        )
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=POS)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=POS,
            insufficient_vol=NO)

        obj = StatusHelper(self.subject_visit_male_t0)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_known, YES)

    def test_first_pos_date(self):
        """Assert uses recorded_hiv_result_date as final date since
        this is the date first POS.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=POS,
            recorded_hiv_result_date=date(2015, 1, 7)
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

    @tag('model_data')
    def test_first_pos_date1(self):
        """Assert prev_result POS taken from recorded_hiv_result
        /recorded_hiv_result_date.
        """
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=POS)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=POS,
            insufficient_vol=NO)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_known, YES)

    def test_prev_result_neg(self):
        """Assert prev_result NEG from recorded_hiv_result.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=NEG,
            recorded_hiv_result_date=date(2015, 1, 7)
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    @tag('model_data')
    def test_prev_result_neg1(self):
        """Assert prev_result NEG from recorded_hiv_result.
        """
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=NEG)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

    def test_prev_result_pos2(self):
        """Assert prev_result POS if recorded_hiv_result,
        result_recorded are discordant.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=NEG,
            recorded_hiv_result_date=date(2015, 1, 7),
            result_recorded=POS,
            result_recorded_date=date(2014, 1, 7)
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2014, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2014, 1, 7))

    @tag('model_data')
    def test_prev_result_pos21(self):
        """Assert prev_result POS if recorded_hiv_result,
        result_recorded are discordant.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=NEG,
            recorded_hiv_result_date=date(2015, 1, 7),
            result_recorded=POS,
            result_recorded_date=date(2014, 1, 7)
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2014, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2014, 1, 7))

    def test_prev_result_neg2(self):
        """Assert prev_result NEG if recorded_hiv_result,
        result_recorded are discordant.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=NEG,
            recorded_hiv_result_date=date(2015, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2014, 1, 7)
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_flips_if_absurd1(self):
        """Assert assumes prev_result is wrong based on final
        hiv result, flips result value from POS to NEG.
        """
        self.model_values.update(
            today_hiv_result=NEG,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=POS,
            recorded_hiv_result_date=date(2015, 1, 6),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 6))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_flips_if_absurd2(self):
        """Assert assumes prev_result is wrong based on final hiv result,
        flips result value from POS to NEG.
        """
        self.model_values.update(
            today_hiv_result=NEG,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=POS,
            result_recorded_date=date(2015, 1, 6),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 6))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_none_if_absurd2(self):
        """Assert assumes prev_result is wrong based on final
        hiv result, flips result value from POS to NEG.
        """
        self.model_values.update(
            today_hiv_result=NEG,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=POS,
            result_recorded_date=date(2015, 1, 6),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 6))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_neg_ignores_absurd_result_recorded(self):
        """Assert prev_result NEG from recorded_hiv_result, ignores
        result_recorded eventhough it is absurd.
        """
        self.model_values.update(
            today_hiv_result=NEG,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=NEG,
            recorded_hiv_result_date=date(2015, 1, 7),
            result_recorded=POS,
            result_recorded_date=date(2014, 1, 7)
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status, NEG)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))

    def test_prev_result_pos3(self):
        """Assert sets prev_result POS and uses prev result date
        for final date.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=POS,
            result_recorded_date=date(2015, 1, 7)
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

    def test_prev_result_neg3(self):
        """Assert sets prev_result NEG and uses today's result date
        for final date.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 6))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    @tag('model_data')
    def test_prev_result_neg31(self):
        """Assert sets prev_result NEG and uses today's result date
        for final date.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
        )
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=NEG)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        report_datetime = subject_visit.report_datetime + timedelta(hours=10)
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=NO)

        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=subject_visit,
            report_datetime=report_datetime + relativedelta(months=4),
            hiv_result=POS,
            insufficient_vol=NO)

        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 6))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    def test_prev_result_missing(self):
        """Assert all previous result values are None.
        """
        self.model_values.update(
            today_hiv_result=NEG,
            today_hiv_result_date=date(2016, 1, 7),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertIsNone(obj.prev_result_known)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertEqual(obj.final_hiv_status, NEG)
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    @tag("model_data")
    def test_prev_result_missing1(self):
        """Assert all previous result values are None.
        """
        self.model_values.update(
            today_hiv_result=NEG,
            today_hiv_result_date=date(2016, 1, 7),
        )
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )
#         hiv_test_date = (
#             self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
#         mommy.make_recipe(
#             'bcpp_subject.hivtestreview',
#             subject_visit=self.subject_visit_male_t0,
#             hiv_test_date=hiv_test_date.date(),
#             recorded_hiv_result=NEG)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)
        obj = StatusHelper(self.subject_visit_male_t0)
        self.assertIsNone(obj.prev_result_known)
        self.assertIsNone(obj.prev_result)
        self.assertIsNone(obj.prev_result_date)
        self.assertEqual(obj.final_hiv_status, NEG)

    def test_prev_result_pos4(self):
        """Assert takes recorded_hiv_result over result_recorded.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            recorded_hiv_result=POS,
            recorded_hiv_result_date=date(2015, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, POS)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 7))
        self.assertEqual(obj.final_hiv_status_date, date(2015, 1, 7))

    def test_prev_result_neg4(self):
        """Assert takes recorded_hiv_result over result_recorded.
        """
        self.model_values.update(
            today_hiv_result=NEG,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)
        self.assertEqual(obj.prev_result_date, date(2015, 1, 6))
        self.assertEqual(obj.final_hiv_status_date, date(2016, 1, 7))

    @tag('model_data')
    def test_prev_result_neg41(self):
        """Assert takes recorded_hiv_result over result_recorded.
        """
        self.model_values.update(
            today_hiv_result=NEG,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
        )
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=NEG)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        report_datetime = subject_visit.report_datetime + timedelta(hours=10)
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )

        mommy.make_recipe(
            'bcpp_subject.hivcareadherence',
            first_positive=subject_visit.report_datetime -
            relativedelta(days=100),
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            medical_care=NO,
            ever_recommended_arv=NO,
            ever_taken_arv=YES,
            on_arv=NO,
            arv_evidence=NO)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)

        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.prev_result_known, YES)
        self.assertEqual(obj.prev_result, NEG)

    def test_arv_status_overrides_neg_rev_result(self):
        """Assert evidence of arv treatment overrides a NEG previous
        result.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
            ever_taken_arv=NO,
            on_arv=NO,
            result_recorded_document=ART_PRESCRIPTION,
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, DEFAULTER)

    def test_arv_status_naive(self):
        """Assert if ever_taken_arv = NO and no response for evidence
        of ARV treatment, final_arv_status=NAIVE.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
            ever_taken_arv=NO,
            on_arv=NO,
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertIsNone(obj.current.arv_evidence)
        self.assertEqual(obj.final_arv_status, NAIVE)

    @tag('model_data')
    def test_arv_status_naive1(self):
        """Assert evidence of arv treatment overrides a NEG previous
        result.
        """
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=NEG)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        report_datetime = subject_visit.report_datetime + timedelta(hours=10)
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=NO
        )
        mommy.make_recipe(
            'bcpp_subject.hivcareadherence',
            first_positive=subject_visit.report_datetime -
            relativedelta(days=100),
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            medical_care=NO,
            ever_recommended_arv=NO,
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=NO)

        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            hiv_result=POS,
            insufficient_vol=NO)

        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, NO)
        self.assertEqual(obj.final_arv_status, NAIVE)

    def test_arv_status_with_evidence(self):
        """Assert final_arv_status is DEFAULTER for POS if responded as
        never having taken ARV but we found evidence.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=YES
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, DEFAULTER)

    @tag('model_data')
    def test_arv_status_with_evidence1(self):
        """Assert final_arv_status is DEFAULTER for POS if responded as
        never having taken ARV but we found evidence.
        """
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=NEG)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        report_datetime = subject_visit.report_datetime + timedelta(hours=10)
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=NO
        )
        mommy.make_recipe(
            'bcpp_subject.hivcareadherence',
            first_positive=subject_visit.report_datetime -
            relativedelta(days=100),
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            medical_care=NO,
            ever_recommended_arv=NO,
            ever_taken_arv=NO,
            on_arv=NO,
            arv_evidence=NO)

        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            hiv_result=POS,
            insufficient_vol=NO)

        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, NO)
        self.assertEqual(obj.final_arv_status, NAIVE)

    def test_arv_status_on_art(self):
        """Assert POS on ART.
        """
        self.model_values.update(
            today_hiv_result=POS,
            today_hiv_result_date=date(2016, 1, 7),
            result_recorded=NEG,
            result_recorded_date=date(2015, 1, 6),
            ever_taken_arv=YES,
            on_arv=YES,
            arv_evidence=YES
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, ON_ART)

    @tag('model_data')
    def test_arv_status_on_art1(self):
        """Assert final_arv_status is DEFAULTER for POS if responded as
        never having taken ARV but we found evidence.
        """
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=NEG,
            other_record=NO
        )
        hiv_test_date = (
            self.subject_visit_male_t0.report_datetime - relativedelta(days=10))
        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=hiv_test_date.date(),
            recorded_hiv_result=NEG)
        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result_datetime=self.subject_visit_male_t0.report_datetime,
            hiv_result=NEG,
            insufficient_vol=NO)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        report_datetime = subject_visit.report_datetime + timedelta(hours=10)
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=NO
        )
        mommy.make_recipe(
            'bcpp_subject.hivcareadherence',
            first_positive=subject_visit.report_datetime -
            relativedelta(days=100),
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            medical_care=YES,
            ever_recommended_arv=YES,
            ever_taken_arv=YES,
            on_arv=YES,
            arv_evidence=YES)

        mommy.make_recipe(
            'bcpp_subject.subjectrequisition',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            panel_name=MICROTUBE,
            is_drawn=YES)
        mommy.make_recipe(
            'bcpp_subject.hivresult',
            subject_visit=subject_visit,
            report_datetime=report_datetime,
            hiv_result=POS,
            insufficient_vol=NO)

        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.current.arv_evidence, YES)
        self.assertEqual(obj.final_arv_status, ON_ART)

    def test_prev_result_pos5(self):
        self.model_values.update(
            elisa_hiv_result=POS,
            elisa_hiv_result_date=date(2015, 11, 4),
            today_hiv_result=IND,
            today_hiv_result_date=date(2015, 10, 22),
            recorded_hiv_result=None,
            recorded_hiv_result_date=None,
            result_recorded=None,
            result_recorded_date=None,
        )
        obj = StatusHelper(self.visit, model_values=self.model_values)
        self.assertEqual(obj.final_hiv_status, POS)
        self.assertEqual(obj.final_hiv_status_date, date(2015, 11, 4))

    @tag('test_default_at_enrollment_helper')
    def test_default_at_enrollment(self):
        """Previously enrollees at t0, t1 who are HIV-positive
        but were on ART, (i.e not arv_naive) at the time of enrollment.
        HivLinkageToCare NOT_REQUIRED 066-01990054-8
        """
        mommy.make_recipe(
            'bcpp_subject.hivtestinghistory',
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.get_utcnow(),
            has_tested=YES,
            when_hiv_test='1 to 5 months ago',
            has_record=YES,
            verbal_hiv_result=POS,
            other_record=YES
        )

        mommy.make_recipe(
            'bcpp_subject.hivtestreview',
            report_datetime=self.get_utcnow(),
            subject_visit=self.subject_visit_male_t0,
            hiv_test_date=self.get_utcnow() - timedelta(days=50),
            recorded_hiv_result=POS)

        mommy.make_recipe(
            'bcpp_subject.hivcareadherence',
            first_positive=self.get_utcnow(),
            subject_visit=self.subject_visit_male_t0,
            report_datetime=self.get_utcnow(),
            medical_care=YES,
            ever_recommended_arv=YES,
            ever_taken_arv=YES,
            on_arv=NO,
            arv_evidence=YES,  # this is the rule field
        )

        obj = StatusHelper(self.subject_visit_male_t0)
        self.assertTrue(obj.defaulter_at_baseline)

        subject_visit = self.add_subject_visit_followup(
            self.subject_visit_male_t0.household_member, T1)

        obj = StatusHelper(subject_visit)
        self.assertTrue(obj.defaulter_at_baseline)

        # add HivCarAdherence,
        mommy.make_recipe(
            'bcpp_subject.hivcareadherence',
            first_positive=subject_visit.report_datetime,
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            medical_care=YES,
            ever_recommended_arv=YES,
            ever_taken_arv=YES,
            on_arv=YES,
            arv_evidence=YES,  # this is the rule field
        )
        obj = StatusHelper(subject_visit)
        self.assertEqual(obj.final_arv_status, ON_ART)
        self.assertTrue(obj.defaulter_at_baseline)
