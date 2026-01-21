from datetime import date

from accounts.decorators import owner_or_permission_required
from accounts.roles import RoleManager
from billing.models import Payment
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum, Q
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404

from .models import Hotel, Room, Service, Floor, RoomCategory, Company
from .activity_models import RoomActivityLog
from .google_drive_forms import GoogleDriveConfigForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
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
    """List rooms for a hotel with filtering"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    rooms = hotel_obj.rooms.all()
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        rooms = rooms.filter(
            Q(room_number__icontains=search) |
            Q(room_type__name__icontains=search)
        )
    
    status = request.GET.get('status')
    if status:
        rooms = rooms.filter(status=status)
    
    room_type = request.GET.get('room_type')
    if room_type:
        rooms = rooms.filter(room_type_id=room_type)
    
    floor = request.GET.get('floor')
    if floor:
        rooms = rooms.filter(floor_id=floor)
    
    min_price = request.GET.get('min_price')
    if min_price:
        rooms = rooms.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        rooms = rooms.filter(price__lte=max_price)
    
    max_guests = request.GET.get('max_guests')
    if max_guests:
        if max_guests == '4':
            rooms = rooms.filter(max_guests__gte=4)
        else:
            rooms = rooms.filter(max_guests=max_guests)
    
    # Get filter options
    from configurations.models import RoomType, Floor as ConfigFloor
    room_types = RoomType.objects.filter(hotels=hotel_obj).order_by('name')
    floors = ConfigFloor.objects.filter(hotels=hotel_obj).order_by('name')
    
    # Check permissions for room management
    can_add_room = request.user.role == 'Owner' or request.user.can_add_rooms
    can_change_room = request.user.role == 'Owner' or request.user.can_change_rooms
    can_delete_room = request.user.role == 'Owner' or request.user.can_delete_rooms
    
    return render(request, 'hotels/room_list_enhanced.html', {
        'hotel': hotel_obj,
        'rooms': rooms,
        'room_types': room_types,
        'floors': floors,
        'can_add_room': can_add_room,
        'can_change_room': can_change_room,
        'can_delete_room': can_delete_room
    })


@owner_or_permission_required('add_room')
def room_create(request, hotel_id):
    """Create new room"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')

    if request.method == 'POST':
        # Create new room
        room = Room.objects.create(
            hotel=hotel_obj,
            room_number=request.POST.get('room_number'),
            price=request.POST.get('price', 0),
            status=request.POST.get('status', 'Available')
        )
        
        # Handle foreign key relationships
        room_type_id = request.POST.get('room_type')
        if room_type_id:
            from configurations.models import RoomType
            room.room_type = RoomType.objects.get(id=room_type_id)
        
        bed_type_id = request.POST.get('bed_type')
        if bed_type_id:
            from configurations.models import BedType
            room.bed_type = BedType.objects.get(id=bed_type_id)
        
        floor_id = request.POST.get('floor')
        if floor_id:
            from configurations.models import Floor
            room.floor = Floor.objects.get(id=floor_id)
        
        room.save()
        
        # Handle amenities
        amenity_ids = request.POST.getlist('amenities')
        room.amenities.set(amenity_ids)
        
        # Handle services
        service_ids = request.POST.getlist('services')
        room.services.set(service_ids)
        
        messages.success(request, f'Room {room.room_number} created successfully!')
        return redirect('hotels:room_list', hotel_id=hotel_id)

    # Get configuration data for the hotel
    from configurations.models import Amenity, RoomType, RoomCategory, BedType, Floor
    amenities = Amenity.objects.filter(hotels=hotel_obj, is_active=True).order_by('name')
    room_types = RoomType.objects.filter(hotels=hotel_obj).order_by('name')
    room_categories = RoomCategory.objects.filter(hotels=hotel_obj).order_by('name')
    bed_types = BedType.objects.filter(hotels=hotel_obj).order_by('name')
    floors = Floor.objects.filter(hotels=hotel_obj).order_by('name')
    services = hotel_obj.services.all().order_by('name')
    
    return render(request, 'hotels/room_form.html', {
        'hotel': hotel_obj,
        'amenities': amenities,
        'room_types': room_types,
        'room_categories': room_categories,
        'bed_types': bed_types,
        'floors': floors,
        'services': services
    })

