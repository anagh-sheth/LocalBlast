from django.core.management.base import BaseCommand

from subscriptions.models import Subscription


class Command(BaseCommand):

    def handle(self, *args: any, **options: any):
        print("Hello, world!")
        qs = Subscription.objects.all()
        for obj in qs:
        #    print(obj.groups.all())
            sub_perms = obj.permissions.all()
            for group in obj.groups.all():
                group.permissions.set(sub_perms)
        #    print(obj.permissions.all())
