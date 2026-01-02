from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from .models import HousekeepingTask, HousekeepingSchedule
from hotels.models import Room, Hotel
from accounts.models import User
from datetime import date, timedelta

@login_required
def housekeeping_dashboard(request):
    """Housekeeping dashboard with real data"""
    # Get user's assigned hotel
    user_hotel = request.user.assigned_hotel
    
    # Get room statistics
    if user_hotel:
        total_rooms = Room.objects.filter(hotel=user_hotel).count()
        available_rooms = Room.objects.filter(hotel=user_hotel, status='Available').count()
        dirty_rooms = Room.objects.filter(hotel=user_hotel, status='Dirty').count()
        cleaning_rooms = Room.objects.filter(hotel=user_hotel, status='Cleaning').count()
        occupied_rooms = Room.objects.filter(hotel=user_hotel, status='Occupied').count()
        maintenance_rooms = Room.objects.filter(hotel=user_hotel, status='Maintenance').count()
        
        # Get today's tasks
        today_tasks = HousekeepingTask.objects.filter(
            room__hotel=user_hotel,
            created_at__date=date.today(),
            deleted_at__isnull=True
        ).count()
        
        pending_tasks = HousekeepingTask.objects.filter(
            room__hotel=user_hotel,
            status='pending',
            deleted_at__isnull=True
        ).count()
        
        completed_tasks = HousekeepingTask.objects.filter(
            room__hotel=user_hotel,
            status='completed',
            created_at__date=date.today(),
            deleted_at__isnull=True
        ).count()
        
        # Get rooms by floor
        floors_data = []
        floors = Room.objects.filter(hotel=user_hotel).values_list('floor__number', flat=True).distinct().order_by('floor__number')
        
        for floor_num in floors:
            if floor_num:
                floor_rooms = Room.objects.filter(hotel=user_hotel, floor__number=floor_num)
                floors_data.append({
                    'floor': floor_num,
                    'clean': floor_rooms.filter(status='Available').count(),
                    'dirty': floor_rooms.filter(status='Dirty').count(),
                    'cleaning': floor_rooms.filter(status='Cleaning').count(),
                    'occupied': floor_rooms.filter(status='Occupied').count(),
                })
    else:
        total_rooms = available_rooms = dirty_rooms = cleaning_rooms = 0
        occupied_rooms = maintenance_rooms = today_tasks = pending_tasks = completed_tasks = 0
        floors_data = []
    
    context = {
        'user_hotel': user_hotel,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'dirty_rooms': dirty_rooms,
        'cleaning_rooms': cleaning_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'today_tasks': today_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'floors_data': floors_data,
    }
    
    return render(request, 'housekeeping/dashboard.html', context)

@login_required
def task_list(request):
    """Housekeeping task list with filtering and real data"""
    # Get user's assigned hotel
    user_hotel = request.user.assigned_hotel
    
    # Base queryset - tasks for user's hotel
    if user_hotel:
        tasks = HousekeepingTask.objects.filter(
            room__hotel=user_hotel,
            deleted_at__isnull=True
        ).select_related('room', 'assigned_staff')
    else:
        tasks = HousekeepingTask.objects.filter(
            deleted_at__isnull=True
        ).select_related('room', 'assigned_staff')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    task_type_filter = request.GET.get('task_type', '')
    priority_filter = request.GET.get('priority', '')
    date_filter = request.GET.get('date', '')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if task_type_filter:
        tasks = tasks.filter(task_type=task_type_filter)
    
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    if date_filter == 'today':
        tasks = tasks.filter(created_at__date=date.today())
    elif date_filter == 'week':
        week_ago = date.today() - timedelta(days=7)
        tasks = tasks.filter(created_at__date__gte=week_ago)
    
    # Order tasks by priority and creation date
    tasks = tasks.order_by('-priority', 'created_at')
    
    # Get statistics
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='completed').count()
    
    # Get rooms that need cleaning (Available but dirty)
    if user_hotel:
        dirty_rooms = Room.objects.filter(
            hotel=user_hotel,
            status__in=['Dirty', 'Cleaning']
        ).count()
        total_rooms = Room.objects.filter(hotel=user_hotel).count()
    else:
        dirty_rooms = Room.objects.filter(status__in=['Dirty', 'Cleaning']).count()
        total_rooms = Room.objects.count()
    
    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'dirty_rooms': dirty_rooms,
        'total_rooms': total_rooms,
        'user_hotel': user_hotel,
        'status_filter': status_filter,
        'task_type_filter': task_type_filter,
        'priority_filter': priority_filter,
        'date_filter': date_filter,
        'status_choices': HousekeepingTask.STATUS_CHOICES,
        'task_type_choices': HousekeepingTask.TASK_TYPE_CHOICES,
    }
    
    return render(request, 'housekeeping/task_list.html', context)