@owner_or_permission_required('view_room')
def room_detail(request, hotel_id, room_id):
    """Room detail view with activity log"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    room = get_object_or_404(Room, room_id=room_id, hotel=hotel_obj)
    
    # Get room activity logs
    activities = room.activity_logs.all()[:20]  # Last 20 activities
    
    return render(request, 'hotels/room_detail.html', {
        'hotel': hotel_obj,
        'room': room,
        'activities': activities
    })

@owner_or_permission_required('change_room')
def room_edit(request, hotel_id, room_id):
    """Edit room"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check if user has access to this hotel
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    room = get_object_or_404(Room, room_id=room_id, hotel=hotel_obj)
    
    if request.method == 'POST':
        # Handle manual form submission
        room.room_number = request.POST.get('room_number')
        room.price = request.POST.get('price')
        room.status = request.POST.get('status')
        
        # Handle foreign key relationships
        room_type_id = request.POST.get('room_type')
        if room_type_id:
            from configurations.models import RoomType
            room.room_type = RoomType.objects.get(id=room_type_id)
        
        bed_type_id = request.POST.get('bed_type')
        if bed_type_id:
            from configurations.models import BedType
            room.bed_type = BedType.objects.get(id=bed_type_id)
        
        floor_id = request.POST.get('floor')
        if floor_id:
            from configurations.models import Floor
            room.floor = Floor.objects.get(id=floor_id)
        
        room.save()
        
        # Handle amenities
        amenity_ids = request.POST.getlist('amenities')
        room.amenities.set(amenity_ids)
        
        # Handle services
        service_ids = request.POST.getlist('services')
        room.services.set(service_ids)
        
        messages.success(request, f'Room {room.room_number} updated successfully!')
        return redirect('hotels:room_detail', hotel_id=hotel_id, room_id=room_id)
    
    # Get configuration data for the hotel
    from configurations.models import Amenity, RoomType, BedType, Floor
    amenities = Amenity.objects.filter(hotels=hotel_obj, is_active=True).order_by('name')
    room_types = RoomType.objects.filter(hotels=hotel_obj).order_by('name')
    bed_types = BedType.objects.filter(hotels=hotel_obj).order_by('name')
    floors = Floor.objects.filter(hotels=hotel_obj).order_by('name')
    services = hotel_obj.services.all().order_by('name')
    
    return render(request, 'hotels/room_form.html', {
        'hotel': hotel_obj,
        'room': room,
        'amenities': amenities,
        'room_types': room_types,
        'bed_types': bed_types,
        'floors': floors,
        'services': services
    })

# Floor Management Views
@owner_or_permission_required('view_hotel')
def floor_list(request, hotel_id):
    """List floors for a hotel"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    floors = hotel_obj.floors.all().order_by('floor_number')
    return render(request, 'hotels/floor_list.html', {
        'hotel': hotel_obj,
        'floors': floors
    })

@owner_or_permission_required('add_hotel')
def floor_create(request, hotel_id):
    """Create new floor"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        floor_number = request.POST.get('floor_number')
        floor_name = request.POST.get('floor_name')
        
        # Check if floor number already exists
        if Floor.objects.filter(hotels=hotel_obj, floor_number=floor_number).exists():
            messages.error(request, f'Floor {floor_number} already exists in this hotel.')
        else:
            Floor.objects.create(
                hotel=hotel_obj,
                floor_number=floor_number,
                floor_name=floor_name,
                description=request.POST.get('description', '')
            )
            messages.success(request, f'Floor "{floor_name}" created successfully!')
            return redirect('hotels:floor_list', hotel_id=hotel_id)
    
    return render(request, 'hotels/floor_form.html', {'hotel': hotel_obj})

