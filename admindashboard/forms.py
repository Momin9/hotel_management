from django import forms

from .models import *


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'
