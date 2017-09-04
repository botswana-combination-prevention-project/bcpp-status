import json

from datetime import datetime
from bcpp_status.models import StatusHistory
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from bcpp_status.status_helper import StatusHelper


class Current:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            try:
                v = datetime.strptime(v, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                pass
            setattr(self, k, v)


class StatusDbHelper:

    def __init__(self, visit=None, subject_identifier=None):

        if visit:
            self.report_datetime = visit.report_datetime
            self.subject_identifier = visit.subject_identifier
            self.subject_visit = visit
            self.visit_code = visit.visit_code
            self.report_date = visit.report_datetime.date()
            history_obj = self.get_or_create_history(visit=visit)
        elif subject_identifier:
            self.subject_identifier = subject_identifier
            history_obj = StatusHistory.objects.filter(
                subject_identifier=self.subject_identifier).order_by('created').last()
        data = json.loads(history_obj.data)
        for k, v in data.items():
            try:
                v = datetime.strptime(v, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                pass
            setattr(self, k, v)
        self.current = Current(
            hiv_result=self.current_hiv_result,
            arv_evidence=self.current_arv_evidence)

    def get_or_create_history(self, visit=None):
        try:
            history_obj = StatusHistory.objects.get(
                status_date=self.report_date)
        except ObjectDoesNotExist:
            history_obj = StatusHelper(
                visit=visit, update_history=True).history_obj
        except MultipleObjectsReturned:
            history_obj = StatusHistory.objects.filter(
                status_date=self.report_date).order_by('created').last()
        return history_obj
