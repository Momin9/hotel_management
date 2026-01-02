from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('accounts.urls')),
    path('hotels/', include('hotels.urls')),
    path('reservations/', include('reservations.urls')),
    path('crm/', include('crm.urls')),
    path('billing/', include('billing.urls')),
    path('housekeeping/', include('housekeeping.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('staff/', include('staff.urls')),
    path('reporting/', include('reporting.urls')),
    path('notifications/', include('notifications.urls')),
    path('front-desk/', include('front_desk.urls')),
    path('pos/', include('pos.urls')),
    path('inventory/', include('inventory.urls')),
    path('finance/', include('finance.urls')),
    path('api/', include('api.urls')),
    path('configurations/', include('configurations.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)