from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('dashboard/', views.hotel_dashboard, name='dashboard'),
    path('overview/', views.hotel_overview, name='overview'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/create/', views.hotel_create, name='hotel_create'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('hotels/<int:hotel_id>/rooms/', views.room_list, name='room_list'),
    path('hotels/<int:hotel_id>/rooms/create/', views.room_create, name='room_create'),
    path('hotels/<int:hotel_id>/rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('hotels/<int:hotel_id>/rooms/<int:room_id>/edit/', views.room_edit, name='room_edit'),
]