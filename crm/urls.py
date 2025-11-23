from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.guest_list, name='list'),
    path('new/', views.guest_create, name='create'),
    path('<uuid:guest_id>/', views.guest_detail, name='detail'),
    path('<uuid:guest_id>/edit/', views.guest_edit, name='edit'),
]