@login_required
def update_task_status(request, task_id):
    """Update task status"""
    task = get_object_or_404(HousekeepingTask, id=task_id)
    
    # Check if user can update this task
    if request.user.assigned_hotel and task.room.hotel != request.user.assigned_hotel:
        messages.error(request, 'You can only update tasks for your assigned hotel.')
        return redirect('housekeeping:task_list')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(HousekeepingTask.STATUS_CHOICES):
            old_status = task.status
            task.status = new_status
            
            # Update timestamps
            if new_status == 'in_progress' and old_status == 'pending':
                task.started_at = timezone.now()
            elif new_status == 'completed':
                task.completed_at = timezone.now()
                # Update room status to clean if task is completed
                if task.task_type in ['checkout_cleaning', 'deep_cleaning']:
                    task.room.status = 'Available'
                    task.room.save()
            
            if notes:
                task.notes = notes
            
            task.save()
            messages.success(request, f'Task status updated to {task.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('housekeeping:task_list')

@login_required
def create_maintenance_request(request, room_id):
    """Create maintenance request for a room"""
    room = get_object_or_404(Room, room_id=room_id)
    
    # Check if user can create maintenance for this room
    if request.user.assigned_hotel and room.hotel != request.user.assigned_hotel:
        messages.error(request, 'You can only create maintenance requests for your assigned hotel.')
        return redirect('housekeeping:task_list')
    
    if request.method == 'POST':
        description = request.POST.get('description')
        priority = request.POST.get('priority', 3)
        
        # Create maintenance issue
        try:
            from maintenance.models import MaintenanceIssue
            from .utils import create_maintenance_request_notification
            
            maintenance_request = MaintenanceIssue.objects.create(
                room=room,
                property=room.hotel,
                title=f'Maintenance Required - Room {room.room_number}',
                description=description,
                reported_by=request.user,
                priority=int(priority),
                status='open'
            )
            
            # Create notifications for managers and admins
            create_maintenance_request_notification(maintenance_request)
            
            messages.success(request, f'Maintenance request created for Room {room.room_number}. Managers have been notified.')
        except ImportError:
            messages.error(request, 'Maintenance system not available')
    
    return redirect('housekeeping:task_list')

@login_required
def room_status_list(request):
    """View and update room cleaning status"""
    # Get user's assigned hotel
    user_hotel = request.user.assigned_hotel
    view_type = request.GET.get('view', 'list')  # 'list' or 'kanban'
    
    # Base queryset - rooms for user's hotel
    if user_hotel:
        rooms = Room.objects.filter(hotel=user_hotel)
    else:
        rooms = Room.objects.all()
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    floor_filter = request.GET.get('floor', '')
    
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    
    if floor_filter and floor_filter != 'None':
        try:
            floor_number = int(floor_filter)
            rooms = rooms.filter(floor__number=floor_number)
        except (ValueError, TypeError):
            pass
    
    # Order rooms by floor and room number
    rooms = rooms.select_related('floor', 'room_type').order_by('floor__number', 'room_number')
    
    # Get statistics
    total_rooms = rooms.count()
    available_rooms = rooms.filter(status='Available').count()
    occupied_rooms = rooms.filter(status='Occupied').count()
    dirty_rooms = rooms.filter(status='Dirty').count()
    cleaning_rooms = rooms.filter(status='Cleaning').count()
    maintenance_rooms = rooms.filter(status='Maintenance').count()
    
    # Get unique floors for filter
    floors = rooms.values_list('floor__number', flat=True).distinct().order_by('floor__number')
    
    context = {
        'rooms': rooms,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'dirty_rooms': dirty_rooms,
        'cleaning_rooms': cleaning_rooms,
        'maintenance_rooms': maintenance_rooms,
        'user_hotel': user_hotel,
        'status_filter': status_filter,
        'floor_filter': floor_filter,
        'floors': floors,
        'room_status_choices': Room.ROOM_STATUS_CHOICES,
        'view_type': view_type,
    }
    
    if view_type == 'kanban':
        context.update({
            'available_rooms_list': rooms.filter(status='Available'),
            'dirty_rooms_list': rooms.filter(status='Dirty'),
            'cleaning_rooms_list': rooms.filter(status='Cleaning'),
            'occupied_rooms_list': rooms.filter(status='Occupied'),
            'maintenance_rooms_list': rooms.filter(status='Maintenance'),
        })
    
    return render(request, 'housekeeping/room_status.html', context)

@login_required
def update_room_status(request, room_id):
    """Update room cleaning status"""
    room = get_object_or_404(Room, room_id=room_id)
    
    # Check if user can update this room
    if request.user.assigned_hotel and room.hotel != request.user.assigned_hotel:
        messages.error(request, 'You can only update rooms for your assigned hotel.')
        return redirect('housekeeping:room_status_list')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        # Validate status - housekeeping can only update cleaning-related statuses
        allowed_statuses = ['Available', 'Dirty', 'Cleaning']
        if new_status in allowed_statuses:
            old_status = room.status
            room.status = new_status
            room.save()
            
            # Create a housekeeping task if room is marked as dirty
            if new_status == 'Dirty' and old_status != 'Dirty':
                # Auto-assign to available housekeeper
                available_housekeeper = User.objects.filter(
                    role='Housekeeping',
                    assigned_hotel=room.hotel,
                    is_active=True
                ).first()
                
                HousekeepingTask.objects.create(
                    room=room,
                    assigned_staff=available_housekeeper,
                    task_type='checkout_cleaning',
                    status='pending',
                    priority=3,
                    description=f'Room {room.room_number} needs cleaning after checkout'
                )
            
            messages.success(request, f'Room {room.room_number} status updated to {new_status}')
        else:
            messages.error(request, 'You can only update cleaning-related statuses (Available, Dirty, Cleaning)')
    
    return redirect('housekeeping:room_status_list')

@login_required
def room_assignments(request):
    """View room assignments for housekeeping staff"""
    # Get user's assigned hotel
    user_hotel = request.user.assigned_hotel
    
    # Get tasks assigned to current user or all tasks if manager/admin
    if request.user.role == 'Housekeeping':
        tasks = HousekeepingTask.objects.filter(
            room__hotel=user_hotel,
            assigned_staff=request.user,
            deleted_at__isnull=True
        ).select_related('room', 'assigned_staff')
    else:
        # Managers and admins can see all assignments
        if user_hotel:
            tasks = HousekeepingTask.objects.filter(
                room__hotel=user_hotel,
                deleted_at__isnull=True
            ).select_related('room', 'assigned_staff')
        else:
            tasks = HousekeepingTask.objects.filter(
                deleted_at__isnull=True
            ).select_related('room', 'assigned_staff')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if date_filter == 'today':
        tasks = tasks.filter(created_at__date=date.today())
    elif date_filter == 'week':
        week_ago = date.today() - timedelta(days=7)
        tasks = tasks.filter(created_at__date__gte=week_ago)
    
    # Order by priority and creation date
    tasks = tasks.order_by('-priority', 'created_at')
    
    # Get statistics
    total_assignments = tasks.count()
    pending_assignments = tasks.filter(status='pending').count()
    in_progress_assignments = tasks.filter(status='in_progress').count()
    completed_assignments = tasks.filter(status='completed').count()
    
    context = {
        'tasks': tasks,
        'total_assignments': total_assignments,
        'pending_assignments': pending_assignments,
        'in_progress_assignments': in_progress_assignments,
        'completed_assignments': completed_assignments,
        'user_hotel': user_hotel,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': HousekeepingTask.STATUS_CHOICES,
    }
    
    return render(request, 'housekeeping/room_assignments.html', context)