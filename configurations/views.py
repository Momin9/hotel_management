from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RoomType, BedType, Floor, Amenity
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
    if request.user.is_superuser:
        room_types = RoomType.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        room_types = RoomType.objects.filter(hotel__in=hotels)
    else:
        room_types = RoomType.objects.filter(hotel=request.user.assigned_hotel) if request.user.assigned_hotel else RoomType.objects.none()
    
    context = {
        'room_types': room_types,
        # Permissions are now handled by context processor
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
        hotel_id = request.POST.get('hotel')
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        
        # Check permission
        if not request.user.is_superuser and request.user.role != 'Owner' and hotel != request.user.assigned_hotel:
            messages.error(request, 'You do not have permission to create room types for this hotel.')
            return redirect('configurations:room_type_list')
        
        RoomType.objects.create(
            hotel=hotel,
            name=request.POST.get('name'),
            description=request.POST.get('description', '')
        )
        messages.success(request, 'Room type created successfully!')
        return redirect('configurations:room_type_list')
    
    # Get available hotels
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/room_type_form.html', {'hotels': hotels})

@login_required
def room_type_detail(request, pk):
    # Check if user has permission to view configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_view_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to view configurations.')
        return redirect('accounts:dashboard')
    
    room_type = get_object_or_404(RoomType, pk=pk)
    
    # Check permission
    if not request.user.is_superuser and request.user.role != 'Owner' and room_type.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to view this room type.')
        return redirect('configurations:room_type_list')
    
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
    
    # Check permission
    if not request.user.is_superuser and request.user.role != 'Owner' and room_type.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to edit this room type.')
        return redirect('configurations:room_type_list')
    
    if request.method == 'POST':
        room_type.name = request.POST.get('name')
        room_type.description = request.POST.get('description', '')
        room_type.save()
        messages.success(request, 'Room type updated successfully!')
        return redirect('configurations:room_type_list')
    
    return render(request, 'configurations/room_type_form.html', {'room_type': room_type})

@login_required
def room_type_delete(request, pk):
    # Check if user has permission to delete configurations
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'employee_profile') and request.user.employee_profile.can_delete_configurations) or
            request.user.role == 'Owner'):
        messages.error(request, 'You do not have permission to delete configurations.')
        return redirect('configurations:room_type_list')
    room_type = get_object_or_404(RoomType, pk=pk)
    
    # Check permission
    if not request.user.is_superuser and request.user.role != 'Owner' and room_type.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to delete this room type.')
        return redirect('configurations:room_type_list')
    
    if request.method == 'POST':
        room_type.delete()
        messages.success(request, 'Room type deleted successfully!')
        return redirect('configurations:room_type_list')
    return render(request, 'configurations/confirm_delete.html', {'object': room_type, 'type': 'Room Type'})

# Bed Type Views
@owner_or_permission_required('view_configurations')
def bed_type_list(request):
    if request.user.is_superuser:
        bed_types = BedType.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        bed_types = BedType.objects.filter(hotel__in=hotels)
    else:
        bed_types = BedType.objects.filter(hotel=request.user.assigned_hotel) if request.user.assigned_hotel else BedType.objects.none()
    
    context = {
        'bed_types': bed_types,
        'can_add_configurations': request.user.role == 'Owner' or request.user.can_add_configurations,
        'can_change_configurations': request.user.role == 'Owner' or request.user.can_change_configurations,
        'can_delete_configurations': request.user.role == 'Owner' or request.user.can_delete_configurations,
    }
    return render(request, 'configurations/bed_type_list.html', context)

@owner_or_permission_required('add_configurations')
def bed_type_create(request):
    if request.method == 'POST':
        hotel_id = request.POST.get('hotel')
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        
        if not request.user.is_superuser and request.user.role != 'Owner' and hotel != request.user.assigned_hotel:
            messages.error(request, 'You do not have permission to create bed types for this hotel.')
            return redirect('configurations:bed_type_list')
        
        BedType.objects.create(
            hotel=hotel,
            name=request.POST.get('name'),
            description=request.POST.get('description', '')
        )
        messages.success(request, 'Bed type created successfully!')
        return redirect('configurations:bed_type_list')
    
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/bed_type_form.html', {'hotels': hotels})

@owner_or_permission_required('change_configurations')
def bed_type_edit(request, pk):
    bed_type = get_object_or_404(BedType, pk=pk)
    
    if not request.user.is_superuser and request.user.role != 'Owner' and bed_type.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to edit this bed type.')
        return redirect('configurations:bed_type_list')
    
    if request.method == 'POST':
        bed_type.name = request.POST.get('name')
        bed_type.description = request.POST.get('description', '')
        bed_type.save()
        messages.success(request, 'Bed type updated successfully!')
        return redirect('configurations:bed_type_list')
    
    return render(request, 'configurations/bed_type_form.html', {'bed_type': bed_type})

@owner_or_permission_required('delete_configurations')
def bed_type_delete(request, pk):
    bed_type = get_object_or_404(BedType, pk=pk)
    
    if not request.user.is_superuser and request.user.role != 'Owner' and bed_type.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to delete this bed type.')
        return redirect('configurations:bed_type_list')
    
    if request.method == 'POST':
        bed_type.delete()
        messages.success(request, 'Bed type deleted successfully!')
        return redirect('configurations:bed_type_list')
    return render(request, 'configurations/confirm_delete.html', {'object': bed_type, 'type': 'Bed Type'})

