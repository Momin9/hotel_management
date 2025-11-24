from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from twilio.rest import Client
from .models import Notification, NotificationTemplate
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email_notification(notification_id):
    """Send email notification"""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        send_mail(
            subject=notification.subject,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient_email],
            fail_silently=False,
        )
        
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        
        logger.info(f"Email sent successfully to {notification.recipient_email}")
        
    except Exception as e:
        notification.status = 'failed'
        notification.error_message = str(e)
        notification.save()
        logger.error(f"Failed to send email: {str(e)}")

@shared_task
def send_sms_notification(notification_id):
    """Send SMS notification"""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=notification.message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=notification.recipient_phone
            )
            
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.metadata['twilio_sid'] = message.sid
            notification.save()
            
            logger.info(f"SMS sent successfully to {notification.recipient_phone}")
        
    except Exception as e:
        notification.status = 'failed'
        notification.error_message = str(e)
        notification.save()
        logger.error(f"Failed to send SMS: {str(e)}")

@shared_task
def process_automated_notifications():
    """Process automated notifications based on triggers"""
    from django.utils import timezone
    from datetime import timedelta
    from reservations.models import Reservation
    from crm.models import GuestProfile
    
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Check-in reminders for tomorrow's arrivals
    arrivals_tomorrow = Reservation.objects.filter(
        check_in=tomorrow,
        status='confirmed'
    )
    
    for reservation in arrivals_tomorrow:
        template = NotificationTemplate.objects.filter(
            trigger='check_in_reminder',
            is_active=True
        ).first()
        
        if template and reservation.guest.email:
            notification = Notification.objects.create(
                recipient_guest=reservation.guest,
                recipient_email=reservation.guest.email,
                type='email',
                subject=template.subject,
                message=template.message.format(
                    guest_name=reservation.guest.full_name,
                    check_in_date=reservation.check_in,
                    property_name=reservation.hotel_property.name
                )
            )
            
            send_email_notification.delay(notification.id)
    
    # Check-out reminders for today's departures
    departures_today = Reservation.objects.filter(
        check_out=today,
        status='checked_in'
    )
    
    for reservation in departures_today:
        template = NotificationTemplate.objects.filter(
            trigger='check_out_reminder',
            is_active=True
        ).first()
        
        if template and reservation.guest.email:
            notification = Notification.objects.create(
                recipient_guest=reservation.guest,
                recipient_email=reservation.guest.email,
                type='email',
                subject=template.subject,
                message=template.message.format(
                    guest_name=reservation.guest.full_name,
                    check_out_date=reservation.check_out,
                    property_name=reservation.hotel_property.name
                )
            )
            
            send_email_notification.delay(notification.id)

@shared_task
def generate_daily_reports():
    """Generate daily reports"""
    from reporting.models import Report
    from django.contrib.auth.models import User
    
    # Generate occupancy report
    admin_users = User.objects.filter(is_superuser=True)
    
    for user in admin_users:
        report = Report.objects.create(
            name=f"Daily Occupancy Report - {timezone.now().date()}",
            type='occupancy',
            generated_by=user,
            date_from=timezone.now().date(),
            date_to=timezone.now().date(),
            status='generating'
        )
        
        # Generate report data (simplified)
        # In a real implementation, this would generate actual report data
        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save()

@shared_task
def cleanup_old_notifications():
    """Clean up old notifications"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Delete notifications older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count = Notification.objects.filter(
        created_at__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old notifications")

@shared_task
def update_room_status_automation():
    """Automated room status updates"""
    from housekeeping.models import HousekeepingTask
    from hotels.models import Room
    from django.utils import timezone
    
    # Auto-create housekeeping tasks for checked-out rooms
    dirty_rooms = Room.objects.filter(status='dirty')
    
    for room in dirty_rooms:
        # Check if there's already a pending task
        existing_task = HousekeepingTask.objects.filter(
            room=room,
            status='pending',
            task_type='checkout_cleaning'
        ).exists()
        
        if not existing_task:
            # Find available housekeeping staff
            from staff.models import Staff
            housekeeper = Staff.objects.filter(
                role='housekeeper',
                is_active=True
            ).first()
            
            if housekeeper:
                HousekeepingTask.objects.create(
                    room=room,
                    assigned_staff=housekeeper,
                    task_type='checkout_cleaning',
                    description=f'Clean room {room.room_number} after checkout',
                    priority=3
                )