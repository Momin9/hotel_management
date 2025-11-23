from django.shortcuts import render, get_object_or_404, redirect

from .forms import *
from .models import *


def index(request):
    visitor_stats = VisitorStats.objects.last()
    booking_stats = BookingStats.objects.last()
    revenue_stats = RevenueStats.objects.last()
    room_stats = RoomStats.objects.last()
    bookings = Booking.objects.all()

    context = {
        'visitor_stats': visitor_stats,
        'booking_stats': booking_stats,
        'revenue_stats': revenue_stats,
        'room_stats': room_stats,
        'bookings': bookings,
    }

    return render(request, 'admin_dashboard/index.html', context)


def team_list(request):
    team_members = TeamMember.objects.all()
    return render(request, 'admin_dashboard/team-list.html', {'team_members': team_members})


def team_profile(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    return render(request, 'admin_dashboard/team-profile.html', {'team_member': team_member})


def team_add(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('team-list')
    else:
        form = TeamMemberForm()
    return render(request, 'admin_dashboard/team-add.html', {'form': form})


def team_update(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=team_member)
        if form.is_valid():
            form.save()
            return redirect('team-list')
    else:
        form = TeamMemberForm(instance=team_member)
    return render(request, 'admin_dashboard/team-update.html', {'form': form, 'team_member': team_member})
