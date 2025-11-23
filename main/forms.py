from django import forms
from django.contrib.auth import get_user_model

from main.models import Reservation

User = get_user_model()


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['room', 'guest', 'check_in_date', 'check_out_date', 'additional']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'guest': forms.Select(attrs={'class': 'form-control'}),
            'check_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'additional': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional Information'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')

        if check_in_date and check_out_date and check_out_date <= check_in_date:
            raise forms.ValidationError("Check-out date must be after check-in date")
        return cleaned_data
