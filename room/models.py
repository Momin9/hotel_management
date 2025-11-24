import uuid
from django.db import models
from django.utils import timezone
from datetime import time


class RoomCategory(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price_per_night = models.FloatField(blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Room(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    hotel = models.ForeignKey('hotel.Hotel', on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    floor = models.IntegerField(blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('under Maintenance','UnderMaintenance' ), ('Cleaning','Cleaning'),('Available', 'Available'), ('Occupied', 'Occupied')],
                              default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def is_booked_now(self):
        now = timezone.now()
        reservations = self.reservation_set.all()
        return any(
            timezone.make_aware(timezone.datetime.combine(reservation.check_in_date, time(12, 0, 0)),
                                timezone.get_current_timezone()) <= now <=
            timezone.make_aware(timezone.datetime.combine(reservation.check_out_date, time(12, 0, 0)),
                                timezone.get_current_timezone())
            for reservation in reservations
        )

    def __str__(self):
        return f"Room {self.room_number} ({self.category.name})"
