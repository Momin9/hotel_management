from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list, name='list'),
    path('create/', views.staff_create, name='create'),
    path('<int:staff_id>/', views.staff_detail, name='detail'),
    path('<int:staff_id>/edit/', views.staff_edit, name='edit'),
    path('<int:staff_id>/permissions/', views.staff_permissions, name='permissions'),
    path('<int:staff_id>/message/', views.staff_send_message, name='send_message'),
    path('<int:staff_id>/schedule/', views.staff_schedule, name='schedule'),
    path('<int:staff_id>/performance/', views.staff_performance, name='performance'),
    path('<int:staff_id>/delete/', views.staff_delete, name='delete'),
]