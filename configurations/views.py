from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RoomType, BedType, Floor, Amenity
from .forms import RoomTypeForm, BedTypeForm, FloorForm, AmenityForm
from hotels.models import Hotel
from accounts.decorators import owner_or_permission_required

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
        room_types = RoomType.objects.all().distinct()
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        room_types = RoomType.objects.filter(hotels__in=hotels).distinct()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        room_types = RoomType.objects.filter(hotels=request.user.assigned_hotel).distinct() if request.user.assigned_hotel else RoomType.objects.none()
    
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
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/room_type_form.html', {'form': form, 'hotels': hotels})

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
        bed_types = BedType.objects.all().distinct()
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        bed_types = BedType.objects.filter(hotels__in=hotels).distinct()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        bed_types = BedType.objects.filter(hotels=request.user.assigned_hotel).distinct() if request.user.assigned_hotel else BedType.objects.none()
    
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
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/bed_type_form.html', {'hotels': hotels})

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
        floors = Floor.objects.all().distinct()
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        floors = Floor.objects.filter(hotels__in=hotels).distinct()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        floors = Floor.objects.filter(hotels=request.user.assigned_hotel).distinct() if request.user.assigned_hotel else Floor.objects.none()
    
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
        hotel_id = request.POST.get('hotel')
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        
        # Check permission
        if not request.user.is_superuser and request.user.role != 'Owner' and hotel != request.user.assigned_hotel:
            messages.error(request, 'You do not have permission to create floors for this hotel.')
            return redirect('configurations:floor_list')
        
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            floor = Floor.objects.create(
                name=request.POST.get('name'),
                number=int(request.POST.get('number')),
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            
            for hotel_id in hotel_ids:
                hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                floor.hotels.add(hotel)
            
            messages.success(request, f'Floor "{floor.name}" created for {len(hotel_ids)} hotel(s)!')
            return redirect('configurations:floor_list')
        messages.success(request, 'Floor created successfully!')
        return redirect('configurations:floor_list')
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/floor_form.html', {'hotels': hotels})

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
        amenities = Amenity.objects.all().distinct()
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        amenities = Amenity.objects.filter(hotels__in=hotels).distinct()
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
        amenities = Amenity.objects.filter(hotels=request.user.assigned_hotel).distinct() if request.user.assigned_hotel else Amenity.objects.none()
    
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
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/amenity_form.html', {'hotels': hotels})

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
def amenity_delete(request, pk):
    # Check if user has permission to delete configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_delete_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to delete configurations.')
        return redirect('configurations:amenity_list')
    amenity = get_object_or_404(Amenity, pk=pk)
    
    # Check permission - skip for ManyToMany relationship
    
    if request.method == 'POST':
        amenity.delete()
        messages.success(request, 'Amenity deleted successfully!')
        return redirect('configurations:amenity_list')
    return render(request, 'configurations/confirm_delete.html', {'object': amenity, 'type': 'Amenity'})