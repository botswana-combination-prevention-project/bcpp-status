import json

from bcpp_status.models import StatusHistory
from django.core.exceptions import MultipleObjectsReturned
from pprint import pprint


class StatusDbHelper:

    def __init__(self, visit=None):
        self.visit = visit
        self.report_date = visit.report_datetime.date()
        try:
            history_obj = StatusHistory.objects.get(
                status_date=self.report_date)
        except MultipleObjectsReturned:
            history_obj = StatusHistory.objects.filter(
                status_datetime=self.report_date).order_by('created').last()
        data = json.loads(history_obj.data)
        for k, v in data.items():
            setattr(self, k, v)
