from datetime import date

from accounts.decorators import owner_or_permission_required
from accounts.roles import RoleManager
from billing.models import Payment
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from .models import Hotel, Room, Service

try:
    from crm.models import GuestProfile
except ImportError:
    GuestProfile = None


@login_required
def hotel_dashboard(request):
    """Role-based dashboard redirect"""
    user_role = RoleManager.get_user_role(request.user)

    if user_role == 'SUPER_ADMIN':
        return redirect('accounts:super_admin_dashboard')
    elif user_role in ['HOTEL_OWNER', 'HOTEL_MANAGER']:
        return redirect('accounts:owner_dashboard')
    else:
        return redirect('accounts:employee_dashboard')


@owner_or_permission_required('view_hotel')
def hotel_overview(request):
    """Role-based dashboard with real data"""

    # Get real statistics based on user role
    user_role = RoleManager.get_user_role(request.user)
    
    if user_role == 'SUPER_ADMIN':
        # Super admin sees all data
        total_rooms = Room.objects.count()
        occupied_rooms = Room.objects.filter(status='Occupied').count()
        available_rooms = Room.objects.filter(status='Available').count()
        dirty_rooms = Room.objects.filter(status='Cleaning').count()
        maintenance_rooms = Room.objects.filter(status='Maintenance').count()
        hotels = Hotel.objects.filter(is_active=True, deleted_at__isnull=True)
    else:
        # Hotel owners see only their hotels' data
        user_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
        total_rooms = Room.objects.filter(hotel__in=user_hotels).count()
        occupied_rooms = Room.objects.filter(hotel__in=user_hotels, status='Occupied').count()
        available_rooms = Room.objects.filter(hotel__in=user_hotels, status='Available').count()
        dirty_rooms = Room.objects.filter(hotel__in=user_hotels, status='Cleaning').count()
        maintenance_rooms = Room.objects.filter(hotel__in=user_hotels, status='Maintenance').count()
        hotels = user_hotels.filter(is_active=True)

    # Calculate occupancy rate
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    # Get today's revenue from payments
    today = date.today()
    try:
        daily_revenue = Payment.objects.filter(
            timestamp__date=today,
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Get this month's revenue
        month_start = today.replace(day=1)
        monthly_revenue = Payment.objects.filter(
            timestamp__date__gte=month_start,
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    except:
        daily_revenue = 0
        monthly_revenue = 0

    # Get guests count
    total_guests = GuestProfile.objects.filter(deleted_at__isnull=True).count() if GuestProfile else 0

    # Recent activities
    recent_activities = [
        {'icon': 'fa-user-check', 'color': 'green', 'text': f'{occupied_rooms} rooms currently occupied',
         'time': 'Live data'},
        {'icon': 'fa-broom', 'color': 'blue', 'text': f'{dirty_rooms} rooms need cleaning', 'time': 'Live data'},
        {'icon': 'fa-tools', 'color': 'orange', 'text': f'{maintenance_rooms} rooms under maintenance',
         'time': 'Live data'},
        {'icon': 'fa-users', 'color': 'purple', 'text': f'{total_guests} total guests in system', 'time': 'Live data'},
    ]

    context = {
        'hotels': hotels,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'dirty_rooms': dirty_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': round(occupancy_rate, 1),
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
        'total_guests': total_guests,
        'recent_activities': recent_activities,
        'user_role': RoleManager.get_user_role(request.user).replace('_', ' ').title(),
    }

    return render(request, 'hotels/dashboard_luxury.html', context)


@owner_or_permission_required('view_hotel')
def hotel_list(request):
    """List hotels based on user role"""
    user_role = RoleManager.get_user_role(request.user)
    
    if user_role == 'SUPER_ADMIN':
        hotels = Hotel.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        # Hotel owners see only their hotels
        hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    else:
        # Staff see only their assigned hotel
        if request.user.assigned_hotel:
            hotels = Hotel.objects.filter(hotel_id=request.user.assigned_hotel.hotel_id, deleted_at__isnull=True)
        else:
            hotels = Hotel.objects.none()
    
    return render(request, 'hotels/hotel_list.html', {'hotels': hotels})


@owner_or_permission_required('add_hotel')
def hotel_create(request):
    """Create new hotel"""
    if request.method == 'POST':
        # Create hotel from form data
        hotel_obj = Hotel.objects.create(
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            is_active=True
        )

        messages.success(request, f'Hotel "{hotel_obj.name}" created successfully!')
        return redirect('hotels:hotel_list')

    return render(request, 'hotels/hotel_form.html')


@owner_or_permission_required('view_hotel')
@csrf_protect
def hotel_detail(request, hotel_id):
    """Hotel detail/settings page"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        hotel_obj.name = request.POST.get('name')
        hotel_obj.address = request.POST.get('address')
        hotel_obj.city = request.POST.get('city')
        hotel_obj.country = request.POST.get('country')
        hotel_obj.phone = request.POST.get('phone')
        hotel_obj.email = request.POST.get('email')
        hotel_obj.is_active = request.POST.get('is_active') == 'on'
        hotel_obj.save()
        
        messages.success(request, f'Hotel "{hotel_obj.name}" updated successfully!')
        return redirect('hotels:hotel_detail', hotel_id=hotel_id)
    
    return render(request, 'hotels/hotel_detail.html', {'hotel': hotel_obj})


@owner_or_permission_required('view_room')
def room_list(request, hotel_id):
    """List rooms for a hotel with modern UI"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    if user_role not in ['SUPER_ADMIN', 'FRONT_DESK', 'HOUSEKEEPING'] and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    rooms = hotel_obj.rooms.all()
    return render(request, 'hotels/room_list_modern.html', {
        'hotel': hotel_obj,
        'rooms': rooms
    })


@owner_or_permission_required('add_room')
def room_create(request, hotel_id):
    """Create new room"""
    from django.db import IntegrityError
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')

    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        
        # Check if room number already exists
        if Room.objects.filter(hotel=hotel_obj, room_number=room_number).exists():
            messages.error(request, f'Room number {room_number} already exists in this hotel. Please choose a different room number.')
            services = Service.objects.filter(hotel=hotel_obj)
            return render(request, 'hotels/room_form.html', {
                'hotel': hotel_obj,
                'services': services
            })
        
        try:
            room = Room.objects.create(
                hotel=hotel_obj,
                room_number=room_number,
                type=request.POST.get('type', 'Single'),
                category=request.POST.get('category', 'Standard'),
                bed=request.POST.get('bed', 'DoubleBed'),
                price=request.POST.get('price', 0),
                status=request.POST.get('status', 'Available')
            )
            
            # Handle services
            selected_services = request.POST.getlist('services')
            if selected_services:
                room.services.set(selected_services)

            messages.success(request, f'Room {room.room_number} created successfully!')
            return redirect('hotels:room_list', hotel_id=hotel_id)
        except IntegrityError:
            messages.error(request, f'Room number {room_number} already exists in this hotel. Please choose a different room number.')

    services = Service.objects.filter(hotel=hotel_obj)
    return render(request, 'hotels/room_form.html', {
        'hotel': hotel_obj,
        'services': services
    })

@owner_or_permission_required('view_room')
def room_detail(request, hotel_id, room_id):
    """Room detail view"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    room = get_object_or_404(Room, room_id=room_id, hotel=hotel_obj)
    return render(request, 'hotels/room_detail.html', {
        'hotel': hotel_obj,
        'room': room
    })

@owner_or_permission_required('change_room')
def room_edit(request, hotel_id, room_id):
    """Edit room"""
    from django.db import IntegrityError
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    room = get_object_or_404(Room, room_id=room_id, hotel=hotel_obj)
    
    if request.method == 'POST':
        new_room_number = request.POST.get('room_number')
        
        # Check if room number already exists (excluding current room)
        if Room.objects.filter(hotel=hotel_obj, room_number=new_room_number).exclude(room_id=room_id).exists():
            messages.error(request, f'Room number {new_room_number} already exists in this hotel. Please choose a different room number.')
            services = Service.objects.filter(hotel=hotel_obj)
            return render(request, 'hotels/room_form.html', {
                'hotel': hotel_obj,
                'room': room,
                'services': services
            })
        
        try:
            room.room_number = new_room_number
            room.type = request.POST.get('type')
            room.category = request.POST.get('category')
            room.bed = request.POST.get('bed')
            room.price = request.POST.get('price')
            room.status = request.POST.get('status')
            room.save()
            
            # Handle services
            selected_services = request.POST.getlist('services')
            room.services.set(selected_services)
            
            messages.success(request, f'Room {room.room_number} updated successfully!')
            return redirect('hotels:room_detail', hotel_id=hotel_id, room_id=room_id)
        except IntegrityError:
            messages.error(request, f'Room number {new_room_number} already exists in this hotel. Please choose a different room number.')
    
    services = Service.objects.filter(hotel=hotel_obj)
    return render(request, 'hotels/room_form.html', {
        'hotel': hotel_obj,
        'room': room,
        'services': services
    })
