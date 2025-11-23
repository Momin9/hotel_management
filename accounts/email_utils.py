from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def send_subscription_welcome_email(subscription, password=None):
    """
    Send VIP welcome email to hotel owner when subscription is created
    """
    try:
        hotel = subscription.hotel
        owner = hotel.owner
        plan = subscription.plan
        
        # Build login URL
        login_url = f"http://127.0.0.1:8000{reverse('accounts:login')}"
        
        # Email context
        context = {
            'owner_name': owner.get_full_name() or owner.username,
            'owner_email': owner.email,
            'username': owner.username,
            'password': password or 'Your existing password',
            'hotel_name': hotel.name,
            'plan_name': plan.name,
            'plan_price': plan.price_monthly,
            'max_rooms': plan.max_rooms,
            'max_managers': plan.max_managers,
            'start_date': subscription.start_date.strftime('%B %d, %Y'),
            'end_date': subscription.end_date.strftime('%B %d, %Y'),
            'billing_cycle': subscription.billing_cycle,
            'login_url': login_url,
        }
        
        # Render email template
        html_message = render_to_string('emails/subscription_welcome.html', context)
        plain_message = strip_tags(html_message)
        
        # Email subject
        subject = f'🎉 Welcome to AuraStay - Your {plan.name} Subscription is Active!'
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {owner.email} for hotel {hotel.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        return False

def send_subscription_update_email(subscription, action='updated'):
    """
    Send email notification when subscription is updated or cancelled
    """
    try:
        hotel = subscription.hotel
        owner = hotel.owner
        plan = subscription.plan
        
        if action == 'cancelled':
            subject = f'⚠️ Subscription Cancelled - {hotel.name}'
            message = f"""
            Dear {owner.get_full_name()},
            
            Your {plan.name} subscription for {hotel.name} has been cancelled.
            
            If you have any questions, please contact our support team.
            
            Best regards,
            AuraStay Team
            """
        else:
            subject = f'✅ Subscription Updated - {hotel.name}'
            message = f"""
            Dear {owner.get_full_name()},
            
            Your subscription for {hotel.name} has been updated.
            Plan: {plan.name}
            Status: {subscription.status.title()}
            
            Best regards,
            AuraStay Team
            """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner.email],
            fail_silently=True,
        )
        
        logger.info(f"Update email sent to {owner.email} for hotel {hotel.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send update email: {str(e)}")
        return False

def send_employee_welcome_email(employee, password, created_by_user):
    """
    Send welcome email to newly created employee
    """
    try:
        # Build login URL
        login_url = f"http://127.0.0.1:8000{reverse('accounts:login')}"
        
        # Get hotel name
        hotel_name = employee.assigned_hotel.name if employee.assigned_hotel else 'Your Hotel'
        
        # Role display mapping
        role_display_map = {
            'Manager': 'Hotel Manager',
            'Staff': 'Hotel Staff', 
            'Owner': 'Hotel Owner',
            'front_desk': 'Front Desk Staff',
            'housekeeping': 'Housekeeping Staff',
            'maintenance': 'Maintenance Staff',
            'kitchen_staff': 'Kitchen Staff',
            'accountant': 'Accountant'
        }
        
        # Email context
        context = {
            'employee_name': employee.get_full_name() or employee.username,
            'employee_email': employee.email,
            'username': employee.username,
            'password': password,
            'role_display': role_display_map.get(employee.role, employee.role),
            'hotel_name': hotel_name,
            'created_by': created_by_user.get_full_name() or created_by_user.username,
            'login_url': login_url,
        }
        
        # Render email template
        html_message = render_to_string('emails/employee_welcome.html', context)
        plain_message = strip_tags(html_message)
        
        # Email subject
        subject = f'🎉 Welcome to AuraStay - Your {role_display_map.get(employee.role, employee.role)} Account is Ready!'
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[employee.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {employee.email} for role {employee.role}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send employee welcome email: {str(e)}")
        return False