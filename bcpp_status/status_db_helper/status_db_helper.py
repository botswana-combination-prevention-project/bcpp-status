import json

from bcpp_status.models import StatusHistory
from bcpp_status.status_helper import StatusHelper
from django.core.exceptions import MultipleObjectsReturned, ValidationError, ObjectDoesNotExist

from .current import Current
from .parser import datetime_parser


class StatusDbHelper:

    def __init__(self, visit=None, subject_identifier=None, validate=None):
        if visit:
            self.report_datetime = visit.report_datetime
            self.subject_identifier = visit.subject_identifier
            self.subject_visit = visit
            self.visit_code = visit.visit_code
            self.report_date = visit.report_datetime.date()
            self.history_obj = self.get_or_create_history(visit=visit)
        elif subject_identifier:
            self.subject_identifier = subject_identifier
            self.history_obj = StatusHistory.objects.filter(
                subject_identifier=self.subject_identifier).order_by(
                    'status_date', '-created').first()

        self._data = json.loads(self.history_obj.data,
                                object_hook=datetime_parser)

        for k, v in self._data.items():
            if not k.startswith('_'):
                setattr(self, k, v)

        self.current = Current(
            today_hiv_result=self.current_hiv_result,
            arv_evidence=self.current_arv_evidence)

        if validate:
            self.validate(visit=visit)

    def get_or_create_history(self, visit=None):
        try:
            history_obj = StatusHistory.objects.get(
                subject_identifier=self.subject_identifier,
                timepoint=self.visit_code,
                status_date=self.report_date)
        except ObjectDoesNotExist:
            StatusHelper(visit=visit, update_history=True)
            history_obj = StatusHistory.objects.get(
                subject_identifier=self.subject_identifier,
                timepoint=self.visit_code,
                status_date=self.report_date)
        except MultipleObjectsReturned:
            history_obj = StatusHistory.objects.filter(
                subject_identifier=self.subject_identifier,
                status_date=self.report_date).order_by('created').last()
        return history_obj

    def validate(self, visit=None):
        status_helper = StatusHelper(visit=visit)
        for k in status_helper._data:
            if not k.startswith('_'):
                db_value = getattr(self, k)
                obj_value = getattr(status_helper, k)
                if db_value != obj_value:
                    msg = (f'{k} DB value differs at {self.history_obj.status_date} '
                           f'for {visit.timepoint}. Got {db_value} (db) != {obj_value}.')
                    raise ValidationError(msg)