# Floor Views
@owner_or_permission_required('view_configurations')
def floor_list(request):
    if request.user.is_superuser:
        floors = Floor.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        floors = Floor.objects.filter(hotel__in=hotels)
    else:
        floors = Floor.objects.filter(hotel=request.user.assigned_hotel) if request.user.assigned_hotel else Floor.objects.none()
    
    context = {
        'floors': floors,
        'can_add_configurations': request.user.role == 'Owner' or request.user.can_add_configurations,
        'can_change_configurations': request.user.role == 'Owner' or request.user.can_change_configurations,
        'can_delete_configurations': request.user.role == 'Owner' or request.user.can_delete_configurations,
    }
    return render(request, 'configurations/floor_list.html', context)

@owner_or_permission_required('add_configurations')
def floor_create(request):
    if request.method == 'POST':
        hotel_id = request.POST.get('hotel')
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        
        if not request.user.is_superuser and request.user.role != 'Owner' and hotel != request.user.assigned_hotel:
            messages.error(request, 'You do not have permission to create floors for this hotel.')
            return redirect('configurations:floor_list')
        
        Floor.objects.create(
            hotel=hotel,
            name=request.POST.get('name'),
            number=int(request.POST.get('number')),
            description=request.POST.get('description', '')
        )
        messages.success(request, 'Floor created successfully!')
        return redirect('configurations:floor_list')
    
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/floor_form.html', {'hotels': hotels})

@owner_or_permission_required('change_configurations')
def floor_edit(request, pk):
    floor = get_object_or_404(Floor, pk=pk)
    
    if not request.user.is_superuser and request.user.role != 'Owner' and floor.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to edit this floor.')
        return redirect('configurations:floor_list')
    
    if request.method == 'POST':
        floor.name = request.POST.get('name')
        floor.number = int(request.POST.get('number'))
        floor.description = request.POST.get('description', '')
        floor.save()
        messages.success(request, 'Floor updated successfully!')
        return redirect('configurations:floor_list')
    
    return render(request, 'configurations/floor_form.html', {'floor': floor})

@owner_or_permission_required('delete_configurations')
def floor_delete(request, pk):
    floor = get_object_or_404(Floor, pk=pk)
    
    if not request.user.is_superuser and request.user.role != 'Owner' and floor.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to delete this floor.')
        return redirect('configurations:floor_list')
    
    if request.method == 'POST':
        floor.delete()
        messages.success(request, 'Floor deleted successfully!')
        return redirect('configurations:floor_list')
    return render(request, 'configurations/confirm_delete.html', {'object': floor, 'type': 'Floor'})

# Amenity Views
@owner_or_permission_required('view_configurations')
def amenity_list(request):
    if request.user.is_superuser:
        amenities = Amenity.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
        amenities = Amenity.objects.filter(hotel__in=hotels)
    else:
        amenities = Amenity.objects.filter(hotel=request.user.assigned_hotel) if request.user.assigned_hotel else Amenity.objects.none()
    
    context = {
        'amenities': amenities,
        'can_add_configurations': request.user.role == 'Owner' or request.user.can_add_configurations,
        'can_change_configurations': request.user.role == 'Owner' or request.user.can_change_configurations,
        'can_delete_configurations': request.user.role == 'Owner' or request.user.can_delete_configurations,
    }
    return render(request, 'configurations/amenity_list.html', context)

@owner_or_permission_required('add_configurations')
def amenity_create(request):
    if request.method == 'POST':
        hotel_id = request.POST.get('hotel')
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        
        if not request.user.is_superuser and request.user.role != 'Owner' and hotel != request.user.assigned_hotel:
            messages.error(request, 'You do not have permission to create amenities for this hotel.')
            return redirect('configurations:amenity_list')
        
        Amenity.objects.create(
            hotel=hotel,
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            icon=request.POST.get('icon', '')
        )
        messages.success(request, 'Amenity created successfully!')
        return redirect('configurations:amenity_list')
    
    if request.user.is_superuser:
        hotels = Hotel.objects.all()
    elif request.user.role == 'Owner':
        hotels = Hotel.objects.filter(owner=request.user)
    else:
        hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    return render(request, 'configurations/amenity_form.html', {'hotels': hotels})

@owner_or_permission_required('change_configurations')
def amenity_edit(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    
    if not request.user.is_superuser and request.user.role != 'Owner' and amenity.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to edit this amenity.')
        return redirect('configurations:amenity_list')
    
    if request.method == 'POST':
        amenity.name = request.POST.get('name')
        amenity.description = request.POST.get('description', '')
        amenity.icon = request.POST.get('icon', '')
        amenity.save()
        messages.success(request, 'Amenity updated successfully!')
        return redirect('configurations:amenity_list')
    
    return render(request, 'configurations/amenity_form.html', {'amenity': amenity})

@owner_or_permission_required('delete_configurations')
def amenity_delete(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    
    if not request.user.is_superuser and request.user.role != 'Owner' and amenity.hotel != request.user.assigned_hotel:
        messages.error(request, 'You do not have permission to delete this amenity.')
        return redirect('configurations:amenity_list')
    
    if request.method == 'POST':
        amenity.delete()
        messages.success(request, 'Amenity deleted successfully!')
        return redirect('configurations:amenity_list')
    return render(request, 'configurations/confirm_delete.html', {'object': amenity, 'type': 'Amenity'})