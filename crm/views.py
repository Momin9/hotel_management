from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import GuestProfile

@login_required
def guest_list(request):
    """List all guests"""
    guests = GuestProfile.objects.all().order_by('-created_at')
    return render(request, 'crm/list.html', {'guests': guests})

@login_required
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

@login_required
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

@login_required
def guest_detail(request, guest_id):
    """Guest detail view"""
    guest = get_object_or_404(GuestProfile, id=guest_id)
    return render(request, 'crm/detail.html', {'guest': guest})