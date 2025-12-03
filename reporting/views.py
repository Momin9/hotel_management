from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from hotels.models import Room
from reservations.models import Reservation
from billing.models import Invoice
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import os
from django.conf import settings
from accounts.pdf_utils import AuraStayDocTemplate

@login_required
def dashboard(request):
    """Reports dashboard with real data"""
    from django.utils import timezone
    from django.db.models import Avg
    from crm.models import GuestProfile
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Calculate real metrics
    # Occupancy rate
    total_rooms = Room.objects.count()
    occupied_rooms = 0
    if total_rooms > 0:
        from reservations.models import Stay, Reservation
        from django.db.models import Q
        
        for room in Room.objects.all():
            current_stay = room.stays.filter(
                Q(actual_check_in__date__lte=today) &
                (Q(actual_check_out__isnull=True) | Q(actual_check_out__date__gte=today))
            ).first()
            
            if current_stay or Reservation.objects.filter(
                room=room,
                check_in__lte=today,
                check_out__gt=today,
                status__in=['confirmed', 'checked_in']
            ).exists():
                occupied_rooms += 1
    
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Monthly revenue
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=month_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Total guests
    total_guests = GuestProfile.objects.count()
    
    # Average rating (placeholder - you can implement actual rating system)
    avg_rating = 4.2
    
    context = {
        'occupancy_rate': round(occupancy_rate, 1),
        'monthly_revenue': monthly_revenue,
        'total_guests': total_guests,
        'avg_rating': avg_rating,
    }
    
    return render(request, 'reporting/dashboard.html', context)

@login_required
def performance_report(request):
    """Performance dashboard with operational metrics"""
    from django.utils import timezone
    from django.db.models import Avg, Count
    from crm.models import GuestProfile
    from reservations.models import Stay, Reservation
    from staff.models import Staff
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    # Operational Efficiency Metrics
    total_rooms = Room.objects.count()
    
    # Check-in/Check-out efficiency
    checkins_today = Stay.objects.filter(actual_check_in__date=today).count()
    checkouts_today = Stay.objects.filter(actual_check_out__date=today).count()
    
    # Staff performance
    total_staff = Staff.objects.filter(is_active=True).count()
    
    # Guest satisfaction metrics
    total_reservations = Reservation.objects.count()
    completed_stays = Stay.objects.filter(actual_check_out__isnull=False).count()
    
    # Revenue per available room (RevPAR)
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=month_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    days_in_month = (today - month_start).days + 1
    revpar = (monthly_revenue / (total_rooms * days_in_month)) if total_rooms > 0 else 0
    
    # Average daily rate (ADR)
    paid_invoices_count = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=month_start
    ).count()
    adr = (monthly_revenue / paid_invoices_count) if paid_invoices_count > 0 else 0
    
    # Occupancy rate
    occupied_rooms = 0
    if total_rooms > 0:
        from django.db.models import Q
        
        for room in Room.objects.all():
            current_stay = room.stays.filter(
                Q(actual_check_in__date__lte=today) &
                (Q(actual_check_out__isnull=True) | Q(actual_check_out__date__gte=today))
            ).first()
            
            if current_stay or Reservation.objects.filter(
                room=room,
                check_in__lte=today,
                check_out__gt=today,
                status__in=['confirmed', 'checked_in']
            ).exists():
                occupied_rooms += 1
    
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Guest retention rate
    repeat_guests = Reservation.objects.values('guest').annotate(
        reservation_count=Count('id')
    ).filter(reservation_count__gt=1).count()
    
    retention_rate = (repeat_guests / total_reservations * 100) if total_reservations > 0 else 0
    
    # Recent performance data
    recent_checkins = Stay.objects.filter(
        actual_check_in__date__gte=week_start
    ).select_related('reservation__guest', 'reservation__room').order_by('-actual_check_in')[:10]
    
    recent_checkouts = Stay.objects.filter(
        actual_check_out__date__gte=week_start
    ).select_related('reservation__guest', 'reservation__room').order_by('-actual_check_out')[:10]
    
    context = {
        'occupancy_rate': round(occupancy_rate, 1),
        'revpar': round(revpar, 2),
        'adr': round(adr, 2),
        'retention_rate': round(retention_rate, 1),
        'checkins_today': checkins_today,
        'checkouts_today': checkouts_today,
        'total_staff': total_staff,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': total_rooms - occupied_rooms,
        'monthly_revenue': monthly_revenue,
        'completed_stays': completed_stays,
        'recent_checkins': recent_checkins,
        'recent_checkouts': recent_checkouts,
    }
    
    return render(request, 'reporting/performance.html', context)

