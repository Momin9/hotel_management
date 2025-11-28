from django import forms
from .models import RoomType, BedType, Floor, Amenity

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['hotel', 'name', 'description', 'max_occupancy', 'bed_configuration', 'is_active']
        widgets = {
            'hotel': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'placeholder': '🏠 Enter room type name (e.g., Deluxe Suite, Standard Room)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white resize-none',
                'rows': 6,
                'placeholder': '📝 Describe the room type features, amenities, and what makes it special...'
            }),
            'max_occupancy': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'min': '1', 'max': '10',
                'placeholder': '👥 Maximum number of guests'
            }),
            'bed_configuration': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'placeholder': '🛏️ Bed setup (e.g., 1 King Bed, 2 Queen Beds)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            }),
        }

class BedTypeForm(forms.ModelForm):
    class Meta:
        model = BedType
        fields = ['hotel', 'name', 'description', 'is_active']
        widgets = {
            'hotel': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'placeholder': '🛏️ Enter bed type name (e.g., King Size, Queen Size)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white resize-none',
                'rows': 4,
                'placeholder': '📝 Describe the bed type specifications and features...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            }),
        }

class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['hotel', 'floor_number', 'name', 'description', 'is_active']
        widgets = {
            'hotel': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'floor_number': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'placeholder': '🔢 Floor number (e.g., 1, 2, 3, -1 for basement)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'placeholder': '🏢 Floor name (e.g., Ground Floor, Mezzanine)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white resize-none',
                'rows': 4,
                'placeholder': '📝 Describe the floor layout and special features...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            }),
        }

class AmenityForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['hotel', 'name', 'description', 'icon', 'is_active']
        widgets = {
            'hotel': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white appearance-none cursor-pointer'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'placeholder': '✨ Amenity name (e.g., Free Wi-Fi, Pool Access)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white resize-none',
                'rows': 4,
                'placeholder': '📝 Describe the amenity and its benefits...'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-300 shadow-sm hover:shadow-md bg-white',
                'placeholder': '🎨 FontAwesome icon class (e.g., fas fa-wifi, fas fa-swimming-pool)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            }),
        }