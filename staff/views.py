from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User
from accounts.roles import RoleManager
from accounts.email_utils import send_employee_welcome_email
from accounts.permissions import assign_default_permissions, get_permission_categories, check_user_permission
from accounts.decorators import owner_or_permission_required
from hotels.models import Hotel
from django.contrib.auth.models import Permission

@owner_or_permission_required('view_staff')
def staff_list(request):
    """List staff based on user role (excluding soft-deleted)"""
    from django.db.models import Q
    
    user_role = RoleManager.get_user_role(request.user)
    
    # Base queryset - exclude soft-deleted users
    base_queryset = User.objects.exclude(role='Owner').exclude(is_superuser=True).filter(deleted_at__isnull=True)
    
    if user_role == 'SUPER_ADMIN':
        # Super admin sees all active staff
        staff_users = base_queryset
        hotels = Hotel.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        # Hotel owners see only staff assigned to their hotels
        owned_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
        staff_users = base_queryset.filter(assigned_hotel__in=owned_hotels)
        hotels = owned_hotels
    else:
        # Staff see only other staff in their assigned hotel
        if request.user.assigned_hotel:
            staff_users = base_queryset.filter(assigned_hotel=request.user.assigned_hotel)
            hotels = Hotel.objects.filter(hotel_id=request.user.assigned_hotel.hotel_id)
        else:
            staff_users = User.objects.none()
            hotels = Hotel.objects.none()
    
    # Apply filters
    search = request.GET.get('search')
    role = request.GET.get('role')
    hotel = request.GET.get('hotel')
    is_active = request.GET.get('is_active')
    
    if search:
        staff_users = staff_users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )
    
    if role:
        staff_users = staff_users.filter(role=role)
    
    if hotel:
        staff_users = staff_users.filter(assigned_hotel__hotel_id=hotel)
    
    if is_active:
        staff_users = staff_users.filter(is_active=is_active.lower() == 'true')
    
    return render(request, 'staff/list.html', {
        'staff_list': staff_users,
        'hotels': hotels,
        'can_add_staff': check_user_permission(request.user, 'add_staff'),
        'can_view_staff': check_user_permission(request.user, 'view_staff'),
        'can_change_staff': check_user_permission(request.user, 'change_staff'),
        'can_delete_staff': check_user_permission(request.user, 'delete_staff'),
    })

