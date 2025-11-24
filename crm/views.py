from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import GuestProfile
from accounts.decorators import owner_or_permission_required
from hotels.models import Hotel
from reservations.models import Reservation

@owner_or_permission_required('view_guest')
def guest_list(request):
    """List guests based on user role"""
    if request.user.is_superuser:
        guests = GuestProfile.objects.all().order_by('-created_at')
    elif request.user.role == 'Owner':
        # Hotel owners see guests from their hotels' reservations
        owned_hotels = Hotel.objects.filter(owner=request.user, deleted_at__isnull=True)
        guest_ids = Reservation.objects.filter(hotel__in=owned_hotels).values_list('guest_id', flat=True).distinct()
        guests = GuestProfile.objects.filter(id__in=guest_ids).order_by('-created_at')
    else:
        # Staff see guests from their assigned hotel's reservations
        if request.user.assigned_hotel:
            guest_ids = Reservation.objects.filter(hotel=request.user.assigned_hotel).values_list('guest_id', flat=True).distinct()
            guests = GuestProfile.objects.filter(id__in=guest_ids).order_by('-created_at')
        else:
            guests = GuestProfile.objects.none()
    
    return render(request, 'crm/list.html', {'guests': guests})

@owner_or_permission_required('add_guest')
def guest_create(request):
    """Create new guest"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date_of_birth = request.POST.get('date_of_birth') or None
        nationality = request.POST.get('nationality')
        address = request.POST.get('address')
        notes = request.POST.get('notes')
        
        guest = GuestProfile.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            date_of_birth=date_of_birth,
            nationality=nationality,
            address=address,
            notes=notes
        )
        
        messages.success(request, 'Guest created successfully!')
        return redirect('crm:list')
    
    return render(request, 'crm/create_modern.html')

@owner_or_permission_required('change_guest')
def guest_edit(request, guest_id):
    """Edit guest"""
    guest = get_object_or_404(GuestProfile, id=guest_id)
    
    if request.method == 'POST':
        guest.first_name = request.POST.get('first_name')
        guest.last_name = request.POST.get('last_name')
        guest.email = request.POST.get('email')
        guest.phone = request.POST.get('phone')
        guest.nationality = request.POST.get('nationality')
        guest.address = request.POST.get('address')
        guest.notes = request.POST.get('notes')
        guest.save()
        
        messages.success(request, 'Guest updated successfully!')
        return redirect('crm:detail', guest_id=guest.id)
    
    return render(request, 'crm/edit.html', {'guest': guest})

@owner_or_permission_required('view_guest')
def guest_detail(request, guest_id):
    """Guest detail view"""
    guest = get_object_or_404(GuestProfile, id=guest_id)
    return render(request, 'crm/detail.html', {'guest': guest})