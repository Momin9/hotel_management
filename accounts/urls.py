from django.urls import path
from django.shortcuts import redirect
from . import views
from .test_email import test_subscription_email

app_name = 'accounts'

def home_redirect(request):
    return redirect('accounts:login')

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('about/', views.about_page, name='about'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.custom_login, name='login'),
    path('contact/', views.contact_form, name='contact_form'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('super-admin/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # Subscription Plans CRUD
    path('subscription-plans/', views.subscription_plan_list, name='subscription_plan_list'),
    path('subscription-plans/create/', views.subscription_plan_create, name='subscription_plan_create'),
    path('subscription-plans/<int:plan_id>/edit/', views.subscription_plan_edit, name='subscription_plan_edit'),
    path('subscription-plans/<int:plan_id>/delete/', views.subscription_plan_delete, name='subscription_plan_delete'),
    
    # Hotel Owners CRUD
    path('hotel-owners/', views.hotel_owner_list, name='hotel_owner_list'),
    path('hotel-owners/create/', views.hotel_owner_create, name='hotel_owner_create'),
    path('hotel-owners/<int:owner_id>/edit/', views.hotel_owner_edit, name='hotel_owner_edit'),
    path('hotel-owners/<int:owner_id>/delete/', views.hotel_owner_delete, name='hotel_owner_delete'),
    
    # Hotels CRUD
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/create/', views.hotel_create, name='hotel_create'),
    path('hotels/<int:hotel_id>/edit/', views.hotel_edit, name='hotel_edit'),
    path('hotels/<int:hotel_id>/delete/', views.hotel_delete, name='hotel_delete'),
    
    # Hotel Subscriptions CRUD
    path('hotel-subscriptions/', views.hotel_subscription_list, name='hotel_subscription_list'),
    path('hotel-subscriptions/create/', views.hotel_subscription_create, name='hotel_subscription_create'),
    path('hotel-subscriptions/<int:subscription_id>/edit/', views.hotel_subscription_edit, name='hotel_subscription_edit'),
    path('hotel-subscriptions/<int:subscription_id>/delete/', views.hotel_subscription_delete, name='hotel_subscription_delete'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/guests/', views.guests_analytics, name='guests_analytics'),
    path('analytics/dining/', views.dining_analytics, name='dining_analytics'),
    path('check-trial-status/', views.check_trial_status, name='check_trial_status'),
    path('download/hotels-pdf/', views.download_hotels_pdf, name='download_hotels_pdf'),
    path('download/subscriptions-pdf/', views.download_subscriptions_pdf, name='download_subscriptions_pdf'),
    path('download/plans-pdf/', views.download_plans_pdf, name='download_plans_pdf'),
    
    # Test Email
    path('test-subscription-email/', test_subscription_email, name='test_subscription_email'),
]