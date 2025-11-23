from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User
from accounts.roles import RoleManager
from accounts.email_utils import send_employee_welcome_email
from accounts.permissions import assign_default_permissions, get_permission_categories, check_user_permission
from hotels.models import Hotel
from django.contrib.auth.models import Permission

@login_required
def staff_list(request):
    """List staff based on user role (excluding soft-deleted)"""
    user_role = RoleManager.get_user_role(request.user)
    
    if user_role == 'SUPER_ADMIN':
        # Super admin sees all staff (excluding owners and superusers)
        staff_users = User.objects.exclude(role='Owner').exclude(is_superuser=True).filter(deleted_at__isnull=True)
    else:
        # Hotel owners see only staff assigned to their hotels (excluding owners)
        owned_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
        staff_users = User.objects.exclude(role='Owner').exclude(is_superuser=True).filter(assigned_hotel__in=owned_hotels, deleted_at__isnull=True)
    
    return render(request, 'staff/list.html', {'staff_list': staff_users})

@login_required
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
        
        # Create user account
        password = 'password123'  # Default password
        role = request.POST.get('role', 'Staff')
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            assigned_hotel=assigned_hotel
        )
        user.set_password(password)
        user.save()
        
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

@login_required
def staff_detail(request, staff_id):
    """Staff detail view"""
    user = get_object_or_404(User, user_id=staff_id)
    return render(request, 'staff/detail.html', {'staff': user})

@login_required
def staff_edit(request, staff_id):
    """Edit staff"""
    user = get_object_or_404(User, user_id=staff_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone', '')
        user.save()
        
        messages.success(request, 'Staff member updated successfully!')
        return redirect('staff:detail', staff_id=user.user_id)
    
    return render(request, 'staff/edit.html', {'staff': user})

@login_required
def staff_delete(request, staff_id):
    """Soft delete staff member"""
    from django.utils import timezone
    user = get_object_or_404(User, user_id=staff_id, role='Staff')
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
            try:
                permission = Permission.objects.get(codename=perm_codename)
                staff_user.user_permissions.add(permission)
            except Permission.DoesNotExist:
                pass
        
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

@login_required
def staff_send_message(request, staff_id):
    """Send message to staff"""
    staff_user = get_object_or_404(User, user_id=staff_id)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        messages.success(request, f'Message sent to {staff_user.get_full_name()}')
        return redirect('staff:detail', staff_id=staff_id)
    
    return render(request, 'staff/send_message.html', {'staff': staff_user})

@login_required
def staff_schedule(request, staff_id):
    """View staff schedule"""
    staff_user = get_object_or_404(User, user_id=staff_id)
    return render(request, 'staff/schedule.html', {'staff': staff_user})

@login_required
def staff_performance(request, staff_id):
    """View staff performance"""
    staff_user = get_object_or_404(User, user_id=staff_id)
    return render(request, 'staff/performance.html', {'staff': staff_user})