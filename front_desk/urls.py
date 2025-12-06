from django.urls import path
from . import views

app_name = 'front_desk'

urlpatterns = [
    path('', views.front_desk_dashboard, name='dashboard'),
    path('check-in/', views.check_in_list, name='check_in'),
    path('check-out/', views.check_out_list, name='check_out'),
    path('check-in/<uuid:reservation_id>/', views.check_in_guest, name='check_in_guest'),
    path('check-out/<uuid:checkin_id>/', views.check_out_guest, name='check_out_guest'),
    path('walk-in/', views.walk_in_registration, name='walk_in'),
    path('folio/<uuid:folio_id>/', views.folio_management, name='folio'),
    path('night-audit/', views.night_audit, name='night_audit'),
    path('room-availability/', views.room_availability, name='room_availability'),
    path('room-details/<int:room_id>/', views.room_details_ajax, name='room_details_ajax'),
    path('update-room-status/<int:room_id>/', views.update_room_status, name='update_room_status'),
]