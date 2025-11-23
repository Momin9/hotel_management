from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, date
from .models import Reservation, Stay
from hotels.models import Hotel, Room
from crm.models import GuestProfile

@login_required
def reservation_list(request):
    """List reservations based on user role"""
    if request.user.is_superuser:
        reservations = Reservation.objects.all().order_by('-created_at')
    else:
        # Hotel owners see only reservations for their hotels
        owned_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
        reservations = Reservation.objects.filter(hotel__in=owned_hotels).order_by('-created_at')
    
    return render(request, 'reservations/list.html', {'reservations': reservations})

@login_required
def reservation_create(request):
    """Create new reservation"""
    if request.method == 'POST':
        # Handle new guest creation if needed
        guest_id = request.POST.get('guest')
        if guest_id == 'new' or not guest_id:
            # Create new guest
            guest = GuestProfile.objects.create(
                first_name=request.POST.get('guest_first_name'),
                last_name=request.POST.get('guest_last_name'),
                email=request.POST.get('guest_email'),
                phone=request.POST.get('guest_phone', '')
            )
        else:
            guest = get_object_or_404(GuestProfile, id=guest_id)
        
        hotel_id = request.POST.get('hotel')
        room_id = request.POST.get('room')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        adults = request.POST.get('adults', 1)
        children = request.POST.get('children', 0)
        reservation_type = request.POST.get('reservation_type', 'reservation')
        special_requests = request.POST.get('special_requests', '')
        
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        room = get_object_or_404(Room, room_id=room_id)
        
        # Determine status based on reservation type
        status = 'checked_in' if reservation_type == 'booking' else 'confirmed'
        
        reservation = Reservation.objects.create(
            guest=guest,
            hotel=hotel,
            room=room,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            children=children,
            rate=room.price,
            status=status,
            booking_source='direct',
            special_requests=special_requests
        )
        
        # Update room status
        if reservation_type == 'booking':
            room.status = 'Occupied'
        else:
            room.status = 'Reserved'
        room.save()
        
        messages.success(request, f'Reservation created successfully for {guest.full_name}!')
        return redirect('reservations:detail', reservation_id=reservation.id)
    
    guests = GuestProfile.objects.filter(deleted_at__isnull=True)
    
    # Filter hotels based on user role
    if request.user.is_superuser:
        hotels = Hotel.objects.filter(deleted_at__isnull=True, is_active=True)
    else:
        # Hotel owners see only their hotels
        hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True, is_active=True)
    
    return render(request, 'reservations/create_new.html', {
        'guests': guests,
        'hotels': hotels
    })

@login_required
def check_room_availability(request):
    """Check room availability for dates"""
    hotel_id = request.GET.get('hotel_id')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if not all([hotel_id, check_in, check_out]):
        return JsonResponse({'rooms': []})
    
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        all_rooms = hotel.rooms.all()
        
        booked_rooms = Reservation.objects.filter(
            hotel=hotel,
            check_in__lt=check_out_date,
            check_out__gt=check_in_date,
            status__in=['confirmed', 'checked_in']
        ).values_list('room_id', flat=True)
        
        available_rooms = all_rooms.exclude(room_id__in=booked_rooms).filter(
            status__in=['Available', 'Cleaning']
        )
        
        rooms_data = [{
            'id': room.room_id,
            'number': room.room_number,
            'type': room.type,
            'category': room.category,
            'price': str(room.price),
            'bed': room.bed
        } for room in available_rooms]
        
        return JsonResponse({'rooms': rooms_data})
        
    except Exception as e:
        return JsonResponse({'rooms': [], 'error': str(e)})

@login_required
def booking_create(request):
    """Create new booking (different from reservation)"""
    if request.method == 'POST':
        messages.success(request, 'Booking created successfully!')
        return redirect('reservations:list')
    
    guests = GuestProfile.objects.filter(deleted_at__isnull=True)
    
    # Filter hotels based on user role
    if request.user.is_superuser:
        hotels = Hotel.objects.filter(deleted_at__isnull=True, is_active=True)
    else:
        # Hotel owners see only their hotels
        hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True, is_active=True)
    
    return render(request, 'reservations/booking_create.html', {
        'guests': guests,
        'hotels': hotels
    })

@login_required
def reservation_detail(request, reservation_id):
    """Reservation detail view"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check if user has access to this reservation
    if not request.user.is_superuser and reservation.hotel.owner != request.user:
        messages.error(request, 'You do not have access to this reservation.')
        return redirect('reservations:list')
    
    return render(request, 'reservations/detail.html', {'reservation': reservation})

@login_required
def reservation_edit(request, reservation_id):
    """Edit reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check if user has access to this reservation
    if not request.user.is_superuser and reservation.hotel.owner != request.user:
        messages.error(request, 'You do not have access to this reservation.')
        return redirect('reservations:list')
    
    if request.method == 'POST':
        messages.success(request, 'Reservation updated successfully!')
        return redirect('reservations:detail', reservation_id=reservation.id)
    
    return render(request, 'reservations/edit.html', {'reservation': reservation})

@login_required
def reservation_cancel(request, reservation_id):
    """Cancel reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Reservation cancelled successfully!')
        return redirect('reservations:list')
    
    return render(request, 'reservations/cancel.html', {'reservation': reservation})

@login_required
def booking_list(request):
    """List all bookings (different from reservations)"""
    bookings = Reservation.objects.filter(booking_source='direct').order_by('-created_at')
    return render(request, 'reservations/booking_list.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    """Booking detail view"""
    booking = get_object_or_404(Reservation, id=booking_id)
    return render(request, 'reservations/booking_detail.html', {'booking': booking})