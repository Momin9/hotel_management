from django import forms

from hotel.models import Guest
from main.models import Reservation
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'category', 'floor', 'price_per_night', 'status']

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'government_id', 'address', 'city', 'country', 'gender']

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['guest', 'room', 'check_in_date', 'check_out_date', 'additional']
