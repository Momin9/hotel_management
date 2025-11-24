from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, date, timedelta
from decimal import Decimal
from .models import Reservation, Stay
from hotels.models import Hotel, Room
from crm.models import GuestProfile
from billing.models import Invoice, ChargeItem, Payment
from django.utils import timezone
from accounts.decorators import owner_or_permission_required

@owner_or_permission_required('view_reservation')
def reservation_list(request):
    """List reservations based on user role"""
    if request.user.is_superuser:
        reservations = Reservation.objects.all().order_by('-created_at')
    elif request.user.role == 'Owner':
        # Hotel owners see only reservations for their hotels
        owned_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
        reservations = Reservation.objects.filter(hotel__in=owned_hotels).order_by('-created_at')
    else:
        # Staff see only reservations for their assigned hotel
        if request.user.assigned_hotel:
            reservations = Reservation.objects.filter(hotel=request.user.assigned_hotel).order_by('-created_at')
        else:
            reservations = Reservation.objects.none()
    
    return render(request, 'reservations/list.html', {'reservations': reservations})

@owner_or_permission_required('add_reservation')
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

@owner_or_permission_required('view_reservation')
def reservation_detail(request, reservation_id):
    """Reservation detail view"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check if user has access to this reservation
    if not request.user.is_superuser and reservation.hotel.owner != request.user:
        messages.error(request, 'You do not have access to this reservation.')
        return redirect('reservations:list')
    
    return render(request, 'reservations/detail.html', {'reservation': reservation})

@owner_or_permission_required('change_reservation')
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

@owner_or_permission_required('delete_reservation')
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

@owner_or_permission_required('add_checkin')
def quick_check_in(request, reservation_id):
    """Quick check-in from list view"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if reservation.status == 'confirmed':
        # Create stay record
        stay = Stay.objects.create(
            reservation=reservation,
            room=reservation.room,
            actual_check_in=timezone.now()
        )
        
        # Update statuses
        reservation.status = 'checked_in'
        reservation.save()
        
        reservation.room.status = 'Occupied'
        reservation.room.save()
        
        return JsonResponse({'success': True, 'message': 'Guest checked in successfully!'})
    
    return JsonResponse({'success': False, 'message': 'Cannot check in this reservation.'})

@owner_or_permission_required('change_checkin')
def quick_check_out(request, reservation_id):
    """Quick check-out from list view"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if reservation.status == 'checked_in':
        try:
            # Update stay record
            stay = reservation.stay
            stay.actual_check_out = timezone.now()
            stay.save()
            
            # Generate invoice
            invoice = generate_invoice(stay)
            
            # Update statuses
            reservation.status = 'checked_out'
            reservation.save()
            
            reservation.room.status = 'Cleaning'
            reservation.room.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Guest checked out! Invoice #{invoice.invoice_number} generated.',
                'invoice_url': f'/billing/invoice/{invoice.id}/'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Cannot check out this reservation.'})

@owner_or_permission_required('add_checkin')
def check_in(request, reservation_id):
    """Check-in guest"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check if user has access
    if not request.user.is_superuser and reservation.hotel.owner != request.user:
        messages.error(request, 'You do not have access to this reservation.')
        return redirect('reservations:list')
    
    if reservation.status != 'confirmed':
        messages.error(request, 'Only confirmed reservations can be checked in.')
        return redirect('reservations:detail', reservation_id=reservation.id)
    
    if request.method == 'POST':
        # Create stay record
        stay = Stay.objects.create(
            reservation=reservation,
            room=reservation.room,
            actual_check_in=timezone.now(),
            notes=request.POST.get('notes', '')
        )
        
        # Update reservation status
        reservation.status = 'checked_in'
        reservation.save()
        
        # Update room status
        reservation.room.status = 'Occupied'
        reservation.room.save()
        
        messages.success(request, f'Guest {reservation.guest.full_name} checked in successfully!')
        return redirect('reservations:detail', reservation_id=reservation.id)
    
    return render(request, 'reservations/check_in.html', {'reservation': reservation})

@owner_or_permission_required('change_checkin')
def check_out(request, reservation_id):
    """Check-out guest and generate invoice"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check if user has access
    if not request.user.is_superuser and reservation.hotel.owner != request.user:
        messages.error(request, 'You do not have access to this reservation.')
        return redirect('reservations:list')
    
    if reservation.status != 'checked_in':
        messages.error(request, 'Only checked-in guests can be checked out.')
        return redirect('reservations:detail', reservation_id=reservation.id)
    
    if request.method == 'POST':
        try:
            # Update stay record
            stay = reservation.stay
            stay.actual_check_out = timezone.now()
            stay.notes += f"\nCheck-out notes: {request.POST.get('notes', '')}"
            stay.save()
            
            # Generate invoice
            invoice = generate_invoice(stay)
            
            # Update reservation status
            reservation.status = 'checked_out'
            reservation.save()
            
            # Update room status
            reservation.room.status = 'Cleaning'
            reservation.room.save()
            
            messages.success(request, f'Guest {reservation.guest.full_name} checked out successfully! Invoice #{invoice.invoice_number} generated.')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
            
        except Exception as e:
            messages.error(request, f'Error during checkout: {str(e)}')
            return redirect('reservations:detail', reservation_id=reservation.id)
    
    return render(request, 'reservations/check_out.html', {'reservation': reservation})

def generate_invoice(stay):
    """Generate invoice for checkout with Pakistan tax system"""
    reservation = stay.reservation
    
    # Generate unique invoice number
    invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(stay.id)[:8].upper()}"
    
    # Create invoice
    invoice = Invoice.objects.create(
        stay=stay,
        guest=reservation.guest,
        invoice_number=invoice_number,
        due_date=timezone.now().date() + timedelta(days=30),
        currency='PKR',
        status='draft'
    )
    
    # Calculate room charges
    nights = (stay.actual_check_out.date() - stay.actual_check_in.date()).days
    if nights == 0:
        nights = 1  # Minimum 1 night charge
    
    room_total = reservation.rate * nights
    
    # Add room charge item
    ChargeItem.objects.create(
        invoice=invoice,
        description=f"Room {reservation.room.room_number} - {nights} night(s)",
        charge_type='room',
        quantity=nights,
        unit_price=reservation.rate,
        amount=room_total
    )
    
    # Pakistan tax calculations
    subtotal = room_total
    
    # Service charges (10%)
    service_charge = subtotal * Decimal('0.10')
    ChargeItem.objects.create(
        invoice=invoice,
        description="Service Charges (10%)",
        charge_type='service',
        quantity=1,
        unit_price=service_charge,
        amount=service_charge
    )
    
    # Sales Tax (17% in Pakistan)
    tax_amount = (subtotal + service_charge) * Decimal('0.17')
    ChargeItem.objects.create(
        invoice=invoice,
        description="Sales Tax (17%)",
        charge_type='tax',
        quantity=1,
        unit_price=tax_amount,
        amount=tax_amount
    )
    
    # Update invoice totals
    invoice.subtotal = subtotal
    invoice.service_charge = service_charge
    invoice.tax_amount = tax_amount
    invoice.total_amount = subtotal + service_charge + tax_amount
    invoice.status = 'sent'
    invoice.save()
    
    return invoice