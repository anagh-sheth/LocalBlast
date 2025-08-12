import helpers.billing
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from subscriptions.models import SubscriptionPrice, UserSubscription


# Create your views here.
@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("refresh sub")
    sub_data = {}
    if user_sub_obj.stripe_id:
        sub_data = helpers.billing.get_subscription(user_sub_obj.stripe_id, raw = False) 
    return render(request, 'subscriptions/user_detail_view.html', {"subscription": sub_data})

def subscription_price_view(request):
    qs = SubscriptionPrice.objects.filter(featured=True)
    monthly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.MONTHLY)
    yearly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.YEARLY)
    return render(request, "subscriptions/pricing.html", {
        "monthly_qs": monthly_qs,
        "yearly_qs": yearly_qs,
    })