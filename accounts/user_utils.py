from django.contrib import messages
from .email_utils import send_employee_welcome_email
import logging

logger = logging.getLogger(__name__)

def create_user_with_email(user_data, password, created_by_user, request=None):
    """
    Create a user and send welcome email
    
    Args:
        user_data: Dictionary with user fields (username, email, first_name, etc.)
        password: Plain text password
        created_by_user: User who is creating this account
        request: HTTP request object for messages (optional)
    
    Returns:
        tuple: (user_object, email_sent_successfully)
    """
    from .models import User
    
    try:
        # Create user
        user = User.objects.create_user(**user_data)
        user.set_password(password)
        user.save()
        
        # Send welcome email
        email_sent = False
        try:
            send_employee_welcome_email(user, password, created_by_user)
            email_sent = True
            if request:
                messages.success(request, f'{user.get_full_name() or user.username} created successfully! Welcome email sent.')
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            if request:
                messages.success(request, f'{user.get_full_name() or user.username} created successfully!')
                messages.warning(request, 'Welcome email could not be sent.')
        
        return user, email_sent
        
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        if request:
            messages.error(request, f'Failed to create user: {str(e)}')
        raise e

def send_welcome_email_to_existing_user(user, password, created_by_user, request=None):
    """
    Send welcome email to an existing user (useful for password resets or account activations)
    
    Args:
        user: User object
        password: Plain text password to send
        created_by_user: User who is sending this email
        request: HTTP request object for messages (optional)
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        send_employee_welcome_email(user, password, created_by_user)
        if request:
            messages.success(request, f'Welcome email sent to {user.get_full_name() or user.username}.')
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        if request:
            messages.warning(request, 'Welcome email could not be sent.')
        return False