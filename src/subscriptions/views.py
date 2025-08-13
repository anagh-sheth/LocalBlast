import helpers.billing
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from subscriptions.models import SubscriptionPrice, UserSubscription


# Create your views here.
@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("refresh sub")
        if user_sub_obj.stripe_id:
            sub_data = helpers.billing.get_subscription(user_sub_obj.stripe_id, raw = False) 
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
        return redirect(user_sub_obj.get_absolute_url())
    
    return render(request, 'subscriptions/user_detail_view.html', {"subscription": user_sub_obj})

@login_required
def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("refresh sub")
        if user_sub_obj.stripe_id:
            sub_data = helpers.billing.get_subscription(user_sub_obj.stripe_id, raw = False) 
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
        return redirect(user_sub_obj.get_absolute_url())
    
    return render(request, 'subscriptions/user_detail_view.html', {"subscription": user_sub_obj})

def subscription_price_view(request):
    qs = SubscriptionPrice.objects.filter(featured=True)
    monthly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.MONTHLY)
    yearly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.YEARLY)
    return render(request, "subscriptions/pricing.html", {
        "monthly_qs": monthly_qs,
        "yearly_qs": yearly_qs,
    })