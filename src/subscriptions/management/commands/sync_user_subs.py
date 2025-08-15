import helpers.billing
from django.core.management.base import BaseCommand

from subscriptions import utils as subs_utils
from customers.models import Customer

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--clear-dangling", action="store_true", default = False)

    def handle(self, *args: any, **options: any):
        clear_dangling = options.get("clear_dangling")
        if clear_dangling:
            subs_utils.clear_dangling_subs()
        else:
            print("Sync active subs ")


