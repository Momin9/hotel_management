from django.urls import path
from . import views

urlpatterns = [
    path('', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/create/', views.tenant_create, name='tenant_create'),
    path('tenants/<uuid:tenant_id>/', views.tenant_detail, name='tenant_detail'),
]