from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from notifications.models import Notification
from accounts.models import User

def create_maintenance_request_notification(maintenance_request):
    """Create notifications for maintenance requests"""
    # Get managers and admins for the hotel
    hotel = maintenance_request.room.hotel if maintenance_request.room else None
    
    if hotel:
        # Get hotel owner and managers assigned to this hotel
        recipients = User.objects.filter(
            models.Q(owned_hotels=hotel) |  # Hotel owner
            models.Q(assigned_hotel=hotel, role='Manager'),  # Managers
            is_active=True
        ).distinct()
    else:
        recipients = User.objects.filter(
            role__in=['Manager', 'Owner'],
            is_active=True
        )
    
    # Create notifications
    for user in recipients:
        Notification.objects.create(
            user=user,
            title='New Maintenance Request',
            message=f'Room {maintenance_request.room.room_number} requires maintenance: {maintenance_request.description[:50]}...',
            notification_type='maintenance',
            status='unread'
        )
        
        # Send email notification
        try:
            send_mail(
                subject='New Maintenance Request',
                message=f'A new maintenance request has been created for Room {maintenance_request.room.room_number}.\n\nDescription: {maintenance_request.description}\n\nReported by: {maintenance_request.reported_by.get_full_name()}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except:
            pass  # Email sending is optional

def auto_assign_checkout_task(room):
    """Auto-assign housekeeping task when room is checked out"""
    from .models import HousekeepingTask
    
    # Find available housekeeper
    available_housekeeper = User.objects.filter(
        role='Housekeeping',
        assigned_hotel=room.hotel,
        is_active=True
    ).first()
    
    if available_housekeeper:
        task = HousekeepingTask.objects.create(
            room=room,
            assigned_staff=available_housekeeper,
            task_type='checkout_cleaning',
            status='pending',
            priority=3,
            description=f'Room {room.room_number} needs cleaning after checkout'
        )
        
        # Notify the housekeeper
        Notification.objects.create(
            user=available_housekeeper,
            title='New Room Assignment',
            message=f'You have been assigned to clean Room {room.room_number}',
            notification_type='task',
            status='unread'
        )
        
        return task
    
    return None