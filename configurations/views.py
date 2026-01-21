import csv
import os
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RoomType, RoomCategory, BedType, Floor, Amenity
from .forms import RoomTypeForm, RoomCategoryForm, BedTypeForm, FloorForm, AmenityForm
from hotels.models import Hotel
from accounts.decorators import owner_or_permission_required
from django.http import JsonResponse

# Room Type Views
@login_required
def room_type_list(request):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    # Base queryset
    if request.user.is_superuser:
        room_types = RoomType.objects.all().distinct().order_by('name')
        hotels = Hotel.objects.all().order_by('name')
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user).order_by('name')
        room_types = RoomType.objects.filter(hotels__in=hotels).distinct().order_by('name')
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        room_types = RoomType.objects.filter(hotels=request.user.assigned_hotel).distinct().order_by('name') if request.user.assigned_hotel else RoomType.objects.none()
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        room_types = room_types.filter(name__icontains=search)
    
    hotel_filter = request.GET.get('hotel')
    if hotel_filter:
        room_types = room_types.filter(hotels__hotel_id=hotel_filter)
    
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        room_types = room_types.filter(is_active=True)
    elif status_filter == 'inactive':
        room_types = room_types.filter(is_active=False)
    
    occupancy_filter = request.GET.get('occupancy')
    if occupancy_filter:
        if occupancy_filter == '4':
            room_types = room_types.filter(max_occupancy__gte=4)
        else:
            room_types = room_types.filter(max_occupancy=occupancy_filter)
    
    context = {
        'room_types': room_types,
        'hotels': hotels,
    }
    return render(request, 'configurations/room_type_list.html', context)

@login_required
def room_type_create(request):
    # Check if user has permission to create configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_add_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to create configurations.')
        return redirect('configurations:room_type_list')
    if request.method == 'POST':
        form = RoomTypeForm(request.POST)
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        elif form.is_valid():
            room_type = form.save()
            
            # Add selected hotels
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                room_type.hotels.add(hotel)
            
            messages.success(request, f'Room type "{room_type.name}" created for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:room_type_list')
    else:
        form = RoomTypeForm()
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
        default_hotel = None
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        default_hotel = hotels.first()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        default_hotel = request.user.assigned_hotel
    
    return render(request, 'configurations/room_type_form.html', {'form': form, 'hotels': hotels, 'default_hotel': default_hotel})

