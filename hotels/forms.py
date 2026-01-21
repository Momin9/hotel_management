from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Room, Company, CompanyRoomRate
from configurations.models import RoomType, RoomCategory, BedType, Floor, Amenity
from crm.models import GuestProfile

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_number', 'floor', 'room_type', 'room_category', 'bed_type', 'max_guests', 
            'room_size', 'view_type', 'price', 'status', 'has_wifi', 'has_ac', 
            'has_tv', 'has_minibar', 'has_balcony', 'has_work_desk', 
            'has_seating_area', 'has_kitchenette', 'has_living_room', 
            'amenities', 'additional_amenities', 'description', 'image'
        ]
        widgets = {
            'room_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'placeholder': '🏠 Enter room number (e.g., 101, A-205)'
            }),
            'max_guests': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'min': '1', 'max': '10', 'placeholder': '👥 Maximum guests'
            }),
            'room_size': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'min': '100', 'placeholder': '📐 Room size in sq ft'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'step': '0.01', 'min': '0', 'placeholder': '💰 Price per night'
            }),
            'view_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'floor': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'room_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'room_category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'bed_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'grid grid-cols-2 gap-3'
            }),
            'additional_amenities': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white resize-none',
                'rows': 3,
                'placeholder': '✨ Premium Amenities, Coffee Machine, etc. (comma-separated)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white resize-none',
                'rows': 4,
                'placeholder': '📝 Describe the room features, atmosphere, and unique selling points...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-gray-50 hover:bg-blue-50 cursor-pointer file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        hotel = kwargs.pop('hotel', None)
        super().__init__(*args, **kwargs)
        
        if hotel:
            # Filter choices based on hotel
            self.fields['floor'].queryset = Floor.objects.filter(hotels=hotel)
            self.fields['room_type'].queryset = RoomType.objects.filter(hotels=hotel)
            self.fields['room_category'].queryset = hotel.config_room_categories.all()
            self.fields['bed_type'].queryset = BedType.objects.filter(hotels=hotel)
            self.fields['amenities'].queryset = Amenity.objects.filter(hotels=hotel)

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            # Company Information
            'name', 'business_type', 'logo', 'registration_number',
            # Contact Information  
            'address', 'city', 'state', 'country', 'phone', 'email', 'website',
            # Authorized Person
            'contact_person', 'designation', 'mobile_number', 'contact_email',
            # Contract Details
            'contract_start_date', 'contract_end_date', 'approved_room_types',
            'corporate_discount', 'billing_mode', 'status',
            # Legacy fields
            'credit_limit', 'payment_terms', 'notes'
        ]
        widgets = {
            # Company Information
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'Enter company name'}),
            'business_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent'}),
            'logo': forms.FileInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'accept': 'image/*'}),
            'registration_number': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'Registration/Tax Number'}),
            
            # Contact Information
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'rows': 3, 'placeholder': 'Registered address'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'Country'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': '+92 300 1234567'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'company@example.com'}),
            'website': forms.URLInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'https://company.com'}),
            
            # Authorized Person
            'contact_person': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'Contact person name'}),
            'designation': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'Manager, Director, etc.'}),
            'mobile_number': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': '+92 300 1234567'}),
            'contact_email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'contact@example.com'}),
            
            # Contract Details
            'contract_start_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'type': 'date'}),
            'approved_room_types': forms.CheckboxSelectMultiple(attrs={'class': 'rounded border-luxury-300 text-royal-600 focus:ring-royal-500'}),
            'corporate_discount': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '10.00'}),
            'billing_mode': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent'}),
            
            # Legacy fields
            'credit_limit': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'step': '0.01', 'min': '0', 'placeholder': '100000.00'}),
            'payment_terms': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'Net 30 days'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'rows': 4, 'placeholder': 'Additional notes about the company'}),
        }
    
    def __init__(self, *args, **kwargs):
        hotel = kwargs.pop('hotel', None)
        super().__init__(*args, **kwargs)
        
        if hotel:
            self.fields['approved_room_types'].queryset = RoomType.objects.filter(hotels=hotel, is_active=True)
        else:
            self.fields['approved_room_types'].queryset = RoomType.objects.none()


class CompanyRoomRateForm(forms.ModelForm):
    class Meta:
        model = CompanyRoomRate
        fields = ['room_type', 'rate_per_night', 'currency', 'is_active']
        widgets = {
            'room_type': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent'}),
            'rate_per_night': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'step': '0.01', 'min': '0', 'placeholder': '8000.00'}),
            'currency': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:border-transparent', 'placeholder': 'PKR'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-royal-600 bg-gray-100 border-gray-300 rounded focus:ring-royal-500'}),
        }
    
    def __init__(self, *args, **kwargs):
        hotel = kwargs.pop('hotel', None)
        super().__init__(*args, **kwargs)
        
        if hotel:
            self.fields['room_type'].queryset = RoomType.objects.filter(hotels=hotel)
        else:
            self.fields['room_type'].queryset = RoomType.objects.none()

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