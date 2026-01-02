from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Room
from .activity_models import RoomActivityLog
import threading

User = get_user_model()

# Thread-local storage to track the current user
_thread_locals = threading.local()

def set_current_user(user):
    """Set the current user in thread-local storage"""
    _thread_locals.user = user

def get_current_user():
    """Get the current user from thread-local storage"""
    return getattr(_thread_locals, 'user', None)

# All room-related signals
@receiver(post_save)
def log_all_room_activities(sender, instance, created, **kwargs):
    """Universal signal handler for all room-related activities"""
    user = get_current_user()
    room = None
    
    # Reservations
    if sender._meta.app_label == 'reservations' and sender._meta.model_name == 'reservation':
        room = getattr(instance, 'room', None)
        if room:
            if created:
                RoomActivityLog.log_activity(
                    room=room, user=user, action='reservation_created',
                    description=f'Reservation created for {getattr(instance, "guest_name", "Guest")} - #{instance.id}',
                    metadata={'guest_name': getattr(instance, 'guest_name', ''), 'check_in': str(getattr(instance, 'check_in_date', '')), 
                             'check_out': str(getattr(instance, 'check_out_date', '')), 'total_amount': str(getattr(instance, 'total_amount', ''))}
                )
            elif hasattr(instance, '_old_status'):
                if getattr(instance, 'status', '') == 'checked_in':
                    RoomActivityLog.log_activity(room=room, user=user, action='guest_checkin',
                        description=f'{getattr(instance, "guest_name", "Guest")} checked in - #{instance.id}',
                        metadata={'guest_name': getattr(instance, 'guest_name', ''), 'total_amount': str(getattr(instance, 'total_amount', ''))})
                elif getattr(instance, 'status', '') == 'checked_out':
                    RoomActivityLog.log_activity(room=room, user=user, action='guest_checkout',
                        description=f'{getattr(instance, "guest_name", "Guest")} checked out - #{instance.id}',
                        metadata={'guest_name': getattr(instance, 'guest_name', ''), 'total_amount': str(getattr(instance, 'total_amount', ''))})
    
    # Payments
    elif sender._meta.app_label == 'billing' and 'payment' in sender._meta.model_name.lower():
        reservation = getattr(instance, 'reservation', None)
        if reservation and hasattr(reservation, 'room'):
            room = reservation.room
            if created:
                RoomActivityLog.log_activity(room=room, user=user, action='payment_received',
                    description=f'Payment received: {getattr(instance, "currency", "PKR")} {getattr(instance, "amount", "0")} - {getattr(instance, "payment_method", "Cash")}',
                    metadata={'payment_id': instance.id, 'amount': str(getattr(instance, 'amount', '')), 
                             'currency': getattr(instance, 'currency', ''), 'method': getattr(instance, 'payment_method', ''),
                             'guest_name': getattr(reservation, 'guest_name', '')})
    
    # Housekeeping
    elif sender._meta.app_label == 'housekeeping':
        room = getattr(instance, 'room', None)
        if room and created:
            if 'schedule' in sender._meta.model_name.lower():
                RoomActivityLog.log_activity(room=room, user=user, action='housekeeping_assigned',
                    description=f'Housekeeping assigned - {getattr(instance, "shift", "")} shift',
                    metadata={'staff': str(getattr(instance, 'assigned_staff', '')), 'shift': getattr(instance, 'shift', '')})
            elif 'task' in sender._meta.model_name.lower():
                RoomActivityLog.log_activity(room=room, user=user, action='cleaning_completed',
                    description=f'Cleaning task: {getattr(instance, "task_type", "General cleaning")}',
                    metadata={'task_type': getattr(instance, 'task_type', ''), 'status': getattr(instance, 'status', '')})
    
    # Maintenance
    elif sender._meta.app_label == 'maintenance':
        room = getattr(instance, 'room', None)
        if room and created:
            RoomActivityLog.log_activity(room=room, user=user, action='maintenance_request',
                description=f'Maintenance request: {getattr(instance, "issue_type", "General issue")}',
                metadata={'issue_type': getattr(instance, 'issue_type', ''), 'priority': getattr(instance, 'priority', ''), 
                         'description': getattr(instance, 'description', '')})
    
    # Staff assignments
    elif sender._meta.app_label == 'staff':
        room = getattr(instance, 'room', None) or getattr(instance, 'assigned_room', None)
        if room and created:
            RoomActivityLog.log_activity(room=room, user=user, action='assignment',
                description=f'Staff assigned: {getattr(instance, "staff_member", "Staff")}',
                metadata={'staff_name': str(getattr(instance, 'staff_member', '')), 'role': getattr(instance, 'role', '')})