@owner_or_permission_required('change_hotel')
def floor_edit(request, hotel_id, floor_id):
    """Edit floor"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    floor = get_object_or_404(Floor, id=floor_id, hotel=hotel_obj)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        new_floor_number = request.POST.get('floor_number')
        
        # Check if floor number already exists (excluding current floor)
        if Floor.objects.filter(hotels=hotel_obj, floor_number=new_floor_number).exclude(id=floor_id).exists():
            messages.error(request, f'Floor {new_floor_number} already exists in this hotel.')
        else:
            floor.floor_number = new_floor_number
            floor.floor_name = request.POST.get('floor_name')
            floor.description = request.POST.get('description', '')
            floor.save()
            messages.success(request, f'Floor "{floor.floor_name}" updated successfully!')
            return redirect('hotels:floor_list', hotel_id=hotel_id)
    
    return render(request, 'hotels/floor_form.html', {
        'hotel': hotel_obj,
        'floor': floor
    })

# Room Category Management Views
@owner_or_permission_required('view_hotel')
def room_category_list(request, hotel_id):
    """List room categories for a hotel"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    categories = hotel_obj.room_categories.all()
    return render(request, 'hotels/room_category_list.html', {
        'hotel': hotel_obj,
        'categories': categories
    })

@owner_or_permission_required('add_hotel')
def room_category_create(request, hotel_id):
    """Create new room category"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        
        # Check if category name already exists
        if RoomCategory.objects.filter(hotels=hotel_obj, name=name).exists():
            messages.error(request, f'Room category "{name}" already exists in this hotel.')
        else:
            RoomCategory.objects.create(
                hotel=hotel_obj,
                name=name,
                description=request.POST.get('description', ''),
                base_price_multiplier=request.POST.get('base_price_multiplier', 1.00),
                amenities=request.POST.get('amenities', '')
            )
            messages.success(request, f'Room category "{name}" created successfully!')
            return redirect('hotels:room_category_list', hotel_id=hotel_id)
    
    return render(request, 'hotels/room_category_form.html', {'hotel': hotel_obj})

@owner_or_permission_required('change_hotel')
def room_category_edit(request, hotel_id, category_id):
    """Edit room category"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    category = get_object_or_404(RoomCategory, id=category_id, hotel=hotel_obj)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        new_name = request.POST.get('name')
        
        # Check if category name already exists (excluding current category)
        if RoomCategory.objects.filter(hotels=hotel_obj, name=new_name).exclude(id=category_id).exists():
            messages.error(request, f'Room category "{new_name}" already exists in this hotel.')
        else:
            category.name = new_name
            category.description = request.POST.get('description', '')
            category.base_price_multiplier = request.POST.get('base_price_multiplier', 1.00)
            category.amenities = request.POST.get('amenities', '')
            category.save()
            messages.success(request, f'Room category "{category.name}" updated successfully!')
            return redirect('hotels:room_category_list', hotel_id=hotel_id)
    
    return render(request, 'hotels/room_category_form.html', {
        'hotel': hotel_obj,
        'category': category
    })

