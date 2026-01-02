from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages
from .models import MaintenanceIssue
from hotels.models import Hotel, Room
from accounts.roles import RoleManager

@login_required
def maintenance_dashboard(request):
    """Maintenance dashboard with real data"""
    user_role = RoleManager.get_user_role(request.user)
    
    # Get user's hotels based on role
    if user_role == 'SUPER_ADMIN':
        user_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        user_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    else:
        user_hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    # Get maintenance statistics
    issues = MaintenanceIssue.objects.filter(property__in=user_hotels, deleted_at__isnull=True)
    
    total_issues = issues.count()
    open_issues = issues.filter(status='open').count()
    in_progress_issues = issues.filter(status='in_progress').count()
    resolved_issues = issues.filter(status='resolved').count()
    urgent_issues = issues.filter(priority='urgent').count()
    
    # Recent issues
    recent_issues = issues.order_by('-reported_at')[:5]
    
    # Issues by category
    category_stats = issues.values('category').annotate(count=Count('id')).order_by('-count')
    
    # Issues by priority
    priority_stats = issues.values('priority').annotate(count=Count('id'))
    
    context = {
        'total_issues': total_issues,
        'open_issues': open_issues,
        'in_progress_issues': in_progress_issues,
        'resolved_issues': resolved_issues,
        'urgent_issues': urgent_issues,
        'recent_issues': recent_issues,
        'category_stats': category_stats,
        'priority_stats': priority_stats,
        'user_hotels': user_hotels,
    }
    
    return render(request, 'maintenance/dashboard.html', context)

@login_required
def issue_list(request):
    """List all maintenance issues"""
    user_role = RoleManager.get_user_role(request.user)
    
    # Get user's hotels based on role
    if user_role == 'SUPER_ADMIN':
        user_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        user_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    else:
        user_hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    issues = MaintenanceIssue.objects.filter(property__in=user_hotels, deleted_at__isnull=True)
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        issues = issues.filter(status=status_filter)
    
    priority_filter = request.GET.get('priority')
    if priority_filter:
        issues = issues.filter(priority=priority_filter)
    
    category_filter = request.GET.get('category')
    if category_filter:
        issues = issues.filter(category=category_filter)
    
    search = request.GET.get('search')
    if search:
        issues = issues.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    context = {
        'issues': issues.order_by('-reported_at'),
        'status_choices': MaintenanceIssue.STATUS_CHOICES,
        'priority_choices': MaintenanceIssue.PRIORITY_CHOICES,
        'category_choices': MaintenanceIssue.CATEGORY_CHOICES,
    }
    
    return render(request, 'maintenance/issue_list.html', context)

@login_required
def issue_create(request):
    """Create new maintenance issue"""
    user_role = RoleManager.get_user_role(request.user)
    
    # Get user's hotels based on role
    if user_role == 'SUPER_ADMIN':
        user_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        user_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    else:
        user_hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    if request.method == 'POST':
        try:
            # Get form data
            property_id = request.POST.get('property')
            room_id = request.POST.get('room') if request.POST.get('room') else None
            title = request.POST.get('title')
            description = request.POST.get('description')
            category = request.POST.get('category')
            priority = request.POST.get('priority')
            
            # Create the issue
            issue = MaintenanceIssue.objects.create(
                property_id=property_id,
                room_id=room_id,
                title=title,
                description=description,
                category=category,
                priority=priority,
                reported_by=request.user,
                status='open'
            )
            
            messages.success(request, f'Maintenance issue "{title}" has been created successfully.')
            return redirect('maintenance:issue_list')
            
        except Exception as e:
            messages.error(request, f'Error creating issue: {str(e)}')
    
    # Get rooms for each hotel
    hotel_rooms = {}
    for hotel in user_hotels:
        rooms = Room.objects.filter(hotel=hotel)
        hotel_rooms[str(hotel.hotel_id)] = [
            {
                'room_id': str(room.room_id),
                'room_number': room.room_number,
                'status': room.status
            } for room in rooms
        ]
    
    context = {
        'user_hotels': user_hotels,
        'hotel_rooms': hotel_rooms,
        'status_choices': MaintenanceIssue.STATUS_CHOICES,
        'priority_choices': MaintenanceIssue.PRIORITY_CHOICES,
        'category_choices': MaintenanceIssue.CATEGORY_CHOICES,
    }
    
    return render(request, 'maintenance/issue_form.html', context)

@login_required
def issue_update(request, issue_id):
    """Update maintenance issue status"""
    user_role = RoleManager.get_user_role(request.user)
    
    # Get user's hotels based on role
    if user_role == 'SUPER_ADMIN':
        user_hotels = Hotel.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        user_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
    else:
        user_hotels = [request.user.assigned_hotel] if request.user.assigned_hotel else []
    
    # Get the issue
    try:
        issue = MaintenanceIssue.objects.get(id=issue_id, property__in=user_hotels)
    except MaintenanceIssue.DoesNotExist:
        messages.error(request, 'Issue not found or access denied.')
        return redirect('maintenance:issue_list')
    
    if request.method == 'POST':
        try:
            # Update allowed fields for maintenance staff
            if request.user.role == 'Maintenance':
                # Maintenance staff can update status, resolution notes, and assign themselves
                if 'status' in request.POST:
                    issue.status = request.POST.get('status')
                if 'resolution_notes' in request.POST:
                    issue.resolution_notes = request.POST.get('resolution_notes')
                if 'assigned_to' in request.POST and not issue.assigned_to:
                    issue.assigned_to = request.user
                if issue.status == 'resolved' and not issue.resolved_at:
                    from django.utils import timezone
                    issue.resolved_at = timezone.now()
            else:
                # Other roles can update all fields
                issue.status = request.POST.get('status', issue.status)
                issue.priority = request.POST.get('priority', issue.priority)
                issue.resolution_notes = request.POST.get('resolution_notes', issue.resolution_notes)
                assigned_to_id = request.POST.get('assigned_to')
                if assigned_to_id:
                    from accounts.models import User
                    issue.assigned_to = User.objects.get(id=assigned_to_id)
            
            issue.save()
            messages.success(request, f'Issue "{issue.title}" has been updated successfully.')
            return redirect('maintenance:issue_list')
            
        except Exception as e:
            messages.error(request, f'Error updating issue: {str(e)}')
    
    context = {
        'issue': issue,
        'status_choices': MaintenanceIssue.STATUS_CHOICES,
        'priority_choices': MaintenanceIssue.PRIORITY_CHOICES,
        'category_choices': MaintenanceIssue.CATEGORY_CHOICES,
        'is_maintenance_staff': request.user.role == 'Maintenance',
    }
    
    return render(request, 'maintenance/issue_update.html', context)