@owner_or_permission_required('add_staff')
def staff_create(request):
    """Create new staff"""
    user_role = RoleManager.get_user_role(request.user)
    
    # Get available hotels for assignment
    if user_role == 'SUPER_ADMIN':
        available_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    else:
        available_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        hotel_id = request.POST.get('assigned_hotel')
        
        # Get assigned hotel
        assigned_hotel = None
        if hotel_id:
            assigned_hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
            # Verify user can assign to this hotel
            if user_role != 'SUPER_ADMIN' and assigned_hotel.owner != request.user:
                messages.error(request, 'You can only assign staff to your own hotels.')
                return render(request, 'staff/create.html', {'available_hotels': available_hotels})
        
        # Check if username already exists (including soft-deleted users)
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists. Please choose a different username.')
            return render(request, 'staff/create.html', {
                'available_hotels': available_hotels,
                'available_roles': ['Manager', 'Staff', 'Receptionist', 'Housekeeper', 'Maintenance', 'Kitchen', 'Accountant']
            })
        
        # Check if email already exists (including soft-deleted users)
        if User.objects.filter(email=email).exists():
            messages.error(request, f'Email "{email}" already exists. Please use a different email address.')
            return render(request, 'staff/create.html', {
                'available_hotels': available_hotels,
                'available_roles': ['Manager', 'Staff', 'Receptionist', 'Housekeeper', 'Maintenance', 'Kitchen', 'Accountant']
            })
        
        # Create user account
        password = request.POST.get('password', 'password123')
        role = request.POST.get('role', 'Staff')
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            assigned_hotel=assigned_hotel,
            # Hotel Management
            can_view_hotels=request.POST.get('can_view_hotels') == 'on',
            can_change_hotels=request.POST.get('can_change_hotels') == 'on',
            can_view_rooms=request.POST.get('can_view_rooms') == 'on',
            can_add_rooms=request.POST.get('can_add_rooms') == 'on',
            can_change_rooms=request.POST.get('can_change_rooms') == 'on',
            can_delete_rooms=request.POST.get('can_delete_rooms') == 'on',
            # Reservations
            can_view_reservations=request.POST.get('can_view_reservations') == 'on',
            can_add_reservations=request.POST.get('can_add_reservations') == 'on',
            can_change_reservations=request.POST.get('can_change_reservations') == 'on',
            can_delete_reservations=request.POST.get('can_delete_reservations') == 'on',
            can_view_checkins=request.POST.get('can_view_checkins') == 'on',
            can_add_checkins=request.POST.get('can_add_checkins') == 'on',
            # Guest Management
            can_view_guests=request.POST.get('can_view_guests') == 'on',
            can_add_guests=request.POST.get('can_add_guests') == 'on',
            can_change_guests=request.POST.get('can_change_guests') == 'on',
            can_delete_guests=request.POST.get('can_delete_guests') == 'on',
            # Staff Management
            can_view_staff=request.POST.get('can_view_staff') == 'on',
            can_add_staff=request.POST.get('can_add_staff') == 'on',
            can_change_staff=request.POST.get('can_change_staff') == 'on',
            can_delete_staff=request.POST.get('can_delete_staff') == 'on',
            # Operations
            can_view_housekeeping=request.POST.get('can_view_housekeeping') == 'on',
            can_add_housekeeping=request.POST.get('can_add_housekeeping') == 'on',
            can_view_maintenance=request.POST.get('can_view_maintenance') == 'on',
            can_add_maintenance=request.POST.get('can_add_maintenance') == 'on',
            can_view_pos=request.POST.get('can_view_pos') == 'on',
            can_add_pos=request.POST.get('can_add_pos') == 'on',
            # Financial
            can_view_billing=request.POST.get('can_view_billing') == 'on',
            can_add_billing=request.POST.get('can_add_billing') == 'on',
            can_view_payments=request.POST.get('can_view_payments') == 'on',
            can_add_payments=request.POST.get('can_add_payments') == 'on',
            can_view_reports=request.POST.get('can_view_reports') == 'on',
            can_view_inventory=request.POST.get('can_view_inventory') == 'on',
            # Configuration
            can_view_configurations=request.POST.get('can_view_configurations') == 'on',
            can_add_configurations=request.POST.get('can_add_configurations') == 'on',
            can_change_configurations=request.POST.get('can_change_configurations') == 'on',
            can_delete_configurations=request.POST.get('can_delete_configurations') == 'on'
        )
        
        # Assign default permissions based on role
        assign_default_permissions(user)
        
        # Send welcome email
        try:
            send_employee_welcome_email(user, password, request.user)
            messages.success(request, f'Staff member {user.full_name} created successfully! Welcome email sent.')
        except Exception as e:
            messages.success(request, f'Staff member {user.full_name} created successfully!')
            messages.warning(request, 'Welcome email could not be sent.')
        
        return redirect('staff:list')
    
    # Get available roles
    available_roles = ['Manager', 'Staff', 'Receptionist', 'Housekeeper', 'Maintenance', 'Kitchen', 'Accountant']
    
    return render(request, 'staff/create.html', {
        'available_hotels': available_hotels,
        'available_roles': available_roles
    })

@owner_or_permission_required('view_staff')
def staff_detail(request, staff_id):
    """Staff detail view"""
    user = get_object_or_404(User, user_id=staff_id)
    return render(request, 'staff/detail.html', {'staff': user})

