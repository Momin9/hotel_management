from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from datetime import date, timedelta
from .roles import RoleManager
from .decorators import super_admin_required
from .email_utils import send_subscription_welcome_email, send_subscription_update_email, send_employee_welcome_email
from tenants.models import SubscriptionPlan
from hotels.models import Hotel, HotelSubscription, Payment, SubscriptionHistory

User = get_user_model()

def landing_page(request):
    """Landing page for AuraStay"""
    from .forms import ContactForm
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    contact_form = ContactForm()
    return render(request, 'accounts/landing.html', {'plans': plans, 'contact_form': contact_form})

def about_page(request):
    """About Us page for AuraStay"""
    from .models import AboutUs
    about_content = AboutUs.objects.filter(is_active=True).first()
    return render(request, 'accounts/about.html', {'about_us': about_content})

def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'accounts/privacy_policy.html')

def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'accounts/terms_of_service.html')


def footer_context(request):
    """Context processor to add footer data to all templates"""
    from .models import Footer
    footer = Footer.objects.first()
    return {'footer': footer}


def page_content_context(request):
    """Context processor to add page content data to all templates"""
    from .models import PageContent
    page_contents = {}
    for content in PageContent.objects.all():
        page_contents[content.page_name] = content
    return {'page_contents': page_contents}

def navigation_context(request):
    """Context processor to add navigation permissions"""
    if not request.user.is_authenticated:
        return {}
    
    from .permissions import check_user_permission
    
    nav_permissions = {
        'can_view_hotels': request.user.role == 'Owner' or check_user_permission(request.user, 'view_hotel'),
        'can_view_staff': request.user.role == 'Owner' or check_user_permission(request.user, 'view_staff'),
        'can_view_reservations': request.user.role == 'Owner' or check_user_permission(request.user, 'view_reservation'),
        'can_view_guests': request.user.role == 'Owner' or check_user_permission(request.user, 'view_guest'),
        'can_view_reports': request.user.role == 'Owner' or check_user_permission(request.user, 'view_reports'),
        'can_add_staff': request.user.role == 'Owner' or check_user_permission(request.user, 'add_staff'),
        'can_add_reservation': request.user.role == 'Owner' or check_user_permission(request.user, 'add_reservation'),
        'can_add_guest': request.user.role == 'Owner' or check_user_permission(request.user, 'add_guest'),
        'can_change_staff': request.user.role == 'Owner' or check_user_permission(request.user, 'change_staff'),
        'can_change_reservation': request.user.role == 'Owner' or check_user_permission(request.user, 'change_reservation'),
        'can_change_guest': request.user.role == 'Owner' or check_user_permission(request.user, 'change_guest'),
        'can_checkin': request.user.role == 'Owner' or check_user_permission(request.user, 'add_checkin'),
        'can_checkout': request.user.role == 'Owner' or check_user_permission(request.user, 'change_checkin'),
        'can_view_rooms': request.user.role == 'Owner' or check_user_permission(request.user, 'view_room'),
    }
    
    return nav_permissions

@csrf_protect
def contact_form(request):
    """Handle contact form submission"""
    from .forms import ContactForm
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_inquiry = form.save()
            
            # Create notification for admin users
            try:
                from notifications.models import Notification
                admin_users = User.objects.filter(is_superuser=True)
                
                notification_title = f'New {contact_inquiry.get_subject_display()} Request'
                notification_message = f'Name: {contact_inquiry.full_name}\nEmail: {contact_inquiry.work_email}\nHotel: {contact_inquiry.hotel_name}\nPhone: {contact_inquiry.phone_number}\nRooms: {contact_inquiry.get_number_of_rooms_display()}\nMessage: {contact_inquiry.message}'
                
                for admin in admin_users:
                    Notification.objects.create(
                        user=admin,
                        title=notification_title,
                        message=notification_message,
                        notification_type='info',
                        is_read=False
                    )
            except Exception as e:
                pass  # Fail silently if notifications not available
            
            messages.success(request, 'Thank you for your interest! Our team will contact you soon.')
            return redirect('accounts:landing')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    
    return redirect('accounts:landing')

