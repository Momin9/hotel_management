from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import GuestProfile
from accounts.decorators import owner_or_permission_required
from hotels.models import Hotel, Company
from hotels.forms import GuestForm
from reservations.models import Reservation

@login_required
def guest_list(request):
    # Check if user has permission to view guests
    if not (request.user.is_superuser or 
            request.user.role == 'Owner' or
            request.user.can_view_guests):
        messages.error(request, 'You do not have permission to view guests.')
        return redirect('accounts:dashboard')
    """List guests based on user role with filtering"""
    if request.user.is_superuser:
        guests = GuestProfile.objects.filter(deleted_at__isnull=True)
    elif request.user.role == 'Owner':
        guests = GuestProfile.objects.filter(deleted_at__isnull=True)
    else:
        guests = GuestProfile.objects.filter(deleted_at__isnull=True)
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        guests = guests.filter(
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search) |
            models.Q(phone__icontains=search) |
            models.Q(national_id_card__icontains=search)
        )
    
    guest_type = request.GET.get('guest_type')
    if guest_type:
        guests = guests.filter(guest_type=guest_type)
    
    company = request.GET.get('company')
    if company:
        guests = guests.filter(company_id=company)
    
    nationality = request.GET.get('nationality')
    if nationality:
        guests = guests.filter(nationality=nationality)
    
    date_from = request.GET.get('date_from')
    if date_from:
        guests = guests.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        guests = guests.filter(created_at__date__lte=date_to)
    
    has_id_card = request.GET.get('has_id_card')
    if has_id_card == 'yes':
        guests = guests.exclude(national_id_card='')
    elif has_id_card == 'no':
        guests = guests.filter(national_id_card='')
    elif has_id_card == 'image':
        guests = guests.exclude(google_drive_file_link='')
    
    guests = guests.order_by('-created_at')
    
    # Get filter options
    from django_countries import countries
    companies = Company.objects.filter(is_active=True)
    # Get all countries for filter dropdown - convert to list of tuples
    nationalities = [(code, name) for code, name in countries]
    
    # Check permissions - these are handled by context processor now
    # can_add_guests = request.user.role == 'Owner' or request.user.can_add_guests
    # can_change_guests = request.user.role == 'Owner' or request.user.can_change_guests
    # can_delete_guests = request.user.role == 'Owner' or request.user.can_delete_guests
    
    return render(request, 'crm/list.html', {
        'guests': guests,
        'companies': companies,
        'nationalities': nationalities,
        # Permissions are now handled by context processor
        # 'can_add_guests': can_add_guests,
        # 'can_change_guests': can_change_guests,
        # 'can_delete_guests': can_delete_guests
    })

@login_required
def guest_create(request, hotel_id=None):
    # Check if user has permission to create guests
    if not (request.user.is_superuser or 
            request.user.role == 'Owner' or
            request.user.can_add_guests):
        messages.error(request, 'You do not have permission to create guests.')
        return redirect('crm:list')
    """Create new guest with company support"""
    hotel = None
    if hotel_id:
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    elif request.user.role == 'Owner':
        # Get the first hotel owned by the user
        hotel = request.user.owned_hotels.first()
    
    if request.method == 'POST':
        form = GuestForm(request.POST, request.FILES, hotel=hotel, user=request.user)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Guest "{guest.full_name}" created successfully!')
            if hotel:
                return redirect('hotels:hotel_detail', hotel_id=hotel.hotel_id)
            return redirect('crm:list')
    else:
        form = GuestForm(hotel=hotel, user=request.user)
    
    # Get companies for the hotel - ensure we always have companies
    companies = []
    if hotel:
        companies = Company.objects.filter(hotel=hotel, is_active=True)
    elif request.user.assigned_hotel:
        # If no hotel specified but user has assigned hotel
        companies = Company.objects.filter(hotel=request.user.assigned_hotel, is_active=True)
    
    return render(request, 'crm/create_modern.html', {
        'form': form,
        'hotel': hotel,
        'companies': companies
    })

