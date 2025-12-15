from django.urls import path
from . import views, schedule_views

app_name = 'housekeeping'

urlpatterns = [
    path('', views.housekeeping_dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<uuid:task_id>/update/', views.update_task_status, name='update_task_status'),
    path('maintenance/create/<int:room_id>/', views.create_maintenance_request, name='create_maintenance_request'),
    path('rooms/', views.room_status_list, name='room_status_list'),
    path('rooms/<int:room_id>/update/', views.update_room_status, name='update_room_status'),
    path('assignments/', views.room_assignments, name='room_assignments'),
    path('schedules/', schedule_views.schedule_list, name='schedule_list'),
    path('schedules/create/', schedule_views.create_schedule, name='create_schedule'),
]