def custom_login(request):
    """Custom login view with subscription access control"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check subscription status for non-superusers
            if not user.is_superuser:
                subscription_active = check_user_subscription_status(user)
                if not subscription_active:
                    messages.error(request, 'Your subscription has expired or is inactive. Please contact administrator.')
                    # Create notification for admin
                    create_admin_notification(
                        f'Login attempt blocked: {user.get_full_name()} - Inactive subscription',
                        'warning'
                    )
                    return render(request, 'accounts/login_luxury.html')
            
            login(request, user)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login_luxury.html')

def check_user_subscription_status(user):
    """Check if user's hotel has active subscription"""
    try:
        if user.role == 'Owner':
            # Check if owner's hotels have active subscriptions
            hotels = Hotel.objects.filter(owner=user, is_active=True)
            for hotel in hotels:
                active_subscription = HotelSubscription.objects.filter(
                    hotel=hotel,
                    status='active',
                    start_date__lte=date.today(),
                    end_date__gte=date.today()
                ).exists()
                if active_subscription:
                    return True
            return False
        elif user.assigned_hotel:
            # Check if staff's assigned hotel has active subscription
            return HotelSubscription.objects.filter(
                hotel=user.assigned_hotel,
                status='active',
                start_date__lte=date.today(),
                end_date__gte=date.today()
            ).exists()
        return True  # Default allow for other roles
    except Exception as e:
        print(f"Subscription check error: {e}")
        return False

def create_admin_notification(message, notification_type='info'):
    """Create notification for admin users"""
    try:
        from notifications.models import Notification
        admin_users = User.objects.filter(is_superuser=True)
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title='Subscription Access Alert',
                message=message,
                notification_type=notification_type,
                is_read=False
            )
    except:
        pass  # Fail silently if notifications app not available

def custom_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')

@login_required
def dashboard(request):
    """Role-based dashboard redirect with subscription check"""
    # Check subscription status for non-superusers
    if not request.user.is_superuser:
        subscription_active = check_user_subscription_status(request.user)
        if not subscription_active:
            messages.error(request, 'Your subscription has expired. Access denied.')
            logout(request)
            return redirect('accounts:login')
    
    if request.user.is_superuser:
        return redirect('accounts:super_admin_dashboard')
    elif request.user.role == 'Owner':
        return redirect('accounts:owner_dashboard')
    else:
        return redirect('accounts:employee_dashboard')

@super_admin_required
def super_admin_dashboard(request):
    """Main Super Admin Dashboard"""
    # Statistics (excluding soft-deleted records)
    total_users = User.objects.filter(deleted_at__isnull=True).count()
    hotel_owners = User.objects.filter(role='Owner', deleted_at__isnull=True).count()
    total_hotels = Hotel.objects.filter(deleted_at__isnull=True).count()
    active_hotels = Hotel.objects.filter(is_active=True, deleted_at__isnull=True).count()
    total_plans = SubscriptionPlan.objects.filter(deleted_at__isnull=True).count()
    active_plans = SubscriptionPlan.objects.filter(is_active=True, deleted_at__isnull=True).count()
    
    # Revenue
    try:
        monthly_revenue = Payment.objects.filter(
            payment_date__month=date.today().month,
            payment_date__year=date.today().year
        ).aggregate(total=Sum('amount'))['total'] or 0
    except:
        monthly_revenue = 0
    
    context = {
        'total_users': total_users,
        'hotel_owners': hotel_owners,
        'total_hotels': total_hotels,
        'active_hotels': active_hotels,
        'total_plans': total_plans,
        'active_plans': active_plans,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'accounts/dashboards/super_admin.html', context)

@login_required
def owner_dashboard(request):
    """Hotel Owner Dashboard"""
    # Get the first hotel owned by the user
    hotel = Hotel.objects.filter(owner=request.user).first()
    hotel_name = hotel.name if hotel else 'Hotel Owner'
    
    context = {
        'user_role': 'Hotel Owner',
        'hotel_name': hotel_name,
        'hotel': hotel
    }
    return render(request, 'accounts/dashboards/owner.html', context)

@login_required
def employee_dashboard(request):
    """Employee Dashboard"""
    context = {'user_role': 'Employee'}
    return render(request, 'accounts/dashboards/employee.html', context)

