from datetime import datetime
# from bcpp_referral.bcpp_referral_facilities import bcpp_referral_facilities
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand
from bcpp_status.status_helper.status_helper import StatusHelper
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from bcpp_status.models import StatusHistory
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
            history_obj = StatusHistory.objects.get(
                subject_identifier=visit.subject_identifier,
                timepoint=visit.visit_code)
        except ObjectDoesNotExist:
            StatusHelper(visit=visit, update_history=True)
            history_obj = StatusHistory.objects.get(
                subject_identifier=visit.subject_identifier,
                timepoint=visit.visit_code)
        except MultipleObjectsReturned:
            history_obj = StatusHistory().objects.filter(
                subject_identifier=visit.subject_identifier,
                timepoint=visit.visit_code).order_by('created').last()
        return history_obj