# Company Management Views
@owner_or_permission_required('view_hotel')
def company_list(request, hotel_id):
    """List companies for a hotel with filtering"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    companies = hotel_obj.companies.all()
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        companies = companies.filter(
            Q(name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(email__icontains=search)
        )
    
    is_active = request.GET.get('is_active')
    if is_active == 'true':
        companies = companies.filter(is_active=True)
    elif is_active == 'false':
        companies = companies.filter(is_active=False)
    
    min_discount = request.GET.get('min_discount')
    if min_discount:
        companies = companies.filter(discount_percentage__gte=min_discount)
    
    companies = companies.order_by('name')
    
    # Check permissions
    can_add_companies = request.user.role == 'Owner' or getattr(request.user, 'can_add_companies', False)
    can_change_companies = request.user.role == 'Owner' or getattr(request.user, 'can_change_companies', False)
    can_delete_companies = request.user.role == 'Owner' or getattr(request.user, 'can_delete_companies', False)
    
    return render(request, 'hotels/company_list.html', {
        'hotel': hotel_obj,
        'companies': companies,
        'can_add_companies': can_add_companies,
        'can_change_companies': can_change_companies,
        'can_delete_companies': can_delete_companies
    })

@owner_or_permission_required('add_hotel')
def company_create(request, hotel_id):
    """Create new company"""
    from .forms import CompanyForm
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        selected_hotel_id = request.POST.get('hotel', hotel_id)
        selected_hotel = get_object_or_404(Hotel, hotel_id=selected_hotel_id)
        
        form = CompanyForm(request.POST, hotel=selected_hotel)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Company.objects.filter(hotels=selected_hotel, name=name).exists():
                messages.error(request, f'Company "{name}" already exists in this hotel.')
            else:
                company = form.save(commit=False)
                company.hotel = selected_hotel
                company.save()
                form.save_m2m()
                messages.success(request, f'Company "{company.name}" created successfully!')
                return redirect('hotels:company_list', hotel_id=selected_hotel_id)
    else:
        form = CompanyForm(hotel=hotel_obj)
    
    # Get available hotels based on user role
    if user_role == 'SUPER_ADMIN':
        available_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        available_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    else:
        available_hotels = [hotel_obj] if hotel_obj else []
    
    return render(request, 'hotels/company_form.html', {
        'hotel': hotel_obj, 
        'form': form, 
        'available_hotels': available_hotels
    })

@owner_or_permission_required('change_hotel')
def company_edit(request, hotel_id, company_id):
    """Edit company"""
    from .forms import CompanyForm
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    company = get_object_or_404(Company, id=company_id, hotel=hotel_obj)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company, hotel=hotel_obj)
        if form.is_valid():
            new_name = form.cleaned_data['name']
            if Company.objects.filter(hotels=hotel_obj, name=new_name).exclude(id=company_id).exists():
                messages.error(request, f'Company "{new_name}" already exists in this hotel.')
            else:
                form.save()
                messages.success(request, f'Company "{company.name}" updated successfully!')
                return redirect('hotels:company_list', hotel_id=hotel_id)
    else:
        form = CompanyForm(instance=company, hotel=hotel_obj)
    
    # Get available hotels for edit (read-only for non-owners)
    if user_role == 'SUPER_ADMIN':
        available_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        available_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    else:
        available_hotels = [hotel_obj]
    
    return render(request, 'hotels/company_form.html', {
        'hotel': hotel_obj,
        'company': company,
        'form': form,
        'available_hotels': available_hotels
    })

# Service Management Views
@owner_or_permission_required('view_hotel')
def service_list(request, hotel_id):
    """List services for a hotel with filtering"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    services = hotel_obj.services.all()
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        services = services.filter(name__icontains=search)
    
    min_price = request.GET.get('min_price')
    if min_price:
        services = services.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        services = services.filter(price__lte=max_price)
    
    services = services.order_by('name')
    
    return render(request, 'hotels/service_list.html', {
        'hotel': hotel_obj,
        'services': services
    })

@owner_or_permission_required('view_hotel')
def service_detail(request, hotel_id, service_id):
    """View service details"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    service = get_object_or_404(Service, service_id=service_id, hotels=hotel_obj)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    return render(request, 'hotels/service_detail.html', {
        'hotel': hotel_obj,
        'service': service
    })

@owner_or_permission_required('add_hotel')
def service_create(request, hotel_id):
    """Create new service"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            price = request.POST.get('price', 0)
            
            service = Service.objects.create(
                name=name,
                description=description,
                price=price,
                is_active=request.POST.get('is_active') == 'on'
            )
            
            for hotel_id_str in hotel_ids:
                selected_hotel = get_object_or_404(Hotel, hotel_id=hotel_id_str)
                service.hotels.add(selected_hotel)
            
            messages.success(request, f'Service "{name}" created for {len(hotel_ids)} hotel(s)!')
            return redirect('hotels:service_list', hotel_id=hotel_id)
    
    # Get available hotels for dropdown
    if user_role == 'SUPER_ADMIN':
        available_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    else:
        available_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    
    return render(request, 'hotels/service_form.html', {
        'hotel': hotel_obj,
        'available_hotels': available_hotels
    })