@login_required
def occupancy_report(request):
    """Occupancy report"""
    from reservations.models import Stay, Reservation
    from django.utils import timezone
    from django.db.models import Q
    
    # Get rooms with related data
    rooms = Room.objects.select_related('room_type').prefetch_related(
        'stays__reservation__guest'
    ).all()
    
    today = timezone.now().date()
    
    # Add current reservation and guest info to each room
    occupied_count = 0
    available_count = 0
    
    for room in rooms:
        # Check for current stay (checked in and not checked out)
        current_stay = room.stays.filter(
            Q(actual_check_in__date__lte=today) &
            (Q(actual_check_out__isnull=True) | Q(actual_check_out__date__gte=today))
        ).first()
        
        if current_stay:
            room.current_reservation = current_stay
            room.current_guest = current_stay.reservation.guest
            room.is_occupied = True
            occupied_count += 1
        else:
            # Check for confirmed reservation for today
            current_reservation = Reservation.objects.filter(
                room=room,
                check_in__lte=today,
                check_out__gt=today,
                status__in=['confirmed', 'checked_in']
            ).first()
            
            if current_reservation:
                room.current_reservation = current_reservation
                room.current_guest = current_reservation.guest
                room.is_occupied = True
                occupied_count += 1
            else:
                room.current_reservation = None
                room.current_guest = None
                room.is_occupied = False
                available_count += 1
    
    total_rooms = rooms.count()
    occupancy_rate = (occupied_count / total_rooms * 100) if total_rooms > 0 else 0
    
    context = {
        'rooms': rooms,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_count,
        'available_rooms': available_count,
        'occupancy_rate': round(occupancy_rate, 1),
    }
    
    return render(request, 'reporting/occupancy.html', context)

