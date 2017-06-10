from edc_constants.constants import POS, NOT_APPLICABLE, DECLINED, NEG, NO, DWTA

from ..models import (
    HivCareAdherence, ElisaHivResult, HivTestingHistory, HivTestReview,
    HivResultDocumentation, HivResult, SubjectVisit)


class ModelValues:

    """A class that fetches raw model values for the status
    helper class.
    """

    def __init__(self, visit, baseline=None):
        self.arv_evidence = None
        self.elisa_hiv_result = None
        self.elisa_hiv_result_date = None
        self.ever_taken_arv = None
        self.has_tested = None
        self.on_arv = None
        self.other_record = None
        self.recorded_hiv_result = None
        self.recorded_hiv_result_date = None
        self.result_recorded = None
        self.result_recorded_document = None
        self.self_reported_result = None
        self.today_hiv_result = None
        self.today_hiv_result_date = None

        if baseline:
            self.subject_visit = SubjectVisit.objects.filter(
                subject_identifier=visit.subject_identifier).order_by(
                    'report_datetime').first()
            options = dict(subject_visit=self.subject_visit)
        else:
            self.subject_visit = visit
            options = dict(
                subject_visit__subject_identifier=visit.subject_identifier,
                subject_visit__report_datetime__lte=visit.report_datetime)

        # HivCareAdherence
        obj = HivCareAdherence.objects.filter(
            **options).order_by('report_datetime').last()
        if obj:
            self.arv_evidence = None if obj.arv_evidence == NOT_APPLICABLE else obj.arv_evidence

            self.ever_taken_arv = obj.ever_taken_arv
            if obj.ever_taken_arv == DWTA:
                self.ever_taken_arv = NO

            self.on_arv = obj.on_arv
            if self.on_arv == NOT_APPLICABLE:
                self.on_arv = None
            elif self.on_arv == DWTA:
                self.on_arv = NO

        # HivTestingHistory
        self.update_from_hiv_testing_history(visit, **options)

        # HivTestReview
        self.update_from_direct_documention(visit, **options)

        # HivResultDocumentation
        self.update_from_indirect_documentation(visit, **options)

        # ElisaHivResult
        self.update_from_elisa(visit, **options)

        # HivResult performed, not declined
        self.update_from_rapid_hiv_tests(visit, **options)

        try:
            obj = HivResult.objects.get(
                subject_visit=visit, hiv_result=DECLINED)
        except HivResult.DoesNotExist:
            self.declined = None
        else:
            self.declined = True

    def update_from_hiv_testing_history(self, visit, **options):
        qs = HivTestingHistory.objects.filter(
            **options).order_by('report_datetime')
        if qs:
            obj = self.get_first_positive_or_none(qs, 'verbal_hiv_result')
            if obj:
                self.has_tested = obj.has_tested
                self.other_record = obj.other_record
                self.self_reported_result = obj.verbal_hiv_result
            else:
                self.has_tested = qs.last().has_tested
                self.other_record = qs.last().other_record
                self.self_reported_result = qs.last().verbal_hiv_result
        # print('self_reported_result', self.self_reported_result)

    def update_from_rapid_hiv_tests(self, visit, **options):
        """Updates using values from HivResult fetching the first POS from
        the history of HivResult, if one exists, or with a NEG result from
        today, if it exists.
        """
        # HivResult performed, not declined
        qs = HivResult.objects.filter(
            hiv_result_datetime__isnull=False,
            **options).order_by('hiv_result_datetime')
        if qs:
            obj = self.get_first_positive_or_none(qs, 'hiv_result')
            if obj:
                self.today_hiv_result = obj.hiv_result
                self.today_hiv_result_date = obj.hiv_result_datetime.date()
            else:
                try:
                    obj = HivResult.objects.get(
                        subject_visit=visit, hiv_result=NEG)
                except HivResult.DoesNotExist:
                    pass
                else:
                    self.today_hiv_result = obj.hiv_result
                    self.today_hiv_result_date = obj.hiv_result_datetime.date()
        # print('today_hiv_result', self.today_hiv_result)

    def update_from_direct_documention(self, visit, **options):
        qs = HivTestReview.objects.filter(
            **options).order_by('hiv_test_date')
        if qs:
            obj = self.get_first_positive_or_none(qs, 'recorded_hiv_result')
            if obj:
                self.recorded_hiv_result = obj.recorded_hiv_result
                self.recorded_hiv_result_date = obj.hiv_test_date
            else:
                self.recorded_hiv_result = qs.last().recorded_hiv_result
                self.recorded_hiv_result_date = qs.last().hiv_test_date
        # print('recorded_hiv_result', self.recorded_hiv_result)

    def update_from_indirect_documentation(self, visit, **options):
        """Updates using values from HivResultDocumentation fetching the first
        POS from the history of HivResultDocumentation, if one exists, or from
        the last entered HivResultDocumentation.
        """
        qs = HivResultDocumentation.objects.filter(
            **options).order_by('result_date')
        if qs:
            obj = self.get_first_positive_or_none(qs, 'result_recorded')
            if obj:
                self.result_recorded = obj.result_recorded
                self.result_recorded_date = obj.result_date
                self.result_recorded_document = obj.result_doc_type
            else:
                self.result_recorded = qs.last().result_recorded
                self.result_recorded_date = qs.last().result_date
                self.result_recorded_document = qs.last().result_doc_type
        # print('result_recorded', self.result_recorded)

    def update_from_elisa(self, visit, **options):
        """Updates using the first POS, if it exists, or the last result,
        if it exists.
        """
        qs = ElisaHivResult.objects.filter(
            **options).order_by('hiv_result_datetime')
        if qs:
            obj = self.get_first_positive_or_none(qs, 'hiv_result')
            if obj:
                self.elisa_hiv_result = obj.hiv_result
                self.elisa_hiv_result_date = obj.hiv_result_datetime
            else:
                self.elisa_hiv_result = qs.last().hiv_result
                self.elisa_hiv_result_date = qs.last().hiv_result_datetime

    def get_first_positive_or_none(self, qs, field_name):
        """Returns the first model instance that is POS or None.
        """
        for obj in qs:
            if getattr(obj, field_name) == POS:
                return obj
        return None