@login_required
def room_type_detail(request, pk):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    room_type = get_object_or_404(RoomType, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    # Get related rooms using this room type
    related_rooms = room_type.rooms.all()[:10]  # Limit to 10 rooms for display
    
    context = {
        'room_type': room_type,
        'related_rooms': related_rooms,
    }
    return render(request, 'configurations/room_type_detail.html', context)

@login_required
def room_type_edit(request, pk):
    # Check if user has permission to edit configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_change_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to edit configurations.')
        return redirect('configurations:room_type_list')
    room_type = get_object_or_404(RoomType, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    if request.method == 'POST':
        form = RoomTypeForm(request.POST, instance=room_type)
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        elif form.is_valid():
            room_type = form.save()
            
            # Update hotels
            room_type.hotels.clear()
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                room_type.hotels.add(hotel)
            
            messages.success(request, f'Room type "{room_type.name}" updated for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:room_type_list')
    else:
        form = RoomTypeForm(instance=room_type)
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/room_type_form.html', {'form': form, 'room_type': room_type, 'hotels': hotels})

@login_required
def room_type_delete(request, pk):
    # Check if user has permission to delete configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_delete_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to delete configurations.')
        return redirect('configurations:room_type_list')
    room_type = get_object_or_404(RoomType, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    if request.method == 'POST':
        room_type.delete()
        messages.success(request, 'Room type deleted successfully!')
        return redirect('configurations:room_type_list')
    return render(request, 'configurations/confirm_delete.html', {'object': room_type, 'type': 'Room Type'})

# Room Category Views
@login_required
def room_category_list(request):
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    if request.user.is_superuser:
        room_categories = RoomCategory.objects.all().distinct().order_by('name')
        hotels = Hotel.objects.all().order_by('name')
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user).order_by('name')
        room_categories = RoomCategory.objects.filter(hotels__in=hotels).distinct().order_by('name')
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        room_categories = RoomCategory.objects.filter(hotels=request.user.assigned_hotel).distinct().order_by('name') if request.user.assigned_hotel else RoomCategory.objects.none()
    
    context = {'room_categories': room_categories, 'hotels': hotels}
    return render(request, 'configurations/room_category_list.html', context)

@login_required
def room_category_create(request):
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_add_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to create configurations.')
        return redirect('configurations:room_category_list')
    
    if request.method == 'POST':
        form = RoomCategoryForm(request.POST)
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        elif form.is_valid():
            room_category = form.save()
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                room_category.hotels.add(hotel)
            messages.success(request, f'Room category "{room_category.name}" created!')
            return redirect('configurations:room_category_list')
    else:
        form = RoomCategoryForm()
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
        default_hotel = None
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        default_hotel = hotels.first()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        default_hotel = request.user.assigned_hotel
    
    return render(request, 'configurations/room_category_form.html', {'form': form, 'hotels': hotels, 'default_hotel': default_hotel})

@login_required
def room_category_detail(request, pk):
    room_category = get_object_or_404(RoomCategory, pk=pk)
    return render(request, 'configurations/room_category_detail.html', {'room_category': room_category})

@login_required
def room_category_edit(request, pk):
    room_category = get_object_or_404(RoomCategory, pk=pk)
    
    if request.method == 'POST':
        form = RoomCategoryForm(request.POST, instance=room_category)
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        elif form.is_valid():
            room_category = form.save()
            room_category.hotels.clear()
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                room_category.hotels.add(hotel)
            messages.success(request, f'Room category "{room_category.name}" updated!')
            return redirect('configurations:room_category_list')
    else:
        form = RoomCategoryForm(instance=room_category)
    
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/room_category_form.html', {'form': form, 'room_category': room_category, 'hotels': hotels})

@login_required
def room_category_delete(request, pk):
    room_category = get_object_or_404(RoomCategory, pk=pk)
    
    if request.method == 'POST':
        room_category.delete()
        messages.success(request, 'Room category deleted successfully!')
        return redirect('configurations:room_category_list')
    return render(request, 'configurations/confirm_delete.html', {'object': room_category, 'type': 'Room Category'})

# Bed Type Views
@login_required
def bed_type_list(request):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    # Base queryset
    if request.user.is_superuser:
        bed_types = BedType.objects.all().distinct().order_by('name')
        hotels = Hotel.objects.all().order_by('name')
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user).order_by('name')
        bed_types = BedType.objects.filter(hotels__in=hotels).distinct().order_by('name')
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        bed_types = BedType.objects.filter(hotels=request.user.assigned_hotel).distinct().order_by('name') if request.user.assigned_hotel else BedType.objects.none()
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        bed_types = bed_types.filter(name__icontains=search)
    
    hotel_filter = request.GET.get('hotel')
    if hotel_filter:
        bed_types = bed_types.filter(hotels__hotel_id=hotel_filter)
    
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        bed_types = bed_types.filter(is_active=True)
    elif status_filter == 'inactive':
        bed_types = bed_types.filter(is_active=False)
    
    context = {
        'bed_types': bed_types,
        'hotels': hotels,
    }
    return render(request, 'configurations/bed_type_list.html', context)

@login_required
def bed_type_create(request):
    # Check if user has permission to create configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_add_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to create configurations.')
        return redirect('configurations:bed_type_list')
    if request.method == 'POST':
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            bed_type = BedType.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                usage=request.POST.get('usage', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                bed_type.hotels.add(hotel)
            
            messages.success(request, f'Bed type "{bed_type.name}" created for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:bed_type_list')
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
        default_hotel = None
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        default_hotel = hotels.first()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        default_hotel = request.user.assigned_hotel
    
    return render(request, 'configurations/bed_type_form.html', {'hotels': hotels, 'default_hotel': default_hotel})

@login_required
def bed_type_detail(request, pk):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    bed_type = get_object_or_404(BedType, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    # Get related rooms using this bed type (if there's a relationship)
    # Note: This assumes there's a relationship between Room and BedType
    # You may need to adjust this based on your actual Room model structure
    try:
        related_rooms = bed_type.rooms.all()[:10]  # Limit to 10 rooms for display
    except:
        related_rooms = []  # If no relationship exists yet
    
    context = {
        'bed_type': bed_type,
        'related_rooms': related_rooms,
    }
    return render(request, 'configurations/bed_type_detail.html', context)

@login_required
def bed_type_edit(request, pk):
    # Check if user has permission to edit configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_change_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to edit configurations.')
        return redirect('configurations:bed_type_list')
    bed_type = get_object_or_404(BedType, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    if request.method == 'POST':
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            bed_type.name = request.POST.get('name')
            bed_type.description = request.POST.get('description', '')
            bed_type.usage = request.POST.get('usage', '')
            bed_type.is_active = request.POST.get('is_active') == 'on'
            bed_type.save()
            
            bed_type.hotels.clear()
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                bed_type.hotels.add(hotel)
            
            messages.success(request, f'Bed type "{bed_type.name}" updated for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:bed_type_list')
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/bed_type_form.html', {'bed_type': bed_type, 'hotels': hotels})

@login_required
def bed_type_delete(request, pk):
    # Check if user has permission to delete configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_delete_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to delete configurations.')
        return redirect('configurations:bed_type_list')
    bed_type = get_object_or_404(BedType, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    if request.method == 'POST':
        bed_type.delete()
        messages.success(request, 'Bed type deleted successfully!')
        return redirect('configurations:bed_type_list')
    return render(request, 'configurations/confirm_delete.html', {'object': bed_type, 'type': 'Bed Type'})

# Floor Views
@login_required
def floor_list(request):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    # Base queryset
    if request.user.is_superuser:
        floors = Floor.objects.all().distinct().order_by('name')
        hotels = Hotel.objects.all().order_by('name')
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user).order_by('name')
        floors = Floor.objects.filter(hotels__in=hotels).distinct().order_by('name')
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        floors = Floor.objects.filter(hotels=request.user.assigned_hotel).distinct().order_by('name') if request.user.assigned_hotel else Floor.objects.none()
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        floors = floors.filter(name__icontains=search)
    
    hotel_filter = request.GET.get('hotel')
    if hotel_filter:
        floors = floors.filter(hotels__hotel_id=hotel_filter)
    
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        floors = floors.filter(is_active=True)
    elif status_filter == 'inactive':
        floors = floors.filter(is_active=False)
    
    number_filter = request.GET.get('number')
    if number_filter:
        floors = floors.filter(number=number_filter)
    
    context = {
        'floors': floors,
        'hotels': hotels,
    }
    return render(request, 'configurations/floor_list.html', context)

@login_required
def floor_create(request):
    # Check if user has permission to create configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_add_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to create configurations.')
        return redirect('configurations:floor_list')
    if request.method == 'POST':
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            # Check permissions for each selected hotel
            for hotel_id in hotel_ids:
                try:
                    hotel = Hotel.objects.get(hotel_id=hotel_id)
                    if not request.user.is_superuser and request.user.role != 'Owner':
                        if not hasattr(request.user, 'assigned_hotel') or hotel != request.user.assigned_hotel:
                            messages.error(request, f'You do not have permission to create floors for {hotel.name}.')
                            return redirect('configurations:floor_list')
                    elif request.user.role == 'Owner' and hotel.owner != request.user:
                        messages.error(request, f'You do not have permission to create floors for {hotel.name}.')
                        return redirect('configurations:floor_list')
                except Hotel.DoesNotExist:
                    messages.error(request, f'Hotel with ID {hotel_id} does not exist.')
                    return redirect('configurations:floor_list')
            
            floor = Floor.objects.create(
                name=request.POST.get('name'),
                number=int(request.POST.get('number')),
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            
            for hotel_id in hotel_ids:
                hotel = Hotel.objects.get(hotel_id=hotel_id)
                floor.hotels.add(hotel)
            
            messages.success(request, f'Floor "{floor.name}" created for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:floor_list')
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
        default_hotel = None
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        default_hotel = hotels.first()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        default_hotel = request.user.assigned_hotel
    
    return render(request, 'configurations/floor_form.html', {'hotels': hotels, 'default_hotel': default_hotel})

@login_required
def floor_detail(request, pk):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    floor = get_object_or_404(Floor, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    # Get related rooms on this floor
    try:
        related_rooms = floor.rooms.all()[:10]  # Limit to 10 rooms for display
    except:
        related_rooms = []  # If no relationship exists yet
    
    context = {
        'floor': floor,
        'related_rooms': related_rooms,
    }
    return render(request, 'configurations/floor_detail.html', context)

def floor_edit(request, pk):
    # Check if user has permission to edit configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_change_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to edit configurations.')
        return redirect('configurations:floor_list')
    floor = get_object_or_404(Floor, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    if request.method == 'POST':
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            floor.name = request.POST.get('name')
            floor.number = int(request.POST.get('number'))
            floor.description = request.POST.get('description', '')
            floor.is_active = request.POST.get('is_active') == 'on'
            floor.save()
            
            floor.hotels.clear()
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                floor.hotels.add(hotel)
            
            messages.success(request, f'Floor "{floor.name}" updated for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:floor_list')
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/floor_form.html', {'floor': floor, 'hotels': hotels})

@login_required
def floor_delete(request, pk):
    # Check if user has permission to delete configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_delete_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to delete configurations.')
        return redirect('configurations:floor_list')
    floor = get_object_or_404(Floor, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    if request.method == 'POST':
        floor.delete()
        messages.success(request, 'Floor deleted successfully!')
        return redirect('configurations:floor_list')
    return render(request, 'configurations/confirm_delete.html', {'object': floor, 'type': 'Floor'})

# Amenity Views
@login_required
def amenity_list(request):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    # Base queryset
    if request.user.is_superuser:
        amenities = Amenity.objects.all().distinct().order_by('name')
        hotels = Hotel.objects.all().order_by('name')
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user).order_by('name')
        amenities = Amenity.objects.filter(hotels__in=hotels).distinct().order_by('name')
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        amenities = Amenity.objects.filter(hotels=request.user.assigned_hotel).distinct().order_by('name') if request.user.assigned_hotel else Amenity.objects.none()
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        amenities = amenities.filter(name__icontains=search)
    
    hotel_filter = request.GET.get('hotel')
    if hotel_filter:
        amenities = amenities.filter(hotels__hotel_id=hotel_filter)
    
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        amenities = amenities.filter(is_active=True)
    elif status_filter == 'inactive':
        amenities = amenities.filter(is_active=False)
    
    context = {
        'amenities': amenities,
        'hotels': hotels,
    }
    return render(request, 'configurations/amenity_list.html', context)

@login_required
def amenity_create(request):
    # Check if user has permission to create configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_add_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to create configurations.')
        return redirect('configurations:amenity_list')
    if request.method == 'POST':
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            amenity = Amenity.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                icon=request.POST.get('icon', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                amenity.hotels.add(hotel)
            
            messages.success(request, f'Amenity "{amenity.name}" created for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:amenity_list')
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
        default_hotel = None
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        default_hotel = hotels.first()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        default_hotel = request.user.assigned_hotel
    
    return render(request, 'configurations/amenity_form.html', {'hotels': hotels, 'default_hotel': default_hotel})

@login_required
def amenity_detail(request, pk):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    amenity = get_object_or_404(Amenity, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    context = {
        'amenity': amenity,
    }
    return render(request, 'configurations/amenity_detail.html', context)

def amenity_edit(request, pk):
    # Check if user has permission to edit configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_change_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to edit configurations.')
        return redirect('configurations:amenity_list')
    amenity = get_object_or_404(Amenity, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    if request.method == 'POST':
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            amenity.name = request.POST.get('name')
            amenity.description = request.POST.get('description', '')
            amenity.icon = request.POST.get('icon', '')
            amenity.is_active = request.POST.get('is_active') == 'on'
            amenity.save()
            
            amenity.hotels.clear()
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                amenity.hotels.add(hotel)
            
            messages.success(request, f'Amenity "{amenity.name}" updated for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:amenity_list')
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/amenity_form.html', {'amenity': amenity, 'hotels': hotels})

@login_required
def bulk_import(request):
    if not (request.user.is_superuser or request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to import configurations.')
        return redirect('configurations:room_type_list')
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        try:
            csv_file = request.FILES['csv_file']
            hotel_ids = request.POST.getlist('hotels')
            
            if not hotel_ids:
                messages.error(request, 'Please select at least one hotel.')
                return redirect('configurations:bulk_import')
            
            # Read CSV file
            file_data = csv_file.read().decode('utf-8')
            lines = file_data.split('\n')
            reader = csv.DictReader(lines)
            
            created_counts = {'total': 0}
            skipped_counts = {'total': 0}
            
            for row in reader:
                if not row.get('Type') or not row.get('Name'):
                    continue
                    
                config_type = row['Type'].strip().lower()
                name = row['Name'].strip()
                description = row.get('Description', '').strip()
                
                if config_type == 'roomtype':
                    if RoomType.objects.filter(name=name).exists():
                        skipped_counts['total'] += 1
                        continue
                    room_type = RoomType.objects.create(name=name, description=description)
                    created_counts['total'] += 1
                    for hotel_id in hotel_ids:
                        hotel = Hotel.objects.get(hotel_id=hotel_id)
                        room_type.hotels.add(hotel)
                        
                elif config_type == 'roomcategory':
                    if RoomCategory.objects.filter(name=name).exists():
                        skipped_counts['total'] += 1
                        continue
                    max_occupancy = int(row.get('Max_Occupancy', 2))
                    category = RoomCategory.objects.create(
                        name=name,
                        description=description,
                        max_occupancy=max_occupancy
                    )
                    created_counts['total'] += 1
                    for hotel_id in hotel_ids:
                        hotel = Hotel.objects.get(hotel_id=hotel_id)
                        category.hotels.add(hotel)
                        
                elif config_type == 'bedtype':
                    if BedType.objects.filter(name=name).exists():
                        skipped_counts['total'] += 1
                        continue
                    usage = row.get('Usage', '').strip()
                    bed_type = BedType.objects.create(
                        name=name,
                        description=description,
                        usage=usage
                    )
                    created_counts['total'] += 1
                    for hotel_id in hotel_ids:
                        hotel = Hotel.objects.get(hotel_id=hotel_id)
                        bed_type.hotels.add(hotel)
                        
                elif config_type == 'floor':
                    if Floor.objects.filter(name=name).exists():
                        skipped_counts['total'] += 1
                        continue
                    try:
                        number = int(float(row.get('Number', 1)))
                    except (ValueError, TypeError):
                        number = 1
                    floor = Floor.objects.create(
                        name=name,
                        description=description,
                        number=number
                    )
                    created_counts['total'] += 1
                    for hotel_id in hotel_ids:
                        hotel = Hotel.objects.get(hotel_id=hotel_id)
                        floor.hotels.add(hotel)
                        
                elif config_type == 'amenity':
                    if Amenity.objects.filter(name=name).exists():
                        skipped_counts['total'] += 1
                        continue
                    icon = row.get('Icon', 'fas fa-star').strip()
                    amenity = Amenity.objects.create(
                        name=name,
                        description=description,
                        icon=icon
                    )
                    created_counts['total'] += 1
                    for hotel_id in hotel_ids:
                        hotel = Hotel.objects.get(hotel_id=hotel_id)
                        amenity.hotels.add(hotel)
            
            if created_counts['total'] > 0:
                messages.success(request, f'Import completed! Created {created_counts["total"]} configurations. Skipped {skipped_counts["total"]} duplicates.')
            else:
                messages.info(request, f'No new items were created. Skipped {skipped_counts["total"]} existing configurations.')
            return redirect('configurations:room_type_list')
            
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
    
    if request.user.is_superuser:
        hotels = Hotel.objects.all().order_by('name')
    else:
        hotels = Hotel.objects.filter(owner=request.user).order_by('name')
    
    return render(request, 'configurations/bulk_import.html', {'hotels': hotels})

@login_required
def download_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hotel_configurations_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Type', 'Name', 'Description', 'Max_Occupancy', 'Usage', 'Number', 'Icon'])
    
    # Room Types
    room_types = [
        ['RoomType', 'Standard Room', 'Basic accommodation with essential amenities'],
        ['RoomType', 'Deluxe Room', 'Enhanced comfort room with premium features'],
        ['RoomType', 'Suite', 'Spacious suite with separate living area'],
        ['RoomType', 'Presidential Suite', 'Luxury presidential suite with exclusive services']
    ]
    
    # Room Categories
    categories = [
        ['RoomCategory', 'Economy', 'Budget-friendly option with basic amenities', '2'],
        ['RoomCategory', 'Business', 'Business traveler focused with work facilities', '2'],
        ['RoomCategory', 'Premium', 'Premium experience with enhanced comfort', '4'],
        ['RoomCategory', 'Luxury', 'Ultimate luxury with exclusive services', '6']
    ]
    
    # Bed Types
    bed_types = [
        ['BedType', 'Single Bed', 'Single occupancy bed for one person', '', 'Single occupancy'],
        ['BedType', 'Double Bed', 'Standard double bed for two people', '', 'Double occupancy'],
        ['BedType', 'Queen Bed', 'Queen size bed with extra comfort', '', 'Double occupancy'],
        ['BedType', 'King Bed', 'King size bed with maximum space', '', 'Double occupancy']
    ]
    
    # Floors
    floors = [
        ['Floor', 'Ground Floor', 'Main entrance level with lobby and reception', '', '', '0'],
        ['Floor', 'First Floor', 'First level above ground with standard rooms', '', '', '1'],
        ['Floor', 'Second Floor', 'Second level with standard accommodations', '', '', '2'],
        ['Floor', 'Third Floor', 'Third level with enhanced room features', '', '', '3']
    ]
    
    # Amenities
    amenities = [
        ['Amenity', 'Free Wi-Fi', 'Complimentary high-speed internet access', '', '', '', 'fas fa-wifi'],
        ['Amenity', 'Air Conditioning', 'Climate control for optimal comfort', '', '', '', 'fas fa-snowflake'],
        ['Amenity', 'TV', 'Flat screen television with cable channels', '', '', '', 'fas fa-tv'],
        ['Amenity', 'Mini Bar', 'In-room refrigerated bar with beverages', '', '', '', 'fas fa-glass-martini']
    ]
    
    for row in room_types + categories + bed_types + floors + amenities:
        writer.writerow(row)
    
    return response

@login_required
def amenity_delete(request, pk):
    if not (request.user.is_superuser or request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to delete configurations.')
        return redirect('configurations:amenity_list')
    amenity = get_object_or_404(Amenity, pk=pk)
    
    if request.method == 'POST':
        amenity.delete()
        messages.success(request, 'Amenity deleted successfully!')
        return redirect('configurations:amenity_list')
    return render(request, 'configurations/confirm_delete.html', {'object': amenity, 'type': 'Amenity'})