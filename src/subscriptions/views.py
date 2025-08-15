import helpers.billing
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from subscriptions.models import SubscriptionPrice, UserSubscription
from subscriptions import utils as subs_utils

# Create your views here.
@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("refresh sub")
        finished = subs_utils.refresh_active_users_subscriptions(user_ids=[request.user.id])
  
        if finished:
            messages.success(request, "Your subscription details have been refreshed")
        else:
            messages.error(request, "Your plan details have not been refreshed, please try again.")

        return redirect(user_sub_obj.get_absolute_url())
    
    return render(request, 'subscriptions/user_detail_view.html', {"subscription": user_sub_obj})

@login_required
def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("refresh sub")
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:
            sub_data = helpers.billing.cancel_subscription(user_sub_obj.stripe_id, reason="User cancelled", 
                                                           feedback="other", cancel_at_period_end=True, raw = False) 
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, "Your subscription has been cancelled")
        return redirect(user_sub_obj.get_absolute_url())
    
    return render(request, 'subscriptions/user_cancel_view.html', {"subscription": user_sub_obj})

def subscription_price_view(request):
    qs = SubscriptionPrice.objects.filter(featured=True)
    monthly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.MONTHLY)
    yearly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.YEARLY)
    return render(request, "subscriptions/pricing.html", {
        "monthly_qs": monthly_qs,
        "yearly_qs": yearly_qs,
    })