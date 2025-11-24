import uuid
from django.db import models
from django.urls import reverse


class Reservation(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    room = models.ForeignKey('room.Room', on_delete=models.CASCADE, related_name='reservations')
    guest = models.ForeignKey('hotel.Guest', on_delete=models.CASCADE, related_name='reservations')
    additional = models.TextField(null=True, blank=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('reservation_detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.room.room_number} | From {self.check_in_date} to {self.check_out_date}"