@login_required
def revenue_report(request):
    """Revenue report"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    # Revenue calculations
    total_revenue = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=month_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    weekly_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=week_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    daily_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date=today
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Invoice statistics
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(status='paid').count()
    pending_invoices = Invoice.objects.filter(status__in=['draft', 'sent']).count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    
    # Recent paid invoices
    recent_invoices = Invoice.objects.filter(status='paid').select_related(
        'guest', 'stay__reservation__room'
    ).order_by('-paid_date')[:10]
    
    # Average revenue per booking
    avg_revenue = total_revenue / paid_invoices if paid_invoices > 0 else 0
    
    context = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'weekly_revenue': weekly_revenue,
        'daily_revenue': daily_revenue,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
        'recent_invoices': recent_invoices,
        'avg_revenue': avg_revenue,
    }
    
    return render(request, 'reporting/revenue.html', context)

@login_required
def guest_report(request):
    """Guest report"""
    from crm.models import GuestProfile
    from django.utils import timezone
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Guest statistics
    total_guests = GuestProfile.objects.count()
    new_guests_this_month = GuestProfile.objects.filter(created_at__date__gte=month_start).count()
    
    # Reservation statistics
    total_reservations = Reservation.objects.count()
    repeat_guests = Reservation.objects.values('guest').annotate(
        reservation_count=Count('id')
    ).filter(reservation_count__gt=1).count()
    
    # Current guests (checked in)
    current_guests = Reservation.objects.filter(status='checked_in').count()
    
    # Guest types
    corporate_guests = GuestProfile.objects.filter(guest_type='corporate').count()
    individual_guests = GuestProfile.objects.filter(guest_type='individual').count()
    
    # Recent guests
    recent_guests = GuestProfile.objects.select_related().order_by('-created_at')[:10]
    
    # Top guests by reservations
    top_guests = Reservation.objects.values('guest__first_name', 'guest__last_name', 'guest__email').annotate(
        reservation_count=Count('id'),
        total_spent=Sum('rate')
    ).order_by('-reservation_count')[:10]
    
    # Guest satisfaction (if you have ratings)
    avg_satisfaction = 4.2  # Placeholder - you can calculate from actual ratings
    
    context = {
        'total_guests': total_guests,
        'new_guests_this_month': new_guests_this_month,
        'total_reservations': total_reservations,
        'repeat_guests': repeat_guests,
        'current_guests': current_guests,
        'corporate_guests': corporate_guests,
        'individual_guests': individual_guests,
        'recent_guests': recent_guests,
        'top_guests': top_guests,
        'avg_satisfaction': avg_satisfaction,
    }
    
    return render(request, 'reporting/guests.html', context)

@login_required
def export_revenue_pdf(request):
    """Export revenue report as PDF"""
    # Get hotel name
    hotel = request.user.assigned_hotel
    hotel_name = hotel.name if hotel else "Hotel"
    
    # Get the same data as revenue report
    today = datetime.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    # Revenue calculations
    total_revenue = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=month_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    weekly_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=week_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    daily_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date=today
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Invoice statistics
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(status='paid').count()
    pending_invoices = Invoice.objects.filter(status__in=['draft', 'sent']).count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    
    # Recent paid invoices
    recent_invoices = Invoice.objects.filter(status='paid').select_related(
        'guest', 'stay__reservation__room'
    ).order_by('-paid_date')[:10]
    
    # Average revenue per booking
    avg_revenue = total_revenue / paid_invoices if paid_invoices > 0 else 0
    
    # Create PDF using AuraStay template
    buffer = BytesIO()
    doc = AuraStayDocTemplate(buffer, pagesize=A4)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles matching invoice PDF
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold'
    )
    
    # Add space from header
    elements.append(Spacer(1, 10))
    
    # Title
    elements.append(Paragraph(f"{hotel_name} Revenue Report", title_style))
    elements.append(Spacer(1, 15))
    
    # Revenue Summary
    elements.append(Paragraph("Revenue Summary", heading_style))
    
    revenue_data = [
        ['Period', 'Amount'],
        ['Total Revenue', f'${total_revenue:,.2f}'],
        ['This Month', f'${monthly_revenue:,.2f}'],
        ['This Week', f'${weekly_revenue:,.2f}'],
        ['Today', f'${daily_revenue:,.2f}'],
        ['Average per Booking', f'${avg_revenue:,.2f}']
    ]
    
    revenue_table = Table(revenue_data, colWidths=[3*inch, 2*inch])
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5)
    ]))
    
    elements.append(revenue_table)
    elements.append(Spacer(1, 20))
    
    # Invoice Statistics
    elements.append(Paragraph("Invoice Statistics", heading_style))
    
    invoice_data = [
        ['Metric', 'Count'],
        ['Total Invoices', str(total_invoices)],
        ['Paid Invoices', str(paid_invoices)],
        ['Pending Invoices', str(pending_invoices)],
        ['Overdue Invoices', str(overdue_invoices)]
    ]
    
    invoice_table = Table(invoice_data, colWidths=[3*inch, 2*inch])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Recent Paid Invoices
    if recent_invoices:
        elements.append(Paragraph("Recent Paid Invoices", heading_style))
        
        invoice_list_data = [['Invoice #', 'Guest', 'Room', 'Amount', 'Paid Date']]
        
        for invoice in recent_invoices:
            invoice_list_data.append([
                invoice.invoice_number,
                f"{invoice.guest.first_name} {invoice.guest.last_name}",
                f"Room {invoice.stay.reservation.room.room_number}",
                f"${invoice.total_amount:,.2f}",
                invoice.paid_date.strftime('%m/%d/%Y') if invoice.paid_date else 'N/A'
            ])
        
        invoice_list_table = Table(invoice_list_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        invoice_list_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        elements.append(invoice_list_table)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="revenue_report_{today.strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response

@login_required
def export_guest_pdf(request):
    """Export guest report as PDF"""
    from crm.models import GuestProfile
    from django.utils import timezone
    
    # Get hotel name
    hotel = request.user.assigned_hotel
    hotel_name = hotel.name if hotel else "Hotel"
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Guest statistics
    total_guests = GuestProfile.objects.count()
    new_guests_this_month = GuestProfile.objects.filter(created_at__date__gte=month_start).count()
    total_reservations = Reservation.objects.count()
    repeat_guests = Reservation.objects.values('guest').annotate(
        reservation_count=Count('id')
    ).filter(reservation_count__gt=1).count()
    current_guests = Reservation.objects.filter(status='checked_in').count()
    corporate_guests = GuestProfile.objects.filter(guest_type='corporate').count()
    individual_guests = GuestProfile.objects.filter(guest_type='individual').count()
    
    # Top guests
    top_guests = Reservation.objects.values('guest__first_name', 'guest__last_name', 'guest__email').annotate(
        reservation_count=Count('id'),
        total_spent=Sum('rate')
    ).order_by('-reservation_count')[:10]
    
    # Create PDF using AuraStay template
    buffer = BytesIO()
    doc = AuraStayDocTemplate(buffer, pagesize=A4)
    
    elements = []
    
    # Define styles matching invoice PDF
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold'
    )
    
    # Add space from header
    elements.append(Spacer(1, 10))
    
    # Title
    elements.append(Paragraph(f"{hotel_name} Guest Analytics Report", title_style))
    elements.append(Spacer(1, 15))
    
    # Guest Statistics
    elements.append(Paragraph("Guest Statistics", heading_style))
    
    guest_data = [
        ['Metric', 'Count'],
        ['Total Guests', str(total_guests)],
        ['New Guests This Month', str(new_guests_this_month)],
        ['Repeat Guests', str(repeat_guests)],
        ['Currently Staying', str(current_guests)],
        ['Corporate Guests', str(corporate_guests)],
        ['Individual Guests', str(individual_guests)],
        ['Total Reservations', str(total_reservations)]
    ]
    
    guest_table = Table(guest_data, colWidths=[3*inch, 2*inch])
    guest_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    
    elements.append(guest_table)
    elements.append(Spacer(1, 20))
    
    # Top Guests
    if top_guests:
        elements.append(Paragraph("Top Guests by Reservations", heading_style))
        
        top_guest_data = [['Guest Name', 'Email', 'Reservations', 'Total Spent']]
        
        for guest in top_guests:
            top_guest_data.append([
                f"{guest['guest__first_name']} {guest['guest__last_name']}",
                guest['guest__email'],
                str(guest['reservation_count']),
                f"${guest['total_spent']:,.2f}" if guest['total_spent'] else "$0.00"
            ])
        
        top_guest_table = Table(top_guest_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.2*inch])
        top_guest_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        elements.append(top_guest_table)
    
    # Build PDF
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="guest_report_{today.strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response

@login_required
def export_occupancy_pdf(request):
    """Export occupancy report as PDF"""
    from reservations.models import Stay, Reservation
    from django.utils import timezone
    from django.db.models import Q
    
    # Get hotel name
    hotel = request.user.assigned_hotel
    hotel_name = hotel.name if hotel else "Hotel"
    
    today = timezone.now().date()
    
    # Get rooms with occupancy data
    rooms = Room.objects.select_related('room_type').prefetch_related(
        'stays__reservation__guest'
    ).all()
    
    occupied_count = 0
    available_count = 0
    room_data = []
    
    for room in rooms:
        # Check for current stay
        current_stay = room.stays.filter(
            Q(actual_check_in__date__lte=today) &
            (Q(actual_check_out__isnull=True) | Q(actual_check_out__date__gte=today))
        ).first()
        
        if current_stay:
            occupied_count += 1
            status = "Occupied"
            guest_name = f"{current_stay.reservation.guest.first_name} {current_stay.reservation.guest.last_name}"
            check_in = current_stay.actual_check_in.strftime('%m/%d/%Y') if current_stay.actual_check_in else 'N/A'
            check_out = current_stay.actual_check_out.strftime('%m/%d/%Y') if current_stay.actual_check_out else 'In Progress'
        else:
            # Check for confirmed reservation
            current_reservation = Reservation.objects.filter(
                room=room,
                check_in__lte=today,
                check_out__gt=today,
                status__in=['confirmed', 'checked_in']
            ).first()
            
            if current_reservation:
                occupied_count += 1
                status = "Reserved"
                guest_name = f"{current_reservation.guest.first_name} {current_reservation.guest.last_name}"
                check_in = current_reservation.check_in.strftime('%m/%d/%Y')
                check_out = current_reservation.check_out.strftime('%m/%d/%Y')
            else:
                available_count += 1
                status = "Available"
                guest_name = "-"
                check_in = "-"
                check_out = "-"
        
        room_data.append([
            room.room_number,
            room.room_type.name if room.room_type else 'N/A',
            status,
            guest_name,
            check_in,
            check_out,
            f"${room.price:,.0f}" if room.price else "$0"
        ])
    
    total_rooms = rooms.count()
    occupancy_rate = (occupied_count / total_rooms * 100) if total_rooms > 0 else 0
    
    # Create PDF using AuraStay template
    buffer = BytesIO()
    doc = AuraStayDocTemplate(buffer, pagesize=A4)
    
    elements = []
    
    # Define styles matching invoice PDF
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold'
    )
    
    # Add space from header
    elements.append(Spacer(1, 10))
    
    # Title
    elements.append(Paragraph(f"{hotel_name} Occupancy Report", title_style))
    elements.append(Spacer(1, 15))
    
    # Occupancy Summary
    elements.append(Paragraph("Occupancy Summary", heading_style))
    
    occupancy_summary = [
        ['Metric', 'Value'],
        ['Total Rooms', str(total_rooms)],
        ['Occupied Rooms', str(occupied_count)],
        ['Available Rooms', str(available_count)],
        ['Occupancy Rate', f"{occupancy_rate:.1f}%"]
    ]
    
    summary_table = Table(occupancy_summary, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Room Details
    elements.append(Paragraph("Room Details", heading_style))
    
    room_headers = ['Room', 'Type', 'Status', 'Guest', 'Check-in', 'Check-out', 'Rate']
    room_table_data = [room_headers] + room_data
    
    room_table = Table(room_table_data, colWidths=[0.8*inch, 1*inch, 0.8*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    room_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (6, 0), (6, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    
    elements.append(room_table)
    
    # Build PDF
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="occupancy_report_{today.strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response
@login_required
def export_performance_pdf(request):
    """Export performance report as PDF"""
    from django.utils import timezone
    from django.db.models import Count
    from crm.models import GuestProfile
    from reservations.models import Stay, Reservation
    from staff.models import Staff
    
    # Get hotel name
    hotel = request.user.assigned_hotel
    hotel_name = hotel.name if hotel else "Hotel"
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Get performance metrics
    total_rooms = Room.objects.count()
    checkins_today = Stay.objects.filter(actual_check_in__date=today).count()
    checkouts_today = Stay.objects.filter(actual_check_out__date=today).count()
    total_staff = Staff.objects.filter(is_active=True).count()
    
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=month_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    days_in_month = (today - month_start).days + 1
    revpar = (monthly_revenue / (total_rooms * days_in_month)) if total_rooms > 0 else 0
    
    paid_invoices_count = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=month_start
    ).count()
    adr = (monthly_revenue / paid_invoices_count) if paid_invoices_count > 0 else 0
    
    # Occupancy calculation
    occupied_rooms = 0
    if total_rooms > 0:
        from django.db.models import Q
        
        for room in Room.objects.all():
            current_stay = room.stays.filter(
                Q(actual_check_in__date__lte=today) &
                (Q(actual_check_out__isnull=True) | Q(actual_check_out__date__gte=today))
            ).first()
            
            if current_stay or Reservation.objects.filter(
                room=room,
                check_in__lte=today,
                check_out__gt=today,
                status__in=['confirmed', 'checked_in']
            ).exists():
                occupied_rooms += 1
    
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    total_reservations = Reservation.objects.count()
    repeat_guests = Reservation.objects.values('guest').annotate(
        reservation_count=Count('id')
    ).filter(reservation_count__gt=1).count()
    retention_rate = (repeat_guests / total_reservations * 100) if total_reservations > 0 else 0
    
    # Create PDF using AuraStay template
    buffer = BytesIO()
    doc = AuraStayDocTemplate(buffer, pagesize=A4)
    
    elements = []
    
    # Define styles matching invoice PDF
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold'
    )
    
    # Add space from header
    elements.append(Spacer(1, 10))
    
    # Title
    elements.append(Paragraph(f"{hotel_name} Performance Dashboard", title_style))
    elements.append(Spacer(1, 15))
    
    # Key Performance Indicators
    elements.append(Paragraph("Key Performance Indicators", heading_style))
    
    kpi_data = [
        ['Metric', 'Value'],
        ['Occupancy Rate', f'{occupancy_rate:.1f}%'],
        ['Revenue per Available Room (RevPAR)', f'${revpar:.2f}'],
        ['Average Daily Rate (ADR)', f'${adr:.2f}'],
        ['Guest Retention Rate', f'{retention_rate:.1f}%'],
        ['Check-ins Today', str(checkins_today)],
        ['Check-outs Today', str(checkouts_today)]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[3*inch, 2*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5)
    ]))
    
    elements.append(kpi_table)
    elements.append(Spacer(1, 20))
    
    # Operational Summary
    elements.append(Paragraph("Operational Summary", heading_style))
    
    ops_data = [
        ['Resource', 'Count/Status'],
        ['Total Rooms', str(total_rooms)],
        ['Occupied Rooms', str(occupied_rooms)],
        ['Available Rooms', str(total_rooms - occupied_rooms)],
        ['Active Staff', str(total_staff)],
        ['Monthly Revenue', f'${monthly_revenue:,.2f}']
    ]
    
    ops_table = Table(ops_data, colWidths=[3*inch, 2*inch])
    ops_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    
    elements.append(ops_table)
    
    # Build PDF
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="performance_report_{today.strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response