@login_required
@csrf_protect
def profile(request):
    """User profile view with edit functionality"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html')

@login_required
@csrf_protect
def reset_password(request):
    """Reset password functionality"""
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            user = request.user
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password updated successfully!')
        else:
            messages.error(request, 'Passwords do not match!')
        
        return redirect('accounts:profile')
    
    return redirect('accounts:profile')

# CRUD Views for Subscription Plans
@super_admin_required
def subscription_plan_list(request):
    """List all subscription plans (excluding soft-deleted)"""
    plans = SubscriptionPlan.objects.filter(deleted_at__isnull=True).order_by('price_monthly')
    return render(request, 'accounts/subscription_plans/list.html', {'plans': plans})

@super_admin_required
def subscription_plan_create(request):
    """Create new subscription plan"""
    if request.method == 'POST':
        plan = SubscriptionPlan.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            price_monthly=request.POST.get('price_monthly') or 0,
            price_yearly=request.POST.get('price_yearly') or 0,
            max_rooms=request.POST.get('max_rooms') or 50,
            max_managers=request.POST.get('max_managers') or 5,
            max_reports=request.POST.get('max_reports') or 10,
            has_advanced_analytics='has_advanced_analytics' in request.POST,
            has_priority_support='has_priority_support' in request.POST,
            is_active=True
        )
        messages.success(request, f'Subscription plan "{plan.name}" created successfully!')
        return redirect('accounts:subscription_plan_list')
    
    return render(request, 'accounts/subscription_plans/form.html')

@super_admin_required
def subscription_plan_edit(request, plan_id):
    """Edit subscription plan with deactivation handling"""
    plan = get_object_or_404(SubscriptionPlan, plan_id=plan_id)
    old_status = plan.is_active
    
    if request.method == 'POST':
        plan.name = request.POST.get('name')
        plan.description = request.POST.get('description', '')
        plan.price_monthly = request.POST.get('price_monthly') or 0
        plan.price_yearly = request.POST.get('price_yearly') or 0
        plan.max_rooms = request.POST.get('max_rooms') or 50
        plan.max_managers = request.POST.get('max_managers') or 5
        plan.max_reports = request.POST.get('max_reports') or 10
        
        # Handle checkbox values properly - if not checked, they won't be in POST data
        plan.has_advanced_analytics = 'has_advanced_analytics' in request.POST
        plan.has_priority_support = 'has_priority_support' in request.POST
        
        new_status = request.POST.get('is_active') == 'on'
        plan.is_active = new_status
        plan.save()
        
        # Handle plan deactivation
        if old_status and not new_status:
            handle_plan_deactivation(plan)
        
        messages.success(request, f'Subscription plan "{plan.name}" updated successfully!')
        return redirect('accounts:subscription_plan_list')
    
    return render(request, 'accounts/subscription_plans/form.html', {'plan': plan})

def handle_plan_deactivation(plan):
    """Handle subscription plan deactivation"""
    # Deactivate all hotel subscriptions using this plan
    affected_subscriptions = HotelSubscription.objects.filter(plan=plan, status='active')
    affected_hotels = []
    
    for subscription in affected_subscriptions:
        subscription.status = 'cancelled'
        subscription.save()
        affected_hotels.append(subscription.hotel)
        
        # Create subscription history
        SubscriptionHistory.objects.create(
            hotel_subscription=subscription,
            action='cancelled',
            action_date=date.today()
        )
    
    # Create admin notification
    if affected_hotels:
        hotel_names = ', '.join([hotel.name for hotel in affected_hotels])
        create_admin_notification(
            f'Plan "{plan.name}" deactivated. Affected hotels: {hotel_names}',
            'warning'
        )

@super_admin_required
def subscription_plan_delete(request, plan_id):
    """Soft delete subscription plan"""
    from django.utils import timezone
    plan = get_object_or_404(SubscriptionPlan, plan_id=plan_id)
    plan_name = plan.name
    plan.deleted_at = timezone.now()
    plan.is_active = False
    plan.save()
    messages.success(request, f'Subscription plan "{plan_name}" deleted successfully!')
    return redirect('accounts:subscription_plan_list')

# CRUD Views for Hotel Owners
@super_admin_required
def hotel_owner_list(request):
    """List all hotel owners (excluding soft-deleted)"""
    owners = User.objects.filter(role='Owner', deleted_at__isnull=True).order_by('-created_at')
    return render(request, 'accounts/hotel_owners/list.html', {'owners': owners})

@super_admin_required
def hotel_owner_create(request):
    """Create new hotel owner"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists!')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'User with this username already exists!')
        else:
            password = request.POST.get('password')
            owner = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone=request.POST.get('phone', ''),
                role='Owner',
                is_active=True
            )
            
            # Store password for potential email sending when subscription is created
            owner.temp_password = password
            owner.save()
            
            # Send welcome email to hotel owner
            try:
                send_employee_welcome_email(owner, password, request.user)
                messages.success(request, f'Hotel owner "{owner.first_name} {owner.last_name}" created successfully! Welcome email sent.')
            except Exception as e:
                messages.success(request, f'Hotel owner "{owner.first_name} {owner.last_name}" created successfully!')
                messages.warning(request, 'Welcome email could not be sent.')
            
            return redirect('accounts:hotel_owner_list')
    
    return render(request, 'accounts/hotel_owners/form.html')

