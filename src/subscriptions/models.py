from django.db import models
from django.db.models import Q

from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.urls import reverse


from django.conf import settings
import helpers.billing


User = settings.AUTH_USER_MODEL

ALLOW_CUSTOM_GROUPS = True
SUBSCRIPTION_PERMISSIONS = [
    ("basic", "Basic"),
    ("pro", "Pro"),
]

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=120)
    subtitle = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, 
                                         limit_choices_to=
                                         {"content_type__app_label": "subscriptions", "codename__in": [perm[0] for perm in SUBSCRIPTION_PERMISSIONS]})
    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    order = models.IntegerField(default=-1, help_text="Order on django pricing page")
    featured = models.BooleanField(default=True, help_text="Featured on django pricing page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


    class Meta:
        ordering = ["order", "featured", "-updated"]
        permissions = SUBSCRIPTION_PERMISSIONS

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = helpers.billing.create_product(name = self.name,
                                                        metadata = {"subscription_plan_id": self.id}, 
                                                        raw=False)
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)



class SubscriptionPrice(models.Model):
    class IntervalChoices(models.TextChoices):
        MONTHLY  = "month", "Monthly"
        YEARLY = "year", "Yearly"

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(max_length=120, default= IntervalChoices.MONTHLY, choices = IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1, help_text="Order on django pricing page")
    featured = models.BooleanField(default=True, help_text="Featured on django pricing page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["subscription__order", "order", "featured", "-updated"]


    def get_checkout_url(self):
        return reverse("sub-price-checkout", kwargs={"price_id": self.id}) 

    @property
    def display_sub_subtitle(self):
        if not self.subscription:
            return "Plan"

        return self.subscription.subtitle
    
    @property
    def stripe_currency(self):
        return "usd"
    
    @property
    def stripe_price(self):
        # remove decimal places
        return int(self.price * 100)

    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id
    

    def save(self, *args, **kwargs):
        if (self.stripe_id is None and self.product_stripe_id is not None):
            
            stripe_id = helpers.billing.create_price(currency = self.stripe_currency,
                                unit_amount = self.stripe_price,
                                interval = self.interval,
                                product = self.product_stripe_id,
                                metadata = {"subscription_plan_price_id": self.id},
                                raw = False)
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)   

        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(subscription = self.subscription, 
                                                  interval = self.interval,
                                                  ).exclude(id = self.id)
            qs.update(featured=False)

class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CANCELED = "canceled", "Canceled"
    PAUSED = "paused", "Paused"
    TRIALING = "trialing", "Trialing"  # 3 days free trial
    INCOMPLETE = "incomplete", "Incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired", "Incomplete Expired"
    PAST_DUE = "past_due", "Past Due"
    UNPAID = "unpaid", "Unpaid"

class UserSubscriptionQuerySet(models.QuerySet):
    def by_active_trailing(self):
        return self.filter(Q(status=SubscriptionStatus.ACTIVE) | Q(status=SubscriptionStatus.TRIALING))
    
    def by_user_ids(self, user_ids=None):
        if isinstance(user_ids, list):
            return self.filter(user_id__in=user_ids)
        elif isinstance(user_ids, int):
            return self.filter(user_id__in=[user_ids])
        elif isinstance(user_ids, str):
            return self.filter(user_id=user_ids)
        return self

class UserSubscriptionManager(models.Manager):
    def get_queryset(self):
        return UserSubscriptionQuerySet(self.model, using=self._db)
        
  #  def by_user_ids(self, user_ids=None):
  #      return self.get_queryset().by_user_ids(user_ids=user_ids)


    

class UserSubscription(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null = True, blank = True)
    active = models.BooleanField(default=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True) 
    user_cancelled = models.BooleanField(default=False)
    original_period_start = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    current_period_start = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    current_period_end = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    status = models.CharField(max_length=20, null=True, blank=True, choices=SubscriptionStatus.choices)

    objects = UserSubscriptionManager()



    def get_absolute_url(self):
        return reverse("user_subscription")
    
    def get_cancel_url(self):
        return reverse("user_subscription_cancel")
    
    def is_active_status(self):
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
    
    @property
    def plan_name(self):
        if not self.subscription:
            return None
        return self.subscription.name
    

    def serialize(self):
        return {
            "plan_name": self.plan_name,
            "status": self.status,
            "current_period_start": self.current_period_start,
            "current_period_end": self.current_period_end,

        }
# optional delay to start new subscription in stripe checkout
    @property
    def billing_cycle_anchor(self):
        if not self.current_period_end:
            return None
        return int(self.current_period_end.timestamp())

 
    def save(self, *args, **kwargs):
        if (self.original_period_start is None and self.current_period_start is not None):
            self.current_period_start = self.original_period_start
        super().save(*args, **kwargs)


def user_sub_post_save(sender, instance, created, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list("id", flat=True)

    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_qs = Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)
     #   groups_ids = groups.values_list("id", flat=True)
        current_groups = user.groups.all().values_list("id", flat=True)
        groups_ids_set = set(groups_ids)
        current_groups_set = set(current_groups) - subs_groups_set
        final_groups_ids = list(groups_ids_set | current_groups_set)
        user.groups.set(final_groups_ids)

post_save.connect(user_sub_post_save, sender=UserSubscription)

