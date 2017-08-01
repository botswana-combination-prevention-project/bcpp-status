from django.apps import apps as django_apps

from edc_reference.site import site_reference_configs

from .elisa_result import ElisaResult
from .hiv_care_adherence import HivCareAdherence
from .hiv_result import HivResult
from .hiv_result_documentation import HivResultDocumentation
from .hiv_test_review import HivTestReview
from .hiv_testing_history import HivTestingHistory


class ModelValuesError(Exception):
    pass


class ModelValues:

    """A class that fetches raw model values for the status
    helper class.
    """
    visit_model = 'bcpp_subject.subjectvisit'

    elisa_result_cls = ElisaResult
    hiv_care_adherence_cls = HivCareAdherence
    hiv_result_cls = HivResult
    hiv_test_review_cls = HivTestReview
    hiv_testing_history_cls = HivTestingHistory
    hiv_result_documentation_cls = HivResultDocumentation

    def __init__(self, subject_identifier=None, report_datetime=None, baseline=None,
                 visit_model=None, app_label=None):
        if visit_model:
            self.visit_model = visit_model
        self.baseline = baseline
        self.reference_model_cls = django_apps.get_model(
            site_reference_configs.get_reference_model(self.visit_model))
        self.report_datetime = report_datetime
        self.subject_identifier = subject_identifier
        self.values = {}
        opts = dict(
            subject_identifier=subject_identifier,
            report_datetime=report_datetime,
            baseline=baseline,
            visit_model=self.visit_model,
            app_label=app_label)

        values_classes = [
            self.elisa_result_cls,
            self.hiv_care_adherence_cls,
            self.hiv_result_cls,
            self.hiv_test_review_cls,
            self.hiv_testing_history_cls,
            self.hiv_result_documentation_cls]

        for values_cls in values_classes:
            values_obj = values_cls(**opts)
            for field, value in values_obj:
                if field in values_obj.attrs:
                    self.values.update({field: value})

        for attr in ['arv_evidence',
                     'elisa_hiv_result',
                     'elisa_hiv_result_date',
                     'ever_taken_arv',
                     'has_tested',
                     'on_arv',
                     'other_record',
                     'recorded_hiv_result',
                     'recorded_hiv_result_date',
                     'result_recorded',
                     'result_recorded_document',
                     'self_reported_result',
                     'today_hiv_result',
                     'today_hiv_result_date']:
            if attr not in self.values:
                raise ModelValuesError(
                    f'Attribute missing from values. Got {attr}')
