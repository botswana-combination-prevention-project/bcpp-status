import sys

from bcpp_status.models import StatusHistory
from bcpp_status.status_helper.status_helper import StatusHelper, StatusHelperError
from datetime import datetime
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from tqdm._tqdm import tqdm


class Command(BaseCommand):

    help = 'Populates the status history model'
    subject_visit_model = 'bcpp_subject.subjectvisit'

    def handle(self, *args, **options):
        cutoff_date = datetime(2017, 1, 1)
        subject_visits = self.subject_visit_model_cls.objects.filter(
            report_datetime__date__gte=cutoff_date)
        for visit in tqdm(subject_visits):
            self.get_or_create_history(visit)

    @property
    def subject_visit_model_cls(self):
        return django_apps.get_model(self.subject_visit_model)

    def get_or_create_history(self, visit=None):
        try:
            StatusHistory.objects.get(
                subject_identifier=visit.subject_identifier,
                timepoint=visit.visit_code)
        except ObjectDoesNotExist:
            try:
                StatusHelper(visit=visit, update_history=True)
            except StatusHelperError as e:
                sys.stdout.write(f'StatusHelperError for {visit.subject_identifier}. Got {e}')
        except MultipleObjectsReturned:
            pass
