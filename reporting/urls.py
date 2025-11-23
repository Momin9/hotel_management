from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('occupancy/', views.occupancy_report, name='occupancy'),
    path('revenue/', views.revenue_report, name='revenue'),
    path('guests/', views.guest_report, name='guests'),
]