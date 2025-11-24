from django import forms
from django.contrib.auth.models import User
from .models import Client, TenantSettings, SubscriptionPlan, TenantUser

class TenantForm(forms.ModelForm):
    """Form for creating/editing tenants"""
    domain_name = forms.CharField(
        max_length=50,
        help_text="Subdomain name (e.g., 'hotel1' for hotel1.yourdomain.com)"
    )
    
    class Meta:
        model = Client
        fields = ['name', 'contact_email', 'contact_phone', 'subscription_plan']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'subscription_plan': forms.Select(attrs={'class': 'form-control'}),
        }

class TenantSettingsForm(forms.ModelForm):
    """Form for tenant-specific settings"""
    
    class Meta:
        model = TenantSettings
        fields = [
            'currency', 'tax_rate', 'service_charge_rate', 'branding_logo',
            'locale', 'timezone', 'check_in_time', 'check_out_time',
            'cancellation_policy', 'deposit_policy'
        ]
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'service_charge_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'branding_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'locale': forms.TextInput(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'check_in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'cancellation_policy': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deposit_policy': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class SubscriptionPlanForm(forms.ModelForm):
    """Form for managing subscription plans"""
    
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'description', 'price', 'billing_cycle', 'max_properties', 'max_rooms', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-control'}),
            'max_properties': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TenantUserForm(forms.ModelForm):
    """Form for managing tenant users"""
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = TenantUser
        fields = ['role', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:
            # Editing existing user
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['password'].required = False
    
    def save(self, commit=True):
        tenant_user = super().save(commit=False)
        
        if not self.instance.pk:
            # Creating new user
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=self.cleaned_data['password']
            )
            tenant_user.user = user
            tenant_user.tenant = self.tenant
        else:
            # Updating existing user
            user = tenant_user.user
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            
            if commit:
                user.save()
        
        if commit:
            tenant_user.save()
        
        return tenant_user