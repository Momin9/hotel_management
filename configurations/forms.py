from django import forms
from .models import RoomType, RoomCategory, BedType, Floor, Amenity
from hotels.models import Hotel

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'}),
        }

class RoomCategoryForm(forms.ModelForm):
    class Meta:
        model = RoomCategory
        fields = ['name', 'description', 'max_occupancy', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'rows': 3}),
            'max_occupancy': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'min': '1'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500'}),
        }

class BedTypeForm(forms.ModelForm):
    class Meta:
        model = BedType
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500'}),
        }

class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['name', 'number', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent'}),
            'number': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500'}),
        }

class AmenityForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['name', 'description', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-luxury-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent', 'placeholder': 'fas fa-wifi'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-orange-500'}),
        }

