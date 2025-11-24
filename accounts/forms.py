from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from .models import ContactInquiry

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address',
        'id': 'form2Example11'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'id': 'form2Example22'
    }))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError("Invalid email or password")
        return self.cleaned_data


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your registered email',
    }))


class ResetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password',
        }),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password',
        }),
        label="Confirm New Password"
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['full_name', 'work_email', 'phone_number', 'hotel_name', 'job_title', 
                 'number_of_rooms', 'subject', 'message', 'hear_about_us', 'privacy_consent']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'work_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@hotel.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'hotel_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your hotel/property name'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'General Manager, Owner, etc.'}),
            'number_of_rooms': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your needs...'}),
            'hear_about_us': forms.Select(attrs={'class': 'form-select'}),
            'privacy_consent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'full_name': 'Full Name *',
            'work_email': 'Work Email *',
            'phone_number': 'Phone Number *',
            'hotel_name': 'Hotel/Property Name *',
            'job_title': 'Job Title *',
            'number_of_rooms': 'Number of Rooms *',
            'subject': 'Subject / Goal *',
            'message': 'Your Message *',
            'hear_about_us': 'How did you hear about us?',
            'privacy_consent': 'I agree to the privacy policy and terms of service *',
        }
