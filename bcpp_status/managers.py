from django.db import models


class StatusHistoryManager(models.Manager):

    def get_by_natural_key(self, status_date, subject_identifier):
        return self.get(
            status_date=status_date,
            subject_identifier=subject_identifier)