@receiver(pre_save)
def track_all_changes(sender, instance, **kwargs):
    """Track changes for all models"""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_status = getattr(old_instance, 'status', None)
            instance._old_instance = old_instance
        except sender.DoesNotExist:
            pass

@receiver(pre_save, sender=Room)
def track_room_changes(sender, instance, **kwargs):
    """Track changes to room before saving"""
    if instance.pk:  # Only for existing rooms
        try:
            old_room = Room.objects.get(pk=instance.pk)
            instance._old_room = old_room
        except Room.DoesNotExist:
            instance._old_room = None
    else:
        instance._old_room = None

@receiver(post_save, sender=Room)
def log_room_activity(sender, instance, created, **kwargs):
    """Log room activities after saving"""
    user = get_current_user()
    
    if created:
        # New room created
        RoomActivityLog.log_activity(
            room=instance,
            user=user,
            action='other',
            description=f'Room {instance.room_number} created',
            metadata={'room_type': instance.room_type.name if instance.room_type else None}
        )
    else:
        # Room updated - check for changes
        old_room = getattr(instance, '_old_room', None)
        if old_room:
            # Check status change
            if old_room.status != instance.status:
                RoomActivityLog.log_activity(
                    room=instance,
                    user=user,
                    action='status_change',
                    description=f'Room status changed from {old_room.status} to {instance.status}',
                    old_value=old_room.status,
                    new_value=instance.status
                )
            
            # Check price change
            if old_room.price != instance.price:
                RoomActivityLog.log_activity(
                    room=instance,
                    user=user,
                    action='price_change',
                    description=f'Room price changed from {old_room.price} to {instance.price}',
                    old_value=str(old_room.price),
                    new_value=str(instance.price)
                )
            
            # Check room type change
            if old_room.room_type != instance.room_type:
                old_type = old_room.room_type.name if old_room.room_type else 'None'
                new_type = instance.room_type.name if instance.room_type else 'None'
                RoomActivityLog.log_activity(
                    room=instance,
                    user=user,
                    action='other',
                    description=f'Room type changed from {old_type} to {new_type}',
                    old_value=old_type,
                    new_value=new_type
                )
            
            # Check amenity changes
            amenity_changes = []
            amenity_fields = [
                ('has_wifi', 'Wi-Fi'), ('has_ac', 'Air Conditioning'), ('has_tv', 'TV'),
                ('has_minibar', 'Mini Bar'), ('has_balcony', 'Balcony'), ('has_work_desk', 'Work Desk'),
                ('has_seating_area', 'Seating Area'), ('has_kitchenette', 'Kitchenette'), ('has_living_room', 'Living Room')
            ]
            
            for field, display_name in amenity_fields:
                old_val = getattr(old_room, field)
                new_val = getattr(instance, field)
                if old_val != new_val:
                    status = 'added' if new_val else 'removed'
                    amenity_changes.append(f'{display_name} {status}')
            
            if amenity_changes:
                RoomActivityLog.log_activity(
                    room=instance,
                    user=user,
                    action='amenity_change',
                    description=f'Amenities updated: {", ".join(amenity_changes)}',
                    metadata={'changes': amenity_changes}
                )