@super_admin_required
def hotel_owner_edit(request, owner_id):
    """Edit hotel owner"""
    owner = get_object_or_404(User, user_id=owner_id, role='Owner')
    
    if request.method == 'POST':
        owner.username = request.POST.get('username')
        owner.first_name = request.POST.get('first_name')
        owner.last_name = request.POST.get('last_name')
        owner.phone = request.POST.get('phone', '')
        owner.is_active = request.POST.get('is_active') == 'on'
        
        password = request.POST.get('password')
        if password:
            owner.set_password(password)
        
        owner.save()
        messages.success(request, f'Hotel owner "{owner.first_name} {owner.last_name}" updated successfully!')
        return redirect('accounts:hotel_owner_list')
    
    return render(request, 'accounts/hotel_owners/form.html', {'owner': owner})

@super_admin_required
def hotel_owner_delete(request, owner_id):
    """Soft delete hotel owner"""
    from django.utils import timezone
    owner = get_object_or_404(User, user_id=owner_id, role='Owner')
    owner_name = f"{owner.first_name} {owner.last_name}"
    owner.deleted_at = timezone.now()
    owner.is_active = False
    owner.save()
    messages.success(request, f'Hotel owner "{owner_name}" deleted successfully!')
    return redirect('accounts:hotel_owner_list')

# CRUD Views for Hotels
@super_admin_required
def hotel_list(request):
    """List all hotels with filtering (excluding soft-deleted)"""
    status_filter = request.GET.get('status', '')
    
    hotels = Hotel.objects.select_related('owner').filter(deleted_at__isnull=True)
    
    if status_filter == 'active':
        hotels = hotels.filter(is_active=True)
    elif status_filter == 'inactive':
        hotels = hotels.filter(is_active=False)
    
    hotels = hotels.order_by('-created_at')
    
    context = {
        'hotels': hotels,
        'status_filter': status_filter,
        'total_hotels': Hotel.objects.filter(deleted_at__isnull=True).count(),
        'active_hotels': Hotel.objects.filter(is_active=True, deleted_at__isnull=True).count(),
        'inactive_hotels': Hotel.objects.filter(is_active=False, deleted_at__isnull=True).count(),
    }
    
    return render(request, 'accounts/hotels/list.html', context)

@super_admin_required
def hotel_create(request):
    """Create new hotel"""
    owners = User.objects.filter(role='Owner')
    
    if request.method == 'POST':
        owner_id = request.POST.get('owner')
        owner = get_object_or_404(User, user_id=owner_id, role='Owner')
        
        hotel = Hotel.objects.create(
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            country=request.POST.get('country'),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            owner=owner,
            is_active=True
        )
        messages.success(request, f'Hotel "{hotel.name}" created successfully!')
        return redirect('accounts:hotel_list')
    
    return render(request, 'accounts/hotels/form.html', {'owners': owners})

