from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.reservation_list, name='list'),
    path('new/', views.reservation_create, name='create'),
    path('booking/', views.booking_list, name='booking_list'),
    path('booking/new/', views.booking_create, name='booking_create'),
    path('booking/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('check-availability/', views.check_room_availability, name='check_availability'),
    path('<uuid:reservation_id>/', views.reservation_detail, name='detail'),
    path('<uuid:reservation_id>/edit/', views.reservation_edit, name='edit'),
    path('<uuid:reservation_id>/cancel/', views.reservation_cancel, name='cancel'),
    path('<uuid:reservation_id>/check-in/', views.check_in, name='check_in'),
    path('<uuid:reservation_id>/check-out/', views.check_out, name='check_out'),
    path('<uuid:reservation_id>/quick-check-in/', views.quick_check_in, name='quick_check_in'),
    path('<uuid:reservation_id>/quick-check-out/', views.quick_check_out, name='quick_check_out'),
]