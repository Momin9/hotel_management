from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HousekeepingSchedule
from hotels.models import Room
from accounts.models import User
from datetime import date, timedelta

@login_required
def schedule_list(request):
    """View housekeeping schedules"""
    user_hotel = request.user.assigned_hotel
    
    if request.user.role == 'Housekeeping':
        schedules = HousekeepingSchedule.objects.filter(staff=request.user)
    else:
        if user_hotel:
            schedules = HousekeepingSchedule.objects.filter(staff__assigned_hotel=user_hotel)
        else:
            schedules = HousekeepingSchedule.objects.all()
    
    date_filter = request.GET.get('date', '')
    if date_filter == 'today':
        schedules = schedules.filter(date=date.today())
    
    context = {
        'schedules': schedules.order_by('date', 'shift'),
        'user_hotel': user_hotel,
    }
    
    return render(request, 'housekeeping/schedule_list.html', context)

@login_required
def create_schedule(request):
    """Create housekeeping schedule (Admin/Manager only)"""
    if request.user.role not in ['Manager', 'Owner'] and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to create schedules.')
        return redirect('housekeeping:schedule_list')
    
    user_hotel = request.user.assigned_hotel
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff')
        schedule_date = request.POST.get('date')
        shift = request.POST.get('shift')
        room_ids = request.POST.getlist('rooms')
        notes = request.POST.get('notes', '')
        
        try:
            staff = User.objects.get(user_id=staff_id, role='Housekeeping')
            
            schedule = HousekeepingSchedule.objects.create(
                staff=staff,
                date=schedule_date,
                shift=shift,
                notes=notes,
                created_by=request.user
            )
            
            if room_ids:
                rooms = Room.objects.filter(room_id__in=room_ids)
                schedule.rooms.set(rooms)
            
            messages.success(request, f'Schedule created for {staff.get_full_name()}')
            return redirect('housekeeping:schedule_list')
        except Exception as e:
            messages.error(request, f'Error creating schedule: {str(e)}')
    
    # Get housekeeping staff
    if user_hotel:
        staff_list = User.objects.filter(
            role='Housekeeping',
            assigned_hotel=user_hotel,
            is_active=True
        )
        rooms = Room.objects.filter(hotel=user_hotel)
    else:
        staff_list = User.objects.filter(role='Housekeeping', is_active=True)
        rooms = Room.objects.all()
    
    context = {
        'staff_list': staff_list,
        'rooms': rooms,
        'shift_choices': HousekeepingSchedule.SHIFT_CHOICES,
    }
    
    return render(request, 'housekeeping/create_schedule.html', context)