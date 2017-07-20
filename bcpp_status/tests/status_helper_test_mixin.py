from dateutil.relativedelta import relativedelta

from edc_constants.constants import YES, NO, POS


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

    def prepare_art_status(self, report_datetime=None, defaulter=True, naive=None, on_art=None):

        if defaulter:
            ever_taken_arv = YES
            arv_evidence = YES
            on_arv = NO
        elif naive:
            ever_taken_arv = NO
            arv_evidence = NO
            on_arv = NO
        elif on_art:
            ever_taken_arv = YES
            arv_evidence = YES
            on_arv = YES
        else:
            # default is NAIVE
            ever_taken_arv = NO
            arv_evidence = NO
            on_arv = NO

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
            ever_taken_arv=ever_taken_arv,
            on_arv=on_arv,
            arv_evidence=arv_evidence)