@super_admin_required
def hotel_edit(request, hotel_id):
    """Edit hotel"""
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    owners = User.objects.filter(role='Owner')
    
    if request.method == 'POST':
        owner_id = request.POST.get('owner')
        owner = get_object_or_404(User, user_id=owner_id, role='Owner')
        
        hotel.name = request.POST.get('name')
        hotel.address = request.POST.get('address')
        hotel.city = request.POST.get('city')
        hotel.country = request.POST.get('country')
        hotel.phone = request.POST.get('phone', '')
        hotel.email = request.POST.get('email', '')
        hotel.owner = owner
        hotel.is_active = request.POST.get('is_active') == 'on'
        hotel.save()
        
        messages.success(request, f'Hotel "{hotel.name}" updated successfully!')
        return redirect('accounts:hotel_list')
    
    return render(request, 'accounts/hotels/form.html', {'hotel': hotel, 'owners': owners})

@super_admin_required
def hotel_delete(request, hotel_id):
    """Soft delete hotel"""
    from django.utils import timezone
    hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
    hotel_name = hotel.name
    hotel.deleted_at = timezone.now()
    hotel.is_active = False
    hotel.save()
    messages.success(request, f'Hotel "{hotel_name}" deleted successfully!')
    return redirect('accounts:hotel_list')

@super_admin_required
def hotel_subscription_delete(request, subscription_id):
    """Soft delete hotel subscription"""
    from django.utils import timezone
    subscription = get_object_or_404(HotelSubscription, id=subscription_id)
    hotel_name = subscription.hotel.name
    subscription.status = 'cancelled'
    subscription.save()
    
    # Create subscription history
    SubscriptionHistory.objects.create(
        hotel_subscription=subscription,
        action='cancelled',
        action_date=date.today()
    )
    
    messages.success(request, f'Subscription for "{hotel_name}" deleted successfully!')
    return redirect('accounts:hotel_subscription_list')

# CRUD Views for Hotel Subscriptions
@super_admin_required
def hotel_subscription_list(request):
    """List all hotel subscriptions"""
    subscriptions = HotelSubscription.objects.select_related('hotel', 'plan').order_by('-created_at')
    return render(request, 'accounts/hotel_subscriptions/list.html', {'subscriptions': subscriptions})

@super_admin_required
def hotel_subscription_create(request):
    """Create new hotel subscription"""
    hotels = Hotel.objects.filter(is_active=True)
    plans = SubscriptionPlan.objects.filter(is_active=True)
    
    if request.method == 'POST':
        hotel_id = request.POST.get('hotel')
        plan_id = request.POST.get('plan')
        
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        plan = get_object_or_404(SubscriptionPlan, plan_id=plan_id)
        
        # Calculate end date based on billing cycle
        start_date = date.today()
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        
        if billing_cycle == 'yearly':
            end_date = start_date.replace(year=start_date.year + 1)
        else:
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)
        
        subscription = HotelSubscription.objects.create(
            hotel=hotel,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            billing_cycle=billing_cycle,
            status='active',
            auto_renew=request.POST.get('auto_renew') == 'on'
        )
        
        # Create payment record
        amount = plan.price_yearly if billing_cycle == 'yearly' else plan.price_monthly
        Payment.objects.create(
            hotel_subscription=subscription,
            amount=amount,
            payment_date=start_date,
            payment_method='admin_created',
            status='completed'
        )
        
        # Create subscription history
        SubscriptionHistory.objects.create(
            hotel_subscription=subscription,
            action='started',
            action_date=start_date
        )
        
        # Send welcome email to hotel owner
        try:
            # Get password if available
            password = getattr(hotel.owner, 'temp_password', None)
            send_subscription_welcome_email(subscription, password)
            messages.success(request, f'Subscription for "{hotel.name}" created successfully! Welcome email sent to owner.')
        except Exception as e:
            messages.success(request, f'Subscription for "{hotel.name}" created successfully!')
            messages.warning(request, 'Welcome email could not be sent.')
        
        return redirect('accounts:hotel_subscription_list')
    
    return render(request, 'accounts/hotel_subscriptions/form.html', {'hotels': hotels, 'plans': plans})

