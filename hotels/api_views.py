from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Hotel
from configurations.models import RoomType

@login_required
def get_room_types(request, hotel_id):
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    room_types = RoomType.objects.filter(hotels=hotel, is_active=True)
    
    data = {
        'room_types': [
            {
                'id': str(rt.id),
                'name': rt.name,
                'description': rt.description or '',
                'max_occupancy': rt.max_occupancy
            }
            for rt in room_types
        ]
    }
    
    return JsonResponse(data)