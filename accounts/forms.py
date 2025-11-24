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
            'full_name': forms.TextInput(attrs={
                'class': 'advanced-input', 
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'work_email': forms.EmailInput(attrs={
                'class': 'advanced-input', 
                'placeholder': 'your.email@hotel.com',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'advanced-input', 
                'placeholder': '+1 (555) 123-4567',
                'required': True
            }),
            'hotel_name': forms.TextInput(attrs={
                'class': 'advanced-input', 
                'placeholder': 'Your hotel or property name',
                'required': True
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'advanced-input', 
                'placeholder': 'General Manager, Owner, Director, etc.',
                'required': True
            }),
            'number_of_rooms': forms.Select(attrs={
                'class': 'advanced-select',
                'required': True
            }),
            'subject': forms.Select(attrs={
                'class': 'advanced-select',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'advanced-textarea', 
                'rows': 5, 
                'placeholder': 'Tell us about your specific needs, challenges, or goals. The more details you provide, the better we can assist you.',
                'required': True
            }),
            'hear_about_us': forms.Select(attrs={
                'class': 'advanced-select'
            }),
            'privacy_consent': forms.CheckboxInput(attrs={
                'class': 'advanced-checkbox',
                'required': True
            }),
        }
        labels = {
            'full_name': 'Full Name *',
            'work_email': 'Work Email Address *',
            'phone_number': 'Phone Number *',
            'hotel_name': 'Hotel/Property Name *',
            'job_title': 'Your Job Title *',
            'number_of_rooms': 'Number of Rooms *',
            'subject': 'What brings you here today? *',
            'message': 'Tell us more about your needs *',
            'hear_about_us': 'How did you discover AuraStay?',
            'privacy_consent': 'Privacy Agreement *',
        }
