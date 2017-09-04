# from bcpp_referral.bcpp_referral_facilities import bcpp_referral_facilities
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Populates the status history model'

    def handle(self, *args, **options):
        # bcpp_referral_facilities
        pass
