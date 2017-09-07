from django.apps import apps as django_apps

from edc_reference import LongitudinalRefset, site_reference_configs


class Values:

    model = None
    visit_model = None

    def __init__(self, subject_identifier=None, report_datetime=None,
                 baseline=None, visit_model=None):
        if visit_model:
            self.visit_model = visit_model
        self.values = {}
        self.baseline = baseline
        self.subject_identifier = subject_identifier
        self.report_datetime = report_datetime
        self.reference_model_cls = django_apps.get_model(
            site_reference_configs.get_reference_model(name=self.visit_model))
        self.longitudinal_refset = LongitudinalRefset(
            name=self.model,
            subject_identifier=self.subject_identifier,
            visit_model=self.visit_model,
            reference_model_cls=self.reference_model_cls,
            **self.options).order_by('report_datetime')

    def __iter__(self):
        return iter([(k, v) for k, v in self.values.items()])

    @property
    def options(self):
        """Returns a dictionary of additional refset query options.
        """
        if self.baseline:
            reference = self.reference_model_cls.objects.filter(
                model=self.visit_model,
                identifier=self.subject_identifier).first()
            options = dict(
                report_datetime=reference.report_datetime)
        else:
            options = dict(report_datetime__lte=self.report_datetime)
        return options