@login_required
def guest_edit(request, guest_id, hotel_id=None):
    # Check if user has permission to edit guests
    if not (request.user.is_superuser or 
            request.user.role == 'Owner' or
            request.user.can_change_guests):
        messages.error(request, 'You do not have permission to edit guests.')
        return redirect('crm:list')
    """Edit guest with company support"""
    guest = get_object_or_404(GuestProfile, id=guest_id)
    hotel = None
    if hotel_id:
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    elif request.user.role == 'Owner':
        hotel = request.user.owned_hotels.first()
    
    if request.method == 'POST':
        # Update guest fields manually since template uses manual form fields
        guest.guest_type = request.POST.get('guest_type', 'individual')
        guest.first_name = request.POST.get('first_name', '')
        guest.last_name = request.POST.get('last_name', '')
        guest.email = request.POST.get('email', '')
        guest.phone = request.POST.get('phone', '')
        guest.date_of_birth = request.POST.get('date_of_birth') or None
        guest.nationality = request.POST.get('nationality', '')
        guest.address = request.POST.get('address', '')
        guest.national_id_card = request.POST.get('national_id_card', '')
        guest.notes = request.POST.get('notes', '')
        
        # Handle company assignment
        if guest.guest_type == 'company':
            company_id = request.POST.get('company')
            if company_id:
                try:
                    guest.company = Company.objects.get(id=company_id)
                except Company.DoesNotExist:
                    guest.company = None
            else:
                messages.error(request, 'Company is required for company guests.')
                return render(request, 'crm/edit.html', {
                    'guest': guest,
                    'hotel': hotel,
                    'companies': Company.objects.filter(hotel=hotel, is_active=True) if hotel else []
                })
        else:
            guest.company = None
        
        # Handle file upload
        if 'national_id_card_image' in request.FILES:
            guest.national_id_card_image = request.FILES['national_id_card_image']
        
        try:
            guest.save()
            messages.success(request, f'Guest "{guest.full_name}" updated successfully!')
            return redirect('crm:detail', guest_id=guest.id)
        except Exception as e:
            messages.error(request, f'Error updating guest: {str(e)}')
    
    # Get companies for the hotel - ensure we always have companies
    companies = []
    if hotel:
        companies = Company.objects.filter(hotel=hotel, is_active=True)
    elif request.user.assigned_hotel:
        # If no hotel specified but user has assigned hotel
        companies = Company.objects.filter(hotel=request.user.assigned_hotel, is_active=True)
    elif request.user.role == 'Owner' and request.user.owned_hotels.exists():
        # For owners, get companies from their first hotel
        companies = Company.objects.filter(hotel=request.user.owned_hotels.first(), is_active=True)
    
    return render(request, 'crm/edit.html', {
        'guest': guest,
        'hotel': hotel,
        'companies': companies
    })

@login_required
def guest_detail(request, guest_id):
    # Check if user has permission to view guests
    if not (request.user.is_superuser or 
            request.user.role == 'Owner' or
            request.user.can_view_guests):
        messages.error(request, 'You do not have permission to view guest details.')
        return redirect('crm:list')
    """Guest detail view"""
    guest = get_object_or_404(GuestProfile, id=guest_id)
    
    # Get guest's reservations
    try:
        from reservations.models import Reservation
        guest_reservations = Reservation.objects.filter(guest=guest).order_by('-check_in')
        last_reservation = guest_reservations.first()
    except ImportError:
        guest_reservations = []
        last_reservation = None
    
    # Get hotel context
    hotel = None
    if request.user.role == 'Owner':
        hotel = request.user.owned_hotels.first()
    
    return render(request, 'crm/detail.html', {
        'guest': guest,
        'guest_reservations': guest_reservations,
        'last_reservation': last_reservation,
        'hotel': hotel
    })

@login_required
def send_email(request, guest_id):
    # Check if user has permission to view guests
    if not (request.user.is_superuser or 
            request.user.role == 'Owner' or
            request.user.can_view_guests):
        messages.error(request, 'You do not have permission to send emails to guests.')
        return redirect('crm:list')
    """Send email to guest"""
    guest = get_object_or_404(GuestProfile, id=guest_id)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[guest.email],
                fail_silently=False,
            )
            messages.success(request, f'Email sent successfully to {guest.full_name}!')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
    
    return redirect('crm:detail', guest_id=guest_id)

@login_required
def guest_history(request, guest_id):
    # Check if user has permission to view guests
    if not (request.user.is_superuser or 
            request.user.role == 'Owner' or
            request.user.can_view_guests):
        messages.error(request, 'You do not have permission to view guest history.')
        return redirect('crm:list')
    """View guest reservation history"""
    guest = get_object_or_404(GuestProfile, id=guest_id)
    
    try:
        from reservations.models import Reservation
        reservations = Reservation.objects.filter(guest=guest).order_by('-check_in')
    except ImportError:
        reservations = []
    
    return render(request, 'crm/guest_history.html', {
        'guest': guest,
        'reservations': reservations
    })

@login_required
def guest_delete(request, guest_id):
    # Check if user has permission to delete guests
    if not (request.user.is_superuser or 
            request.user.role == 'Owner' or
            request.user.can_delete_guests):
        messages.error(request, 'You do not have permission to delete guests.')
        return redirect('crm:list')
    """Delete guest (soft delete)"""
    guest = get_object_or_404(GuestProfile, id=guest_id)
    
    if request.method == 'POST':
        # Check if guest has any reservations
        try:
            from reservations.models import Reservation
            active_reservations = Reservation.objects.filter(
                guest=guest, 
                status__in=['confirmed', 'checked_in']
            )
            if active_reservations.exists():
                messages.error(request, f'Cannot delete guest "{guest.full_name}" - they have active reservations.')
                return redirect('crm:detail', guest_id=guest_id)
        except ImportError:
            pass
        
        # Soft delete
        from django.utils import timezone
        guest.deleted_at = timezone.now()
        guest.save()
        
        messages.success(request, f'Guest "{guest.full_name}" deleted successfully!')
        return redirect('crm:list')
    
    return render(request, 'crm/delete.html', {'guest': guest})