@super_admin_required
def hotel_subscription_edit(request, subscription_id):
    """Edit hotel subscription with status change handling"""
    subscription = get_object_or_404(HotelSubscription, id=subscription_id)
    hotels = Hotel.objects.filter(is_active=True)
    plans = SubscriptionPlan.objects.filter(is_active=True)
    old_status = subscription.status
    
    if request.method == 'POST':
        hotel_id = request.POST.get('hotel')
        plan_id = request.POST.get('plan')
        
        hotel = get_object_or_404(Hotel, hotel_id=hotel_id)
        plan = get_object_or_404(SubscriptionPlan, plan_id=plan_id)
        
        subscription.hotel = hotel
        subscription.plan = plan
        subscription.billing_cycle = request.POST.get('billing_cycle', 'monthly')
        new_status = request.POST.get('status', 'active')
        subscription.status = new_status
        subscription.auto_renew = request.POST.get('auto_renew') == 'on'
        subscription.save()
        
        # Handle subscription deactivation
        if old_status == 'active' and new_status != 'active':
            create_admin_notification(
                f'Hotel subscription deactivated: {hotel.name} - {plan.name}',
                'warning'
            )
            # Create subscription history
            SubscriptionHistory.objects.create(
                hotel_subscription=subscription,
                action='cancelled' if new_status == 'cancelled' else 'expired',
                action_date=date.today()
            )
            # Send update email
            try:
                send_subscription_update_email(subscription, 'cancelled' if new_status == 'cancelled' else 'updated')
            except:
                pass
        
        # Send update email for other changes
        if old_status == new_status == 'active':
            try:
                send_subscription_update_email(subscription, 'updated')
            except:
                pass
        
        messages.success(request, f'Subscription for "{hotel.name}" updated successfully!')
        return redirect('accounts:hotel_subscription_list')
    
    return render(request, 'accounts/hotel_subscriptions/form.html', {
        'subscription': subscription, 
        'hotels': hotels, 
        'plans': plans
    })

@super_admin_required
def hotel_subscription_delete(request, subscription_id):
    """Delete hotel subscription"""
    subscription = get_object_or_404(HotelSubscription, id=subscription_id)
    hotel_name = subscription.hotel.name
    subscription.delete()
    messages.success(request, f'Subscription for "{hotel_name}" deleted successfully!')
    return redirect('accounts:hotel_subscription_list')

# Analytics Views
@super_admin_required
def analytics_dashboard(request):
    """Advanced Analytics Dashboard"""
    from django.db.models import Count, Sum, Avg
    from datetime import datetime, timedelta
    import json
    
    # Revenue Analytics
    last_12_months = []
    revenue_data = []
    for i in range(12):
        month_date = date.today().replace(day=1) - timedelta(days=30*i)
        month_revenue = Payment.objects.filter(
            payment_date__year=month_date.year,
            payment_date__month=month_date.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        last_12_months.insert(0, month_date.strftime('%b %Y'))
        revenue_data.insert(0, float(month_revenue))
    
    # Hotel Growth
    hotel_growth = []
    for i in range(6):
        month_date = date.today().replace(day=1) - timedelta(days=30*i)
        hotel_count = Hotel.objects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        hotel_growth.insert(0, hotel_count)
    
    # Subscription Distribution
    subscription_stats = SubscriptionPlan.objects.annotate(
        subscription_count=Count('hotelsubscription')
    ).values('name', 'subscription_count')
    
    context = {
        'revenue_labels': json.dumps(last_12_months),
        'revenue_data': json.dumps(revenue_data),
        'hotel_growth_data': json.dumps(hotel_growth),
        'subscription_stats': list(subscription_stats),
        'total_revenue': sum(revenue_data),
        'avg_monthly_revenue': sum(revenue_data) / 12 if revenue_data else 0,
    }
    
    return render(request, 'accounts/analytics/dashboard.html', context)

@super_admin_required
def guests_analytics(request):
    """Guests Analytics Dashboard with Real Hotel Data"""
    try:
        from hotels.models import Room, Service
    except ImportError:
        Room = None
        Service = None
    
    try:
        from staff.models import Staff
    except ImportError:
        Staff = None
    
    try:
        from crm.models import Guest
    except ImportError:
        Guest = None
    
    # Real hotel data
    hotels = Hotel.objects.select_related('owner')
    
    # Room data
    if Room:
        total_rooms = Room.objects.count()
        occupied_rooms = Room.objects.filter(status='Occupied').count()
        available_rooms = Room.objects.filter(status='Available').count()
    else:
        total_rooms = 0
        occupied_rooms = 0
        available_rooms = 0
    
    # Staff data
    if Staff:
        total_staff = Staff.objects.count()
        staff_by_hotel = []  # No hotel relationship in Staff model
    else:
        total_staff = 0
        staff_by_hotel = []
    
    # Guest data
    if Guest:
        try:
            total_guests = Guest.objects.count()
            new_guests_this_month = Guest.objects.filter(
                created_at__month=date.today().month,
                created_at__year=date.today().year
            ).count()
        except:
            total_guests = 0
            new_guests_this_month = 0
    else:
        total_guests = 0
        new_guests_this_month = 0
    
    # Room occupancy by hotel
    hotel_occupancy = []
    for hotel in hotels:
        if Room:
            total_hotel_rooms = hotel.rooms.count() if hasattr(hotel, 'rooms') else 0
            occupied_hotel_rooms = hotel.rooms.filter(status='Occupied').count() if hasattr(hotel, 'rooms') else 0
        else:
            total_hotel_rooms = 0
            occupied_hotel_rooms = 0
        
        occupancy_rate = (occupied_hotel_rooms / total_hotel_rooms * 100) if total_hotel_rooms > 0 else 0
        hotel_occupancy.append({
            'hotel_name': hotel.name,
            'total_rooms': total_hotel_rooms,
            'occupied_rooms': occupied_hotel_rooms,
            'occupancy_rate': round(occupancy_rate, 1),
            'owner': hotel.owner.get_full_name()
        })
    
    context = {
        'hotels': hotels,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'total_staff': total_staff,
        'staff_by_hotel': staff_by_hotel,
        'total_guests': total_guests,
        'new_guests_this_month': new_guests_this_month,
        'hotel_occupancy': hotel_occupancy,
        'occupancy_rate': round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 1)
    }
    return render(request, 'accounts/analytics/guests.html', context)

