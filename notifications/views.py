from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification

@login_required
def notification_list(request):
    """List all notifications for the user"""
    notifications = request.user.notifications.all()[:20]
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient_user=request.user)
    notification.status = 'read'
    notification.read_at = timezone.now()
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications:list')

@login_required
def mark_all_as_read(request):
    """Mark all notifications as read for the user"""
    request.user.notifications.filter(status__in=['pending', 'sent']).update(
        status='read',
        read_at=timezone.now()
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications:list')