from django import forms
from django.contrib.auth import get_user_model

from hotel.models import Hotel, Guest, Employee

User = get_user_model()


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'contact_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hotel Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Hotel Address'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['hotel', 'user', 'role', 'salary']
        widgets = {
            'hotel': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Role'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salary'}),
        }


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['hotel', 'first_name', 'last_name', 'email', 'phone_number', 'government_id', 'address']
        widgets = {
            'hotel': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'government_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Government ID'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address'}),
        }
