from .activity_models import RoomActivityLog
from .signals import get_current_user

def log_room_activity(room, action, description, **metadata):
    """Helper function to manually log room activities"""
    user = get_current_user()
    return RoomActivityLog.log_activity(
        room=room,
        user=user,
        action=action,
        description=description,
        **metadata
    )

def log_guest_activity(room, guest_name, action_type, **details):
    """Log guest-related activities"""
    user = get_current_user()
    
    if action_type == 'checkin':
        description = f'{guest_name} checked in'
        action = 'guest_checkin'
    elif action_type == 'checkout':
        description = f'{guest_name} checked out'
        action = 'guest_checkout'
    else:
        description = f'Guest activity: {action_type}'
        action = 'other'
    
    return RoomActivityLog.log_activity(
        room=room,
        user=user,
        action=action,
        description=description,
        metadata={'guest_name': guest_name, **details}
    )

def log_payment_activity(room, amount, currency='PKR', method='Cash', guest_name=''):
    """Log payment activities"""
    user = get_current_user()
    return RoomActivityLog.log_activity(
        room=room,
        user=user,
        action='payment_received',
        description=f'Payment received: {currency} {amount} via {method}',
        metadata={
            'amount': str(amount),
            'currency': currency,
            'method': method,
            'guest_name': guest_name
        }
    )

def log_maintenance_activity(room, issue_type, description='', priority='medium'):
    """Log maintenance activities"""
    user = get_current_user()
    return RoomActivityLog.log_activity(
        room=room,
        user=user,
        action='maintenance_request',
        description=f'Maintenance: {issue_type} - {description}',
        metadata={
            'issue_type': issue_type,
            'priority': priority,
            'description': description
        }
    )

def log_housekeeping_activity(room, task_type, staff_name='', status='assigned'):
    """Log housekeeping activities"""
    user = get_current_user()
    return RoomActivityLog.log_activity(
        room=room,
        user=user,
        action='housekeeping_assigned' if status == 'assigned' else 'cleaning_completed',
        description=f'Housekeeping: {task_type} - {status}',
        metadata={
            'task_type': task_type,
            'staff_name': staff_name,
            'status': status
        }
    )