@owner_or_permission_required('change_hotel')
def service_edit(request, hotel_id, service_id):
    """Edit service"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    service = get_object_or_404(Service, service_id=service_id, hotels=hotel_obj)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        hotel_ids = request.POST.getlist('hotels')
        
        if not hotel_ids:
            messages.error(request, 'Please select at least one hotel.')
        else:
            service.name = request.POST.get('name')
            service.description = request.POST.get('description', '')
            service.price = request.POST.get('price', 0)
            service.is_active = request.POST.get('is_active') == 'on'
            service.save()
            
            service.hotels.clear()
            for hotel_id_str in hotel_ids:
                selected_hotel = get_object_or_404(Hotel, hotel_id=hotel_id_str)
                service.hotels.add(selected_hotel)
            
            messages.success(request, f'Service "{service.name}" updated for {len(hotel_ids)} hotel(s)!')
            return redirect('hotels:service_list', hotel_id=hotel_id)
    
    # Get available hotels for dropdown
    if user_role == 'SUPER_ADMIN':
        available_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    else:
        available_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    
    return render(request, 'hotels/service_form.html', {
        'hotel': hotel_obj,
        'service': service,
        'available_hotels': available_hotels
    })

@owner_or_permission_required('change_hotel')
def service_delete(request, hotel_id, service_id):
    """Delete service"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    service = get_object_or_404(Service, service_id=service_id, hotels=hotel_obj)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        hotel_obj.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == hotel_id)
    )
    
    if not has_access:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    service_name = service.name
    service.delete()
    
    messages.success(request, f'Service "{service_name}" deleted successfully!')
    return redirect('hotels:service_list', hotel_id=hotel_id)

@owner_or_permission_required('change_hotel')
def google_drive_config(request, hotel_id):
    """Configure Google Drive integration for hotel"""
    hotel_obj = get_object_or_404(Hotel, hotel_id=hotel_id)
    
    # Check access
    user_role = RoleManager.get_user_role(request.user)
    if user_role != 'SUPER_ADMIN' and hotel_obj.owner != request.user:
        messages.error(request, 'You do not have access to this hotel.')
        return redirect('hotels:hotel_list')
    
    if request.method == 'POST':
        form = GoogleDriveConfigForm(request.POST, instance=hotel_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Google Drive configuration updated successfully!')
            return redirect('hotels:hotel_detail', hotel_id=hotel_id)
    else:
        form = GoogleDriveConfigForm(instance=hotel_obj)
    
    return render(request, 'hotels/google_drive_config.html', {
        'hotel': hotel_obj,
        'form': form
    })

@login_required
@require_POST
def add_room_note(request, room_id):
    """Add a note to room activity log"""
    room = get_object_or_404(Room, room_id=room_id)
    
    # Check if user has access to this room's hotel
    user_role = RoleManager.get_user_role(request.user)
    has_access = (
        user_role == 'SUPER_ADMIN' or 
        room.hotel.owner == request.user or
        (request.user.assigned_hotel and request.user.assigned_hotel.hotel_id == room.hotel.hotel_id)
    )
    
    if not has_access:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    note = request.POST.get('note', '').strip()
    if not note:
        return JsonResponse({'success': False, 'error': 'Note cannot be empty'})
    
    # Create activity log entry
    RoomActivityLog.log_activity(
        room=room,
        user=request.user,
        action='note_added',
        description=note
    )
    
    return JsonResponse({'success': True})
