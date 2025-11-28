from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Room, Company
from configurations.models import RoomType, BedType, Floor, Amenity
from crm.models import GuestProfile

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_number', 'floor', 'room_type', 'bed_type', 'max_guests', 
            'room_size', 'view_type', 'price', 'status', 'has_wifi', 'has_ac', 
            'has_tv', 'has_minibar', 'has_balcony', 'has_work_desk', 
            'has_seating_area', 'has_kitchenette', 'has_living_room', 
            'amenities', 'additional_amenities', 'description', 'image'
        ]
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'max_guests': forms.NumberInput(attrs={'class': 'form-control'}),
            'room_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'view_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'floor': forms.Select(attrs={'class': 'form-select'}),
            'room_type': forms.Select(attrs={'class': 'form-select'}),
            'bed_type': forms.Select(attrs={'class': 'form-select'}),
            'amenities': forms.CheckboxSelectMultiple(),
            'additional_amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hotel = kwargs.pop('hotel', None)
        super().__init__(*args, **kwargs)
        
        if hotel:
            # Filter choices based on hotel
            self.fields['floor'].queryset = Floor.objects.filter(hotel=hotel)
            self.fields['room_type'].queryset = RoomType.objects.filter(hotel=hotel)
            self.fields['bed_type'].queryset = BedType.objects.filter(hotel=hotel)
            self.fields['amenities'].queryset = Amenity.objects.filter(hotel=hotel)

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'contact_person', 'email', 'phone', 'address', 
            'tax_id', 'discount_percentage', 'credit_limit', 
            'payment_terms', 'is_active', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Net 30 days'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class GuestForm(forms.ModelForm):
    class Meta:
        model = GuestProfile
        fields = [
            'guest_type', 'company', 'first_name', 'last_name', 'email', 
            'phone', 'date_of_birth', 'nationality', 'address', 
            'id_number', 'national_id_card', 'national_id_card_image', 'preferences', 'notes'
        ]
        widgets = {
            'guest_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'id': 'id_guest_type',
                'onchange': 'toggleCompanyField()'
            }),
            'company': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'id': 'id_company'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'guest@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'placeholder': '+1 (555) 123-4567'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'type': 'date'
            }),
            'nationality': CountrySelectWidget(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'rows': 3,
                'placeholder': 'Enter complete address'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'Passport/ID number'
            }),
            'national_id_card': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'placeholder': 'National Identity Card Number'
            }),
            'national_id_card_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'accept': 'image/*'
            }),
            'preferences': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'rows': 3,
                'placeholder': 'Room preferences, dietary requirements, etc.'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-luxury-200 rounded-2xl focus:ring-2 focus:ring-royal-500 focus:border-transparent transition-all duration-200',
                'rows': 3,
                'placeholder': 'Additional notes about the guest'
            }),
        }

    def __init__(self, *args, **kwargs):
        hotel = kwargs.pop('hotel', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Store hotel reference for validation
        self.hotel = hotel
        
        # Ensure guest_type field is properly configured
        self.fields['guest_type'].required = True
        
        # Make national_id_card required for non-superusers
        if user and not user.is_superuser:
            self.fields['national_id_card'].required = True
        
        if hotel:
            # Filter companies based on hotel and active status
            self.fields['company'].queryset = Company.objects.filter(hotel=hotel, is_active=True)
        else:
            # If no hotel, show no companies
            self.fields['company'].queryset = Company.objects.none()
        
        # Set empty label for company field
        self.fields['company'].empty_label = "Select a company"
        
        # Make company field not required by default (will be handled by JavaScript and clean method)
        self.fields['company'].required = False

    def clean(self):
        cleaned_data = super().clean()
        guest_type = cleaned_data.get('guest_type')
        company = cleaned_data.get('company')
        national_id_card_image = cleaned_data.get('national_id_card_image')
        
        if guest_type == 'company' and not company:
            raise forms.ValidationError('Company is required for company guests.')
        
        if guest_type == 'individual' and company:
            cleaned_data['company'] = None
        
        # Check Google Drive configuration if image is uploaded
        if national_id_card_image and hasattr(self, 'hotel') and self.hotel:
            if not self.hotel.google_drive_enabled:
                raise forms.ValidationError('Google Drive integration must be enabled to upload ID card images. Please contact your administrator to configure Google Drive settings.')
            
            if not self.hotel.google_drive_folder_id or not self.hotel.google_service_account_key:
                raise forms.ValidationError('Google Drive configuration is incomplete. Please configure Google Drive folder ID and service account key in hotel settings before uploading images.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle Google Drive upload if image is provided
        if self.cleaned_data.get('national_id_card_image') and hasattr(self, 'hotel') and self.hotel:
            if self.hotel.google_drive_enabled:
                try:
                    from hotels.google_drive_service import upload_to_google_drive
                    
                    image_file = self.cleaned_data['national_id_card_image']
                    filename = f"ID_Card_{instance.first_name}_{instance.last_name}_{instance.national_id_card}.jpg"
                    guest_name = f"{instance.first_name} {instance.last_name}"
                    
                    # Upload to Google Drive
                    drive_result = upload_to_google_drive(
                        image_file.file, 
                        filename, 
                        self.hotel, 
                        guest_name
                    )
                    
                    # Store Google Drive info
                    instance.google_drive_file_id = drive_result['file_id']
                    instance.google_drive_file_link = drive_result['web_view_link']
                    
                except Exception as e:
                    raise forms.ValidationError(f"Failed to upload to Google Drive: {str(e)}")
        
        if commit:
            instance.save()
        
        return instance