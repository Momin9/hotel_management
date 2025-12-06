from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Sum
from .models import CheckInOut, WalkInReservation, GuestFolio, FolioCharge, NightAudit
from reservations.models import Reservation
from hotels.models import Room, Hotel
from crm.models import GuestProfile
import json
from django.views.decorators.http import require_http_methods

@login_required
def front_desk_dashboard(request):
    """Front desk main dashboard"""
    today = timezone.now().date()
    
    # Today's arrivals (confirmed reservations for today)
    arrivals = Reservation.objects.filter(
        check_in=today,
        status='confirmed'
    ).select_related('guest', 'room')
    
    # Today's departures (checked-in guests checking out today)
    departures = Reservation.objects.filter(
        check_out=today,
        status='checked_in'
    ).select_related('guest', 'room')
    
    # Current occupancy (checked-in guests)
    occupied_rooms = Reservation.objects.filter(
        status='checked_in'
    ).count()
    
    # Walk-ins today (reservations created today with direct booking)
    walk_ins = Reservation.objects.filter(
        created_at__date=today,
        booking_source='walk_in'
    ).select_related('guest', 'room')
    
    context = {
        'arrivals': arrivals,
        'departures': departures,
        'occupied_rooms': occupied_rooms,
        'walk_ins': walk_ins,
        'today': today,
        'arrivals_count': arrivals.count(),
        'departures_count': departures.count(),
        'walk_ins_count': walk_ins.count(),
    }
    
    return render(request, 'front_desk/dashboard.html', context)

