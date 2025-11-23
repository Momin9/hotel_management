from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Sum
from .models import CheckInOut, WalkInReservation, GuestFolio, FolioCharge, NightAudit
from reservations.models import Reservation
from hotels.models import Room
from crm.models import GuestProfile
import json

@login_required
def front_desk_dashboard(request):
    """Front desk main dashboard"""
    today = timezone.now().date()
    
    # Today's arrivals and departures
    # Mock data for demo
    arrivals = []
    departures = []
    
    # Current occupancy
    # Mock data since tables don't exist yet
    occupied_rooms = 0
    
    # Walk-ins today
    walk_ins = []
    
    context = {
        'arrivals': arrivals,
        'departures': departures,
        'occupied_rooms': occupied_rooms,
        'walk_ins': walk_ins,
        'today': today,
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