@super_admin_required
def dining_analytics(request):
    """Dining Analytics Dashboard with Real Hotel Data"""
    try:
        from hotels.models import Service
    except ImportError:
        Service = None
    
    try:
        from maintenance.models import MaintenanceIssue
    except ImportError:
        MaintenanceIssue = None
    
    try:
        from pos.models import MenuItem, Order
    except ImportError:
        MenuItem = None
        Order = None
    
    # Real dining and maintenance data
    hotels = Hotel.objects.all()
    
    # Services data
    if Service:
        total_services = Service.objects.count()
        popular_services = Service.objects.order_by('-price')[:5]
    else:
        total_services = 0
        popular_services = []
    
    # Maintenance data
    if MaintenanceIssue:
        try:
            total_maintenance = MaintenanceIssue.objects.count()
            pending_maintenance = MaintenanceIssue.objects.filter(status__in=['open', 'in_progress']).count()
            completed_maintenance = MaintenanceIssue.objects.filter(status__in=['resolved', 'closed']).count()
            maintenance_by_hotel = MaintenanceIssue.objects.values('property__name').annotate(count=Count('id'))
        except:
            total_maintenance = 0
            pending_maintenance = 0
            completed_maintenance = 0
            maintenance_by_hotel = []
    else:
        total_maintenance = 0
        pending_maintenance = 0
        completed_maintenance = 0
        maintenance_by_hotel = []
    
    # Services by hotel
    services_by_hotel = []
    for hotel in hotels:
        if Service and hasattr(hotel, 'services'):
            hotel_services = hotel.services.all()
            total_service_revenue = sum(service.price for service in hotel_services)
            services_by_hotel.append({
                'hotel_name': hotel.name,
                'services_count': hotel_services.count(),
                'total_revenue': total_service_revenue,
                'services': hotel_services[:5]  # Top 5 services
            })
        else:
            services_by_hotel.append({
                'hotel_name': hotel.name,
                'services_count': 0,
                'total_revenue': 0,
                'services': []
            })
    
    context = {
        'hotels': hotels,
        'total_services': total_services,
        'services_by_hotel': services_by_hotel,
        'popular_services': popular_services,
        'total_maintenance': total_maintenance,
        'pending_maintenance': pending_maintenance,
        'completed_maintenance': completed_maintenance,
        'maintenance_by_hotel': maintenance_by_hotel,
        'maintenance_completion_rate': round((completed_maintenance / total_maintenance * 100) if total_maintenance > 0 else 0, 1)
    }
    return render(request, 'accounts/analytics/dining.html', context)