@login_required
def check_in_guest(request, reservation_id):
    """Check-in a guest"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        # Assign room if not already assigned
        room_id = request.POST.get('room_id')
        if room_id:
            room = get_object_or_404(Room, id=room_id)
        else:
            # Auto-assign available room of the reserved type
            room = Room.objects.filter(
                room_type=reservation.room_type,
                status='clean'
            ).first()
        
        if not room:
            messages.error(request, 'No available rooms of the reserved type.')
            return redirect('front_desk:dashboard')
        
        # Create check-in record
        checkin = CheckInOut.objects.create(
            reservation=reservation,
            guest=reservation.guest,
            room=room,
            checked_in_at=timezone.now(),
            checked_in_by=request.user,
            number_of_guests=request.POST.get('number_of_guests', reservation.adults),
            special_requests=request.POST.get('special_requests', ''),
            incidental_deposit=request.POST.get('incidental_deposit', 0)
        )
        
        # Update reservation status
        reservation.status = 'checked_in'
        reservation.save()
        
        # Update room status
        room.status = 'occupied'
        room.save()
        
        # Create guest folio
        folio_number = f"F{timezone.now().strftime('%Y%m%d')}{checkin.id.hex[:6].upper()}"
        GuestFolio.objects.create(
            checkin_record=checkin,
            guest=reservation.guest,
            folio_number=folio_number,
            room_charges=reservation.rate * reservation.total_nights
        )
        
        messages.success(request, f'Guest {reservation.guest.full_name} checked in successfully to room {room.room_number}')
        return redirect('front_desk:dashboard')
    
    # Get available rooms for the reservation
    available_rooms = Room.objects.filter(
        room_type=reservation.room_type,
        status='clean'
    )
    
    context = {
        'reservation': reservation,
        'available_rooms': available_rooms,
    }
    
    return render(request, 'front_desk/check_in.html', context)

@login_required
def check_out_guest(request, checkin_id):
    """Check-out a guest"""
    checkin = get_object_or_404(CheckInOut, id=checkin_id)
    
    if request.method == 'POST':
        # Update check-in record
        checkin.checked_out_at = timezone.now()
        checkin.checked_out_by = request.user
        checkin.status = 'checked_out'
        checkin.save()
        
        # Update reservation status
        checkin.reservation.status = 'checked_out'
        checkin.reservation.save()
        
        # Update room status
        checkin.room.status = 'dirty'
        checkin.room.save()
        
        # Settle folio if requested
        if request.POST.get('settle_folio'):
            folio = checkin.folio
            folio.is_settled = True
            folio.settled_at = timezone.now()
            folio.save()
        
        messages.success(request, f'Guest {checkin.guest.full_name} checked out successfully from room {checkin.room.room_number}')
        return redirect('front_desk:dashboard')
    
    # Get folio details
    folio = getattr(checkin, 'folio', None)
    
    context = {
        'checkin': checkin,
        'folio': folio,
    }
    
    return render(request, 'front_desk/check_out.html', context)

@login_required
def walk_in_registration(request):
    """Register walk-in guests"""
    if request.method == 'POST':
        # Create or get guest profile
        email = request.POST.get('email')
        guest, created = GuestProfile.objects.get_or_create(
            email=email,
            defaults={
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'phone': request.POST.get('phone'),
            }
        )
        
        # Get room
        room = get_object_or_404(Room, id=request.POST.get('room_id'))
        
        # Create walk-in reservation
        walk_in = WalkInReservation.objects.create(
            guest=guest,
            room=room,
            property=room.room_type.property,
            check_in_date=request.POST.get('check_in_date'),
            check_out_date=request.POST.get('check_out_date'),
            number_of_guests=request.POST.get('number_of_guests', 1),
            rate_per_night=request.POST.get('rate_per_night'),
            total_amount=request.POST.get('total_amount'),
            created_by=request.user
        )
        
        messages.success(request, f'Walk-in guest {guest.full_name} registered successfully')
        return redirect('front_desk:dashboard')
    
    # Get available rooms
    available_rooms = Room.objects.filter(status='clean')
    
    context = {
        'available_rooms': available_rooms,
    }
    
    return render(request, 'front_desk/walk_in.html', context)

@login_required
def folio_management(request, folio_id):
    """Manage guest folio"""
    folio = get_object_or_404(GuestFolio, id=folio_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_charge':
            FolioCharge.objects.create(
                folio=folio,
                charge_type=request.POST.get('charge_type'),
                description=request.POST.get('description'),
                amount=request.POST.get('amount'),
                quantity=request.POST.get('quantity', 1),
                charged_by=request.user
            )
            
            # Update folio totals
            total_charges = folio.charges.aggregate(
                total=Sum('amount')
            )['total'] or 0
            folio.incidental_charges = total_charges
            folio.total_charges = folio.room_charges + folio.incidental_charges + folio.tax_amount
            folio.balance = folio.total_charges - folio.payments_received
            folio.save()
            
            messages.success(request, 'Charge added successfully')
        
        elif action == 'add_payment':
            payment_amount = float(request.POST.get('payment_amount', 0))
            folio.payments_received += payment_amount
            folio.balance = folio.total_charges - folio.payments_received
            folio.save()
            
            messages.success(request, 'Payment recorded successfully')
    
    charges = folio.charges.all().order_by('-charge_date')
    
    context = {
        'folio': folio,
        'charges': charges,
    }
    
    return render(request, 'front_desk/folio.html', context)

@login_required
def night_audit(request):
    """Perform night audit"""
    today = timezone.now().date()
    
    # Check if audit already performed today
    audit, created = NightAudit.objects.get_or_create(
        audit_date=today,
        defaults={
            'performed_by': request.user,
            'start_time': timezone.now(),
        }
    )
    
    if request.method == 'POST' and not audit.is_completed:
        # Calculate statistics
        occupied_rooms = CheckInOut.objects.filter(
            status='checked_in',
            checked_out_at__isnull=True
        ).count()
        
        total_revenue = GuestFolio.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum('total_charges'))['total'] or 0
        
        arrivals_count = CheckInOut.objects.filter(
            checked_in_at__date=today
        ).count()
        
        departures_count = CheckInOut.objects.filter(
            checked_out_at__date=today
        ).count()
        
        no_shows_count = Reservation.objects.filter(
            check_in=today,
            status='no_show'
        ).count()
        
        # Update audit record
        audit.total_occupied_rooms = occupied_rooms
        audit.total_revenue = total_revenue
        audit.arrivals_count = arrivals_count
        audit.departures_count = departures_count
        audit.no_shows_count = no_shows_count
        audit.end_time = timezone.now()
        audit.is_completed = True
        audit.notes = request.POST.get('notes', '')
        audit.save()
        
        messages.success(request, 'Night audit completed successfully')
        return redirect('front_desk:dashboard')
    
    context = {
        'audit': audit,
        'today': today,
    }
    
    return render(request, 'front_desk/night_audit.html', context)

@login_required
def check_in_list(request):
    """List of guests to check in"""
    return render(request, 'front_desk/check_in_list.html')

@login_required
def check_out_list(request):
    """List of guests to check out"""
    return render(request, 'front_desk/check_out_list.html')

@login_required
def room_availability(request):
    """Room availability dashboard with floor filtering"""
    from hotels.models import Hotel
    from configurations.models import Floor as ConfigFloor
    
    # Get user's hotel
    if hasattr(request.user, 'assigned_hotel') and request.user.assigned_hotel:
        hotel = request.user.assigned_hotel
    else:
        # For owners, get their first hotel
        hotel = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True).first()
    
    if not hotel:
        messages.error(request, 'No hotel assigned to your account.')
        return redirect('front_desk:dashboard')
    
    # Get all rooms for the hotel
    rooms = hotel.rooms.all().select_related('floor', 'room_type', 'bed_type')
    
    # Apply floor filter if provided
    floor_filter = request.GET.get('floor')
    if floor_filter:
        rooms = rooms.filter(floor_id=floor_filter)
    
    # Apply status filter if provided
    status_filter = request.GET.get('status')
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    
    # Apply search filter if provided
    search_query = request.GET.get('search')
    if search_query:
        rooms = rooms.filter(
            Q(room_number__icontains=search_query) |
            Q(room_type__name__icontains=search_query)
        )
    
    # Get available floors for the hotel
    floors = ConfigFloor.objects.filter(hotels=hotel, is_active=True).order_by('number')
    
    # Room status choices for filtering
    status_choices = Room.ROOM_STATUS_CHOICES
    
    # Group rooms by floor for better display
    rooms_by_floor = {}
    for room in rooms:
        floor_name = room.floor.name if room.floor else 'No Floor Assigned'
        if floor_name not in rooms_by_floor:
            rooms_by_floor[floor_name] = []
        rooms_by_floor[floor_name].append(room)
    
    # Room statistics
    total_rooms = rooms.count()
    available_rooms = rooms.filter(status='Available').count()
    occupied_rooms = rooms.filter(status='Occupied').count()
    dirty_rooms = rooms.filter(status='Dirty').count()
    maintenance_rooms = rooms.filter(status='Maintenance').count()
    
    context = {
        'hotel': hotel,
        'rooms': rooms,
        'rooms_by_floor': rooms_by_floor,
        'floors': floors,
        'status_choices': status_choices,
        'selected_floor': floor_filter,
        'selected_status': status_filter,
        'search_query': search_query,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'dirty_rooms': dirty_rooms,
        'maintenance_rooms': maintenance_rooms,
    }
    
    return render(request, 'front_desk/room_availability.html', context)

@login_required
def room_details_ajax(request, room_id):
    """Get room details via AJAX"""
    try:
        room = get_object_or_404(Room, room_id=room_id)
        
        # Check if user has access to this room's hotel
        user_hotel = None
        if hasattr(request.user, 'assigned_hotel') and request.user.assigned_hotel:
            user_hotel = request.user.assigned_hotel
        else:
            user_hotel = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True).first()
        
        if not user_hotel or room.hotel != user_hotel:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get current reservation if room is occupied
        current_reservation = None
        if room.status == 'Occupied':
            from reservations.models import Reservation
            current_reservation = Reservation.objects.filter(
                room=room,
                status='checked_in'
            ).select_related('guest').first()
        
        room_data = {
            'room_number': room.room_number,
            'status': room.status,
            'room_type': room.room_type.name if room.room_type else 'N/A',
            'bed_type': room.bed_type.name if room.bed_type else 'N/A',
            'floor': room.floor.name if room.floor else 'N/A',
            'max_guests': room.max_guests,
            'price': str(room.price),
            'amenities': room.amenities_list,
            'current_guest': None
        }
        
        if current_reservation:
            room_data['current_guest'] = {
                'name': current_reservation.guest.full_name,
                'check_in': current_reservation.check_in.strftime('%Y-%m-%d'),
                'check_out': current_reservation.check_out.strftime('%Y-%m-%d'),
                'adults': current_reservation.adults,
                'children': current_reservation.children
            }
        
        return JsonResponse(room_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def update_room_status(request, room_id):
    """Update room status via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        room = get_object_or_404(Room, room_id=room_id)
        
        # Check if user has access to this room's hotel
        user_hotel = None
        if hasattr(request.user, 'assigned_hotel') and request.user.assigned_hotel:
            user_hotel = request.user.assigned_hotel
        else:
            user_hotel = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True).first()
        
        if not user_hotel or room.hotel != user_hotel:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Room.ROOM_STATUS_CHOICES]
        
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        room.status = new_status
        room.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Room {room.room_number} status updated to {new_status}',
            'new_status': new_status
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)