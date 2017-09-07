from django.db import models, transaction

from .status_helper import StatusHelper
from .models import StatusHistory


class StatusHelperModelMixin(models.Model):

    status_helper_cls = StatusHelper

    def save(self, *args, **kwargs):
        self.update_status_history()
        super().save(*args, **kwargs)

    def update_status_history(self):
        with transaction.atomic():
            StatusHistory.objects.filter(
                subject_identifier=self.appointment.subject_identifier,
                timepoint=self.appointment.visit_code).delete()
        self.status_helper_cls(visit=self, update_history=True)

    class Meta:
        abstract = True
