from django.urls import path
from . import api_views

urlpatterns = [
    path('room-types/<int:hotel_id>/', api_views.get_room_types, name='api_room_types'),
]