@owner_or_permission_required('change_staff')
def staff_edit(request, staff_id):
    """Edit staff"""
    user = get_object_or_404(User, user_id=staff_id)
    user_role = RoleManager.get_user_role(request.user)
    
    # Get available hotels for assignment
    if user_role == 'SUPER_ADMIN':
        available_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    else:
        available_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone', '')
        
        # Allow owners and superusers to update everything
        if request.user.role == 'Owner' or request.user.is_superuser:
            user.username = request.POST.get('username')
            user.role = request.POST.get('role')
            user.is_active = request.POST.get('is_active') == 'true'
            
            # Update password if provided
            new_password = request.POST.get('new_password')
            if new_password and new_password.strip():
                user.set_password(new_password)
                messages.success(request, 'Password updated successfully!')
            
            # Update assigned hotel
            hotel_id = request.POST.get('assigned_hotel')
            if hotel_id:
                assigned_hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
                # Verify user can assign to this hotel
                if user_role != 'SUPER_ADMIN' and assigned_hotel.owner != request.user:
                    messages.error(request, 'You can only assign staff to your own hotels.')
                    return render(request, 'staff/edit.html', {'staff': user, 'available_hotels': available_hotels})
                user.assigned_hotel = assigned_hotel
            else:
                user.assigned_hotel = None
        
        user.save()
        
        messages.success(request, 'Staff member updated successfully!')
        return redirect('staff:detail', staff_id=user.user_id)
    
    return render(request, 'staff/edit.html', {
        'staff': user,
        'available_hotels': available_hotels
    })

@owner_or_permission_required('delete_staff')
def staff_delete(request, staff_id):
    """Soft delete staff member"""
    from django.utils import timezone
    user = get_object_or_404(User, user_id=staff_id, deleted_at__isnull=True)
    
    # Prevent deletion of owners and superusers
    if user.role == 'Owner' or user.is_superuser:
        messages.error(request, 'Cannot delete owners or administrators.')
        return redirect('staff:list')
    
    user_name = user.get_full_name() or user.username
    user.deleted_at = timezone.now()
    user.is_active = False
    user.save()
    messages.success(request, f'Staff member "{user_name}" deleted successfully!')
    return redirect('staff:list')

@login_required
def staff_permissions(request, staff_id):
    """Manage staff permissions"""
    staff_user = get_object_or_404(User, user_id=staff_id)
    
    # Only hotel owners can manage permissions for their staff
    if request.user.role != 'Owner' and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to manage staff permissions.')
        return redirect('staff:list')
    
    # Check if staff belongs to owner's hotel
    if request.user.role == 'Owner' and staff_user.assigned_hotel and staff_user.assigned_hotel.owner != request.user:
        messages.error(request, 'You can only manage permissions for your own staff.')
        return redirect('staff:list')
    
    if request.method == 'POST':
        # Clear existing permissions
        staff_user.user_permissions.clear()
        
        # Add selected permissions
        selected_permissions = request.POST.getlist('permissions')
        for perm_codename in selected_permissions:
            permission = Permission.objects.filter(codename=perm_codename).first()
            if permission:
                staff_user.user_permissions.add(permission)
        
        messages.success(request, f'Permissions updated for {staff_user.get_full_name()}')
        return redirect('staff:detail', staff_id=staff_id)
    
    # Get current permissions
    current_permissions = list(staff_user.user_permissions.values_list('codename', flat=True))
    
    context = {
        'staff': staff_user,
        'permission_categories': get_permission_categories(),
        'current_permissions': current_permissions
    }
    
    return render(request, 'staff/permissions.html', context)

@owner_or_permission_required('view_staff')
def staff_send_message(request, staff_id):
    """Send message to staff"""
    staff_user = get_object_or_404(User, user_id=staff_id)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        messages.success(request, f'Message sent to {staff_user.get_full_name()}')
        return redirect('staff:detail', staff_id=staff_id)
    
    return render(request, 'staff/send_message.html', {'staff': staff_user})

@owner_or_permission_required('view_staff')
def staff_schedule(request, staff_id):
    """View staff schedule"""
    staff_user = get_object_or_404(User, user_id=staff_id)
    return render(request, 'staff/schedule.html', {'staff': staff_user})

@owner_or_permission_required('view_staff')
def staff_performance(request, staff_id):
    """View staff performance"""
    staff_user = get_object_or_404(User, user_id=staff_id)
    return render(request, 'staff/performance.html', {'staff': staff_user})