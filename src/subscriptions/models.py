from django.db import models
from django.contrib.auth.models import Group, Permission

SUBSCRIPTION_PERMISSIONS = [
    ("basic", "Basic"),
    ("pro", "Pro"),
]

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=120)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, 
                                         limit_choices_to=
                                         {"content_type__app_label": "subscriptions", "codename__in": [perm[0] for perm in SUBSCRIPTION_PERMISSIONS]})

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
