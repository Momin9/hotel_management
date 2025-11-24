"""
Public schema URLs - for super admin and tenant management
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_admin(request):
    return redirect('/accounts/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_admin, name='public_home'),
    path('accounts/', include('accounts.urls')),
    path('tenants/', include('tenants.urls')),
]