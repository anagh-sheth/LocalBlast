"""
URL configuration for localblast project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from auth import views as auth_views
from checkouts import views as checkout_views
from subscriptions import views as subscription_views
from features import views as feature_views

from localblast.views import home_view, about_view, pw_protected_view, user_only_view, staff_only_view


urlpatterns = [
    path('', home_view, name='home'),
  #  path('login/', auth_views.login_view),
  #  path('register/', auth_views.register_view),
    path('about/', about_view),

    
    # Features URLs
    path('dashboard/', feature_views.dashboard_view, name='dashboard'),
    
    # Business Profiles
    path('businesses/', feature_views.business_profile_list, name='business_profile_list'),
    path('businesses/create/', feature_views.business_profile_create, name='business_profile_create'),
    path('businesses/<int:pk>/', feature_views.business_profile_detail, name='business_profile_detail'),
    path('businesses/<int:pk>/edit/', feature_views.business_profile_edit, name='business_profile_edit'),
    path('businesses/<int:business_pk>/audit/', feature_views.run_seo_audit, name='run_seo_audit'),
    
    # SEO Audits
    path('audits/<int:audit_pk>/', feature_views.audit_detail, name='audit_detail'),
    
    # Checklists
    path('checklists/', feature_views.checklist_list, name='checklist_list'),
    path('checklists/create/', feature_views.checklist_create, name='checklist_create'),
    path('checklists/<int:pk>/', feature_views.checklist_detail, name='checklist_detail'),
    
    # Ranking Trackers
    path('rankings/', feature_views.ranking_tracker_list, name='ranking_tracker_list'),
    path('rankings/create/', feature_views.ranking_tracker_create, name='ranking_tracker_create'),
    
    path("checkout/sub-price/<int:price_id>/", 
            checkout_views.product_price_redirect_view,
            name='sub-price-checkout'
            ),
    path("checkout/start/", 
            checkout_views.checkout_redirect_view,
            name='stripe-checkout-start'
            ),
    path("checkout/success/", 
            checkout_views.checkout_finalize_view,
            name='stripe-checkout-end'
            ),


    path('pricing/', subscription_views.subscription_price_view, name='pricing'),
    path('accounts/billing/', subscription_views.user_subscription_view, name='user_subscription'),
    path('accounts/billing/cancel/', subscription_views.user_subscription_cancel_view, name='user_subscription_cancel'),
    path('accounts/', include('allauth.urls')),
    path('protected/', pw_protected_view),
    path('protected/user-only/', user_only_view),
    path('protected/staff-only/', user_only_view),
    path('profiles/', include('profiles.urls')),
    path('admin/', admin.site.urls),

]
