import json

from django.db import models
from django.db.models.indexes import Index
from edc_base.model_mixins import BaseUuidModel
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin


class StatusHistory(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    status_date = models.DateField()

    timepoint = models.CharField(max_length=25)

    final_hiv_status = models.CharField(
        max_length=25, null=True)

    final_hiv_status_date = models.DateField(null=True)

    final_arv_status = models.CharField(
        max_length=25, null=True)

    data = models.TextField()

    def __str__(self):
        return f'{self.subject_identifier}, {self.status_date}, {self.timepoint}, created={self.created}'

    def to_dict(self):
        return json.loads(self.data)

    class Meta:
        ordering = ('subject_identifier', 'status_date', '-created')
        indexes = [
            Index(fields=['subject_identifier', 'status_date']),
            Index(fields=['subject_identifier', 'status_date', '-created'])]
