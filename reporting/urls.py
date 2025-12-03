from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('occupancy/', views.occupancy_report, name='occupancy'),
    path('occupancy/export/', views.export_occupancy_pdf, name='export_occupancy_pdf'),
    path('revenue/', views.revenue_report, name='revenue'),
    path('revenue/export/', views.export_revenue_pdf, name='export_revenue_pdf'),
    path('guests/', views.guest_report, name='guests'),
    path('guests/export/', views.export_guest_pdf, name='export_guest_pdf'),
    path('performance/', views.performance_report, name='performance'),
    path('performance/export/', views.export_performance_pdf, name='export_performance_pdf'),
]