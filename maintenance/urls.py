from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.maintenance_dashboard, name='dashboard'),
    path('issues/', views.issue_list, name='issue_list'),
    path('issues/new/', views.issue_create, name='issue_create'),
    path('issues/<uuid:issue_id>/update/', views.issue_update, name='issue_update'),
]