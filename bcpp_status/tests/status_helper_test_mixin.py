from dateutil.relativedelta import relativedelta
from edc_constants.constants import YES, NO, NAIVE, DEFAULTER, ON_ART
from edc_constants.constants import POS, NEG, IND, UNK

from ..status_helper import StatusHelper


class StatusHelperTestMixin:

    """Declare as a MIXIN.

    Expects reference_helper (ReferenceTestHelper) class to available

    For example:

        class MyTests(StatusHelperTestMixin, TestCase):

            reference_helper = ReferenceTestHelper
            visit_model = 'bcpp_subject.subjectvisit'

            def setUp(self):
                self.subject_identifier = '111111'
                self.reference_helper = self.reference_helper_cls(
                    visit_model=self.visit_model,
                    subject_identifier=self.subject_identifier)

                [...]

    """

    def prepare_known_positive(self, visit=None):
        # hivtestinghistory
        self.reference_helper.create_for_model(
            report_datetime=visit.report_datetime,
            model='hivtestinghistory',
            visit_code='T0',
            other_record=YES,
            has_tested=YES,
            verbal_hiv_result=POS)
        status_helper = StatusHelper(visit=visit, update_history=True)
        assert not status_helper.known_positive

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=visit.report_datetime,
            model='hivtestreview',
            visit_code='T0',
            recorded_hiv_result=POS,
            hiv_test_date=(visit.report_datetime - relativedelta(days=50)).date())
        status_helper = StatusHelper(visit=visit, update_history=True)
        assert status_helper.known_positive

    def prepare_hiv_status(self, visit=None, result=None):
        if result == POS:
            # hivresult
            self.reference_helper.create_for_model(
                report_datetime=visit.report_datetime,
                model='hivresult',
                visit_code=visit.visit_code,
                hiv_result=POS,
                hiv_result_datetime=visit.report_datetime)
            status_helper = StatusHelper(visit=visit, update_history=True)
            assert status_helper.final_hiv_status == POS
        elif result == NEG:
            # hivresult
            self.reference_helper.create_for_model(
                report_datetime=visit.report_datetime,
                model='hivresult',
                visit_code=visit.visit_code,
                hiv_result=NEG,
                hiv_result_datetime=visit.report_datetime)
            # hivtestreview
            self.reference_helper.create_for_model(
                report_datetime=visit.report_datetime,
                model='hivtestreview',
                visit_code=visit.visit_code,
                recorded_hiv_result=NEG,
                hiv_test_date=(visit.report_datetime - relativedelta(days=50)).date())
            status_helper = StatusHelper(visit=visit, update_history=True)
            assert status_helper.final_hiv_status == NEG
        elif result == IND:
            # hivresult
            self.reference_helper.create_for_model(
                report_datetime=visit.report_datetime,
                model='hivresult',
                visit_code=visit.visit_code,
                hiv_result=IND,
                hiv_result_datetime=visit.report_datetime)
        else:
            status_helper = StatusHelper(visit=visit, update_history=True)
            assert status_helper.final_hiv_status == UNK

    def prepare_art_status(self, visit=None, result=None,
                           defaulter=None, naive=None, on_art=None):

        result = POS if not result else result
        if defaulter:
            result = POS
            ever_taken_arv = YES
            arv_evidence = YES
            on_arv = NO
        elif on_art:
            result = POS
            ever_taken_arv = YES
            arv_evidence = YES
            on_arv = YES
        elif naive:
            ever_taken_arv = NO
            arv_evidence = NO
            on_arv = NO
        else:
            # default is NAIVE
            ever_taken_arv = NO
            arv_evidence = NO
            on_arv = NO

        # hivresult
        self.reference_helper.create_for_model(
            report_datetime=visit.report_datetime,
            model='hivresult',
            visit_code=visit.visit_code,
            hiv_result=result,
            hiv_result_datetime=visit.report_datetime)
        StatusHelper(visit=visit, update_history=True)

        # hivtestinghistory
        if result == POS:
            self.reference_helper.create_for_model(
                report_datetime=visit.report_datetime,
                model='hivtestinghistory',
                visit_code=visit.visit_code,
                other_record=YES,
                has_tested=YES,
                verbal_hiv_result=result)
            StatusHelper(visit=visit, update_history=True)

        # hivtestreview
        self.reference_helper.create_for_model(
            report_datetime=visit.report_datetime,
            model='hivtestreview',
            visit_code=visit.visit_code,
            recorded_hiv_result=result,
            hiv_test_date=(visit.report_datetime - relativedelta(days=50)).date())
        StatusHelper(visit=visit, update_history=True)

        # hivcareadherence
        self.reference_helper.create_for_model(
            report_datetime=visit.report_datetime,
            model='hivcareadherence',
            visit_code=visit.visit_code,
            ever_taken_arv=ever_taken_arv,
            on_arv=on_arv,
            arv_evidence=arv_evidence)

        status_helper = StatusHelper(visit=visit, update_history=True)

        assert status_helper.final_hiv_status == POS
        if defaulter:
            assert status_helper.final_arv_status == DEFAULTER
        elif naive:
            assert status_helper.final_arv_status == NAIVE
        elif on_art:
            assert status_helper.final_arv_status == ON_ART
        else:
            assert status_helper.final_arv_status == NAIVE
