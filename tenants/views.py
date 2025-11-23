from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Client, Domain, SubscriptionPlan, TenantSettings, TenantUser, AuditLog
from .forms import TenantForm, TenantSettingsForm
from hotels.models import Hotel
from reservations.models import Reservation

def is_superuser(user):
    return user.is_superuser

def landing_page(request):
    """Public landing page"""
    return render(request, 'public/index.html')

@login_required
@user_passes_test(is_superuser)
def super_admin_dashboard(request):
    """Super admin dashboard with platform overview"""
    # Get key metrics
    total_tenants = Client.objects.count()
    active_tenants = Client.objects.filter(is_active=True).count()
    total_properties = Hotel.objects.count()
    
    # Recent activity
    recent_tenants = Client.objects.order_by('-created_on')[:5]
    recent_logs = AuditLog.objects.order_by('-timestamp')[:10]
    
    # Revenue metrics (simplified)
    subscription_plans = SubscriptionPlan.objects.filter(is_active=True)
    
    context = {
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'total_properties': total_properties,
        'recent_tenants': recent_tenants,
        'recent_logs': recent_logs,
        'subscription_plans': subscription_plans,
    }
    
    return render(request, 'dashboards/super_admin_dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def tenant_list(request):
    """List all tenants for super admin"""
    tenants = Client.objects.all().order_by('-created_on')
    
    context = {
        'tenants': tenants,
    }
    
    return render(request, 'tenants/tenant_list.html', context)

@login_required
@user_passes_test(is_superuser)
def tenant_create(request):
    """Create new tenant"""
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            
            # Create domain
            domain_name = form.cleaned_data.get('domain_name')
            if domain_name:
                Domain.objects.create(
                    domain=f"{domain_name}.yourdomain.com",
                    tenant=tenant,
                    is_primary=True
                )
            
            # Create audit log
            AuditLog.objects.create(
                tenant=tenant,
                user=request.user,
                action='tenant_created',
                description=f'Tenant {tenant.name} created by {request.user.username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Tenant {tenant.name} created successfully!')
            return redirect('tenant_list')
    else:
        form = TenantForm()
    
    return render(request, 'tenants/tenant_form.html', {'form': form})

@login_required
@user_passes_test(is_superuser)
def tenant_detail(request, tenant_id):
    """Tenant detail view for super admin"""
    tenant = get_object_or_404(Client, id=tenant_id)
    
    # Get tenant statistics
    properties = Hotel.objects.filter(tenant=tenant)
    total_reservations = Reservation.objects.filter(hotel_property__in=properties).count()
    
    context = {
        'tenant': tenant,
        'properties': properties,
        'total_reservations': total_reservations,
    }
    
    return render(request, 'tenants/tenant_detail.html', context)

@login_required
def hotel_owner_dashboard(request):
    """Hotel owner/manager dashboard"""
    # Get user's properties
    try:
        tenant_user = TenantUser.objects.get(user=request.user)
        properties = Hotel.objects.all()  # All properties in tenant schema
    except TenantUser.DoesNotExist:
        properties = Hotel.objects.none()
    
    # Dashboard metrics
    total_properties = properties.count()
    total_rooms = sum(prop.room_types.aggregate(
        total=Sum('rooms__id')
    )['total'] or 0 for prop in properties)
    
    # Recent reservations
    recent_reservations = Reservation.objects.filter(
        hotel_property__in=properties
    ).order_by('-created_at')[:10]
    
    # Occupancy data (simplified)
    today = timezone.now().date()
    occupied_rooms = Reservation.objects.filter(
        hotel_property__in=properties,
        check_in__lte=today,
        check_out__gt=today,
        status='checked_in'
    ).count()
    
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    context = {
        'properties': properties,
        'total_properties': total_properties,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_rate': occupancy_rate,
        'recent_reservations': recent_reservations,
    }
    
    return render(request, 'dashboards/hotel_owner_dashboard.html', context)

@login_required
def employee_dashboard(request):
    """Employee dashboard based on role"""
    try:
        staff = request.user.staff_profile
        role = staff.role
    except:
        role = 'guest'  # Default for non-staff users
    
    context = {
        'role': role,
        'staff': getattr(request.user, 'staff_profile', None),
    }
    
    if role == 'receptionist':
        return receptionist_dashboard(request, context)
    elif role == 'housekeeper':
        return housekeeper_dashboard(request, context)
    elif role == 'maintenance':
        return maintenance_dashboard(request, context)
    elif role == 'chef':
        return chef_dashboard(request, context)
    else:
        return render(request, 'dashboards/employee_dashboard.html', context)

def receptionist_dashboard(request, context):
    """Receptionist-specific dashboard"""
    today = timezone.now().date()
    
    # Today's arrivals and departures
    arrivals = Reservation.objects.filter(
        check_in=today,
        status__in=['confirmed', 'checked_in']
    ).order_by('check_in')
    
    departures = Reservation.objects.filter(
        check_out=today,
        status='checked_in'
    ).order_by('check_out')
    
    # Walk-ins and pending reservations
    pending_reservations = Reservation.objects.filter(
        status='pending'
    ).order_by('created_at')
    
    context.update({
        'arrivals': arrivals,
        'departures': departures,
        'pending_reservations': pending_reservations,
    })
    
    return render(request, 'dashboards/receptionist_dashboard.html', context)

def housekeeper_dashboard(request, context):
    """Housekeeper-specific dashboard"""
    from housekeeping.models import HousekeepingTask
    
    staff = context['staff']
    
    # Today's tasks
    today_tasks = HousekeepingTask.objects.filter(
        assigned_staff=staff,
        created_at__date=timezone.now().date()
    ).order_by('priority', 'created_at')
    
    # Pending tasks
    pending_tasks = HousekeepingTask.objects.filter(
        assigned_staff=staff,
        status='pending'
    ).order_by('priority', 'created_at')
    
    context.update({
        'today_tasks': today_tasks,
        'pending_tasks': pending_tasks,
    })
    
    return render(request, 'dashboards/housekeeper_dashboard.html', context)

def maintenance_dashboard(request, context):
    """Maintenance staff dashboard"""
    from maintenance.models import MaintenanceIssue
    
    staff = context['staff']
    
    # Assigned issues
    assigned_issues = MaintenanceIssue.objects.filter(
        assigned_to=staff,
        status__in=['open', 'in_progress']
    ).order_by('priority', 'reported_at')
    
    # Recent issues
    recent_issues = MaintenanceIssue.objects.filter(
        property=staff.property
    ).order_by('-reported_at')[:10]
    
    context.update({
        'assigned_issues': assigned_issues,
        'recent_issues': recent_issues,
    })
    
    return render(request, 'dashboards/maintenance_dashboard.html', context)

def chef_dashboard(request, context):
    """Chef/kitchen staff dashboard"""
    # This would integrate with POS system for food orders
    # Simplified for now
    
    context.update({
        'orders': [],  # Would come from POS integration
    })
    
    return render(request, 'dashboards/chef_dashboard.html', context)