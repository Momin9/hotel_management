from django import forms
from .models import Hotel

class GoogleDriveConfigForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = [
            'google_drive_enabled', 'google_drive_folder_id', 
            'google_service_account_key', 'google_drive_share_email'
        ]
        widgets = {
            'google_drive_enabled': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 rounded focus:ring-blue-500'
            }),
            'google_drive_folder_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter Google Drive folder ID'
            }),
            'google_service_account_key': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 8,
                'placeholder': 'Paste your Google Service Account JSON key here'
            }),
            'google_drive_share_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'admin@yourhotel.com'
            }),
        }
        help_texts = {
            'google_drive_enabled': 'Enable Google Drive integration for storing guest documents',
            'google_drive_folder_id': 'The ID of the Google Drive folder where documents will be stored',
            'google_service_account_key': 'JSON key for Google Service Account with Drive API access',
            'google_drive_share_email': 'Email address to share uploaded documents with',
        }

    def clean(self):
        cleaned_data = super().clean()
        enabled = cleaned_data.get('google_drive_enabled')
        folder_id = cleaned_data.get('google_drive_folder_id')
        service_key = cleaned_data.get('google_service_account_key')
        
        if enabled:
            if not folder_id:
                raise forms.ValidationError('Google Drive folder ID is required when Google Drive is enabled.')
            
            if not service_key:
                raise forms.ValidationError('Google Service Account key is required when Google Drive is enabled.')
        
        return cleaned_data