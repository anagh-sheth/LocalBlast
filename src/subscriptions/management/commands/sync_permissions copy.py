from django.core.management.base import BaseCommand

from subscriptions.models import Subscription
from subscriptions import utils as subs_utils


class Command(BaseCommand):

    def handle(self, *args: any, **options: any):
        subs_utils.sync_sub_group_permissions()