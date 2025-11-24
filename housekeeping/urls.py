from django.urls import path
from . import views

app_name = 'housekeeping'

urlpatterns = [
    path('', views.housekeeping_dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
]