from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from .models import Invoice, Payment
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from decimal import Decimal
import io
import os

@login_required
def dashboard(request):
    """Billing dashboard"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_payments = Invoice.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_invoices = Invoice.objects.count()
    monthly_revenue = Payment.objects.filter(
        status='completed',
        timestamp__date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_invoices = Invoice.objects.order_by('-created_at')[:5]
    
    context = {
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'total_invoices': total_invoices,
        'monthly_revenue': monthly_revenue,
        'recent_invoices': recent_invoices,
    }
    
    return render(request, 'billing/dashboard.html', context)

@login_required
def invoice_list(request):
    """List all invoices"""
    invoices = Invoice.objects.all().order_by('-created_at')
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})

@login_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.all().order_by('-timestamp')
    
    # Calculate statistics
    total_received = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_amount = Payment.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
    failed_amount = Payment.objects.filter(status='failed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'payments': payments,
        'total_received': total_received,
        'pending_amount': pending_amount,
        'failed_amount': failed_amount,
    }
    
    return render(request, 'billing/payment_list.html', context)

@login_required
def invoice_detail(request, invoice_id):
    """Invoice detail view"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})

@login_required
def mark_invoice_paid(request, invoice_id):
    """Mark invoice as paid"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        if invoice.status != 'paid':
            # Create payment record
            Payment.objects.create(
                invoice=invoice,
                amount=invoice.total_amount,
                method=request.POST.get('payment_method', 'cash'),
                status='completed'
            )
            
            # Update invoice status
            invoice.status = 'paid'
            invoice.paid_date = timezone.now().date()
            invoice.save()
            
            messages.success(request, f'Invoice #{invoice.invoice_number} marked as paid successfully!')
        else:
            messages.warning(request, 'Invoice is already marked as paid.')
        
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    return render(request, 'billing/mark_paid.html', {'invoice': invoice})

class InvoiceDocTemplate(BaseDocTemplate):
    """Custom document template with header and footer"""
    
    def __init__(self, filename, invoice, **kwargs):
        self.invoice = invoice
        BaseDocTemplate.__init__(self, filename, **kwargs)
        
        # Define frame for content - optimized for single page
        frame = Frame(
            20*mm, 20*mm, 170*mm, 247*mm,
            leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0
        )
        
        # Create page template
        template = PageTemplate(id='invoice', frames=frame, onPage=self.add_page_decorations)
        self.addPageTemplates([template])
    
    def add_page_decorations(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Watermark
        canvas.setFillColor(colors.HexColor('#f0f0f0'))  # Very light gray
        canvas.setFont('Helvetica-Bold', 60)
        canvas.rotate(45)
        watermark_text = f"{self.invoice.stay.reservation.hotel.name} - AuraStay"
        canvas.drawString(200, 100, watermark_text)
        canvas.rotate(-45)
        
        # Header
        canvas.setFillColor(colors.HexColor('#1e3a8a'))  # Dark blue
        canvas.rect(0, A4[1] - 80, A4[0], 80, fill=1)
        
        # Hotel name in header
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawString(30, A4[1] - 45, self.invoice.stay.reservation.hotel.name)
        
        # Invoice title and status
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawRightString(A4[0] - 30, A4[1] - 50, f'INVOICE #{self.invoice.invoice_number}')
        
        # Status with color coding
        status_color = colors.green if self.invoice.status == 'paid' else colors.red if self.invoice.status == 'overdue' else colors.orange
        canvas.setFillColor(status_color)
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawRightString(A4[0] - 30, A4[1] - 25, f'STATUS: {self.invoice.status.upper()}')
        
        # Footer
        canvas.setFillColor(colors.HexColor('#f3f4f6'))  # Light gray
        canvas.rect(0, 0, A4[0], 50, fill=1)
        
        # Footer content
        canvas.setFillColor(colors.HexColor('#374151'))  # Dark gray
        canvas.setFont('Helvetica', 10)
        canvas.drawString(30, 25, f'{self.invoice.stay.reservation.hotel.name} | {self.invoice.stay.reservation.hotel.address}')
        canvas.drawString(30, 15, f'Phone: {self.invoice.stay.reservation.hotel.phone} | Email: {self.invoice.stay.reservation.hotel.email}')
        
        # Page number
        canvas.drawRightString(A4[0] - 30, 20, f'Page {doc.page}')
        
        canvas.restoreState()

@login_required
def download_invoice_pdf(request, invoice_id):
    """Download invoice as PDF"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Create custom document - reduced margins for single page
    doc = InvoiceDocTemplate(buffer, invoice, pagesize=A4, topMargin=80, bottomMargin=50)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=15,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=TA_CENTER
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
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=3,
        textColor=colors.HexColor('#374151')
    )
    
    # Add minimal space after header
    elements.append(Spacer(1, 10))
    
    # Bill To and Ship To section
    elements.append(Paragraph('BILLING INFORMATION', heading_style))
    
    # Create info table with better styling
    hotel_info = f"""
    <b style="color: #1e3a8a;">FROM:</b><br/>
    <b>{invoice.stay.reservation.hotel.name}</b><br/>
    {invoice.stay.reservation.hotel.address}<br/>
    {invoice.stay.reservation.hotel.city}, {invoice.stay.reservation.hotel.country}<br/>
    <b>Phone:</b> {invoice.stay.reservation.hotel.phone}<br/>
    <b>Email:</b> {invoice.stay.reservation.hotel.email}
    """
    
    guest_info = f"""
    <b style="color: #1e3a8a;">BILL TO:</b><br/>
    <b>{invoice.guest.full_name}</b><br/>
    <b>Email:</b> {invoice.guest.email}<br/>
    <b>Phone:</b> {invoice.guest.phone}<br/>
    <b>Check-in:</b> {invoice.stay.actual_check_in.strftime('%B %d, %Y')}<br/>
    <b>Check-out:</b> {invoice.stay.actual_check_out.strftime('%B %d, %Y') if invoice.stay.actual_check_out else 'Still checked in'}
    """
    
    info_data = [
        [Paragraph(hotel_info, normal_style), Paragraph(guest_info, normal_style)]
    ]
    
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # Invoice details in a nice box
    invoice_details_data = [
        ['Invoice Date:', invoice.created_at.strftime('%B %d, %Y'), 'Due Date:', invoice.due_date.strftime('%B %d, %Y')],
        ['Status:', f'{invoice.status.upper()}', 'Currency:', invoice.currency]
    ]
    
    details_table = Table(invoice_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#3b82f6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#93c5fd')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(details_table)
    elements.append(Spacer(1, 15))
    
    # Items section
    elements.append(Paragraph('INVOICE DETAILS', heading_style))
    
    # Charge items table with better styling
    charge_data = [['Description', 'Qty', 'Unit Price', 'Amount']]
    
    for item in invoice.charge_items.all():
        charge_data.append([
            item.description,
            str(item.quantity),
            f"{invoice.currency} {item.unit_price:.2f}",
            f"{invoice.currency} {item.amount:.2f}"
        ])
    
    # Add empty row for spacing
    charge_data.append(['', '', '', ''])
    
    # Add totals with better formatting
    charge_data.extend([
        ['', '', 'Subtotal:', f"{invoice.currency} {invoice.subtotal:.2f}"],
        ['', '', f'Service Charge ({((invoice.service_charge/invoice.subtotal)*100):.1f}%):', f"{invoice.currency} {invoice.service_charge:.2f}"] if invoice.service_charge > 0 else ['', '', 'Service Charge:', f"{invoice.currency} 0.00"],
        ['', '', f'Tax ({invoice.tax_rate:.1f}%):', f"{invoice.currency} {invoice.tax_amount:.2f}"] if invoice.tax_rate > 0 else ['', '', 'Tax:', f"{invoice.currency} 0.00"],
        ['', '', 'TOTAL:', f"{invoice.currency} {invoice.total_amount:.2f}"]
    ])
    
    charge_table = Table(charge_data, colWidths=[3.5*inch, 0.8*inch, 1.3*inch, 1.4*inch])
    charge_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Description left aligned
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -5), colors.white),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        
        # Totals section
        ('FONTNAME', (2, -4), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (2, -4), (-1, -2), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (2, -1), (-1, -1), colors.white),
        ('FONTSIZE', (2, -1), (-1, -1), 12),
        
        # Grid
        ('GRID', (0, 0), (-1, -5), 1, colors.HexColor('#e5e7eb')),
        ('GRID', (2, -4), (-1, -1), 1, colors.HexColor('#9ca3af')),
        
        # Alignment for totals
        ('ALIGN', (2, -4), (-1, -1), 'RIGHT'),
        ('ALIGN', (3, -4), (-1, -1), 'RIGHT'),
    ]))
    
    elements.append(charge_table)
    elements.append(Spacer(1, 15))
    
    # Payment status with enhanced styling
    if invoice.status == 'paid':
        status_text = f"<b style='color: #059669; font-size: 14px;'>✓ PAYMENT STATUS: PAID</b><br/>Payment received on {invoice.paid_date.strftime('%B %d, %Y') if invoice.paid_date else 'N/A'}"
    elif invoice.status == 'overdue':
        status_text = f"<b style='color: #dc2626; font-size: 14px;'>⚠ PAYMENT STATUS: OVERDUE</b><br/>Payment was due on {invoice.due_date.strftime('%B %d, %Y')}"
    else:
        status_text = f"<b style='color: #f59e0b; font-size: 14px;'>⏳ PAYMENT STATUS: {invoice.status.upper()}</b><br/>Payment due by {invoice.due_date.strftime('%B %d, %Y')}"
    
    elements.append(Paragraph(status_text, normal_style))
    elements.append(Spacer(1, 10))
    
    # Thank you note
    thank_you = Paragraph(
        "<b>Thank you for choosing our hotel!</b><br/>We appreciate your business and look forward to serving you again.",
        ParagraphStyle(
            'ThankYou',
            parent=normal_style,
            alignment=TA_CENTER,
            fontSize=12,
            textColor=colors.HexColor('#1e3a8a'),
            spaceBefore=10
        )
    )
    elements.append(thank_you)
    
    # Add invoice date at bottom right
    elements.append(Spacer(1, 15))
    invoice_date = Paragraph(
        f"Date: {invoice.created_at.strftime('%B %d, %Y')}",
        ParagraphStyle(
            'InvoiceDate',
            parent=normal_style,
            alignment=TA_RIGHT,
            fontSize=10,
            textColor=colors.HexColor('#374151')
        )
    )
    elements.append(invoice_date)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    response.write(pdf)
    
    return response

@login_required
def checkout_guest(request, stay_id):
    """Checkout guest and create invoice"""
    from reservations.models import Stay
    from .models import TaxConfiguration, ChargeItem
    from datetime import date, timedelta
    import random
    
    stay = get_object_or_404(Stay, id=stay_id)
    
    if request.method == 'POST':
        # Check if invoice already exists
        existing_invoice = Invoice.objects.filter(stay=stay).first()
        if existing_invoice:
            messages.info(request, f'Invoice {existing_invoice.invoice_number} already exists for this stay.')
            return redirect('billing:invoice_detail', invoice_id=existing_invoice.id)
        
        # Get form data
        apply_tax = request.POST.get('apply_tax') == 'on'
        tax_rate = request.POST.get('tax_rate', '0')
        apply_service_charge = request.POST.get('apply_service_charge') == 'on'
        service_charge_rate = request.POST.get('service_charge_rate', '5')
        
        # Create invoice
        invoice_number = f"INV-{random.randint(100000, 999999)}"
        invoice = Invoice.objects.create(
            stay=stay,
            guest=stay.reservation.guest,
            invoice_number=invoice_number,
            due_date=date.today() + timedelta(days=30),
            tax_rate=Decimal(tax_rate) if apply_tax else Decimal('0'),
            currency='USD',
            status='pending'
        )
        
        # Add room charges
        nights = (stay.actual_check_out.date() - stay.actual_check_in.date()).days if stay.actual_check_out else 1
        room_rate = stay.reservation.rate
        
        ChargeItem.objects.create(
            invoice=invoice,
            description=f"Room {stay.room.room_number} - {nights} night(s)",
            charge_type='room',
            quantity=nights,
            unit_price=room_rate,
            amount=room_rate * int(nights)
        )
        
        # Add reservation expenses
        from reservations.models import ReservationExpense
        expenses = ReservationExpense.objects.filter(
            reservation=stay.reservation,
            deleted_at__isnull=True
        )
        
        for expense in expenses:
            ChargeItem.objects.create(
                invoice=invoice,
                description=expense.description,
                charge_type=expense.expense_type,
                quantity=expense.quantity,
                unit_price=expense.unit_price,
                amount=expense.total_amount
            )
        
        # Calculate service charge if enabled
        if apply_service_charge:
            invoice.service_charge = Decimal(service_charge_rate) / 100
        else:
            invoice.service_charge = Decimal('0')
        
        # Save service charge rate, then calculate totals
        invoice.save()
        invoice.calculate_totals()
        
        # Update stay checkout
        if not stay.actual_check_out:
            stay.actual_check_out = timezone.now()
            stay.save()
        
        # Update reservation status
        stay.reservation.status = 'checked_out'
        stay.reservation.save()
        
        messages.success(request, f'Guest checked out successfully! Invoice {invoice_number} created.')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    # Get available tax configurations
    tax_configs = TaxConfiguration.objects.filter(is_active=True)
    
    context = {
        'stay': stay,
        'tax_configs': tax_configs
    }
    
    return render(request, 'billing/checkout.html', context)

@login_required
def payment_detail(request, payment_id):
    """Payment detail view"""
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'billing/payment_detail.html', {'payment': payment})

class ReceiptDocTemplate(BaseDocTemplate):
    """Custom document template for payment receipts"""
    
    def __init__(self, filename, payment, **kwargs):
        self.payment = payment
        BaseDocTemplate.__init__(self, filename, **kwargs)
        
        # Define frame for content
        frame = Frame(
            20*mm, 20*mm, 170*mm, 247*mm,
            leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0
        )
        
        # Create page template
        template = PageTemplate(id='receipt', frames=frame, onPage=self.add_page_decorations)
        self.addPageTemplates([template])
    
    def add_page_decorations(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Get hotel info
        hotel = self.payment.invoice.stay.reservation.hotel if self.payment.invoice else None
        
        # Watermark
        canvas.setFillColor(colors.HexColor('#f0f0f0'))
        canvas.setFont('Helvetica-Bold', 60)
        canvas.rotate(45)
        watermark_text = f"{hotel.name if hotel else 'Hotel'} - AuraStay"
        canvas.drawString(200, 100, watermark_text)
        canvas.rotate(-45)
        
        # Header
        canvas.setFillColor(colors.HexColor('#1e3a8a'))
        canvas.rect(0, A4[1] - 80, A4[0], 80, fill=1)
        
        # Hotel name in header
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 24)
        canvas.drawString(30, A4[1] - 45, hotel.name if hotel else 'Hotel Receipt')
        
        # Receipt title and status
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawRightString(A4[0] - 30, A4[1] - 50, f'PAYMENT RECEIPT #{str(self.payment.id)[:8].upper()}')
        
        # Status with color coding
        status_color = colors.green if self.payment.status == 'completed' else colors.red if self.payment.status == 'failed' else colors.orange
        canvas.setFillColor(status_color)
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawRightString(A4[0] - 30, A4[1] - 25, f'STATUS: {self.payment.status.upper()}')
        
        # Footer
        canvas.setFillColor(colors.HexColor('#f3f4f6'))
        canvas.rect(0, 0, A4[0], 50, fill=1)
        
        # Footer content
        canvas.setFillColor(colors.HexColor('#374151'))
        canvas.setFont('Helvetica', 10)
        if hotel:
            canvas.drawString(30, 25, f'{hotel.name} | {hotel.address}')
            canvas.drawString(30, 15, f'Phone: {hotel.phone} | Email: {hotel.email}')
        
        # Page number
        canvas.drawRightString(A4[0] - 30, 20, f'Page {doc.page}')
        
        canvas.restoreState()

@login_required
def download_receipt(request, payment_id):
    """Download payment receipt as PDF with invoice-like styling"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Create custom document
    doc = ReceiptDocTemplate(buffer, payment, pagesize=A4, topMargin=80, bottomMargin=50)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.HexColor('#374151'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=3,
        textColor=colors.HexColor('#374151')
    )
    
    # Add minimal space after header
    elements.append(Spacer(1, 10))
    
    # Payment Information
    elements.append(Paragraph('PAYMENT INFORMATION', heading_style))
    
    # Get hotel and guest info
    hotel = payment.invoice.stay.reservation.hotel if payment.invoice else None
    guest = payment.invoice.guest if payment.invoice else None
    
    # Create info table
    hotel_info = f"""
    <b style="color: #1e3a8a;">FROM:</b><br/>
    <b>{hotel.name if hotel else 'Hotel'}</b><br/>
    {hotel.address if hotel else ''}<br/>
    {hotel.city if hotel else ''}, {hotel.country if hotel else ''}<br/>
    <b>Phone:</b> {hotel.phone if hotel else ''}<br/>
    <b>Email:</b> {hotel.email if hotel else ''}
    """
    
    payment_info = f"""
    <b style="color: #1e3a8a;">PAYMENT TO:</b><br/>
    <b>{guest.full_name if guest else 'Guest'}</b><br/>
    <b>Email:</b> {guest.email if guest else ''}<br/>
    <b>Phone:</b> {guest.phone if guest else ''}<br/>
    <b>Payment Date:</b> {payment.timestamp.strftime('%B %d, %Y')}<br/>
    <b>Payment Method:</b> {payment.method or 'Credit Card'}
    """
    
    info_data = [
        [Paragraph(hotel_info, normal_style), Paragraph(payment_info, normal_style)]
    ]
    
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # Payment details
    payment_details_data = [
        ['Payment ID:', str(payment.id)[:8].upper(), 'Amount:', f"${payment.amount:.2f}"],
        ['Status:', payment.status.upper(), 'Method:', payment.method or 'Credit Card']
    ]
    
    if payment.invoice:
        payment_details_data.append(['Invoice:', payment.invoice.invoice_number, 'Date:', payment.timestamp.strftime('%B %d, %Y')])
    
    details_table = Table(payment_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#3b82f6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#93c5fd')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(details_table)
    elements.append(Spacer(1, 20))
    
    # Payment amount table
    elements.append(Paragraph('PAYMENT DETAILS', heading_style))
    
    amount_data = [
        ['Description', 'Amount']
    ]
    
    if payment.invoice:
        amount_data.append([f'Payment for Invoice #{payment.invoice.invoice_number}', f"${payment.amount:.2f}"])
    else:
        amount_data.append(['Payment Received', f"${payment.amount:.2f}"])
    
    # Add total
    amount_data.extend([
        ['', ''],
        ['TOTAL PAID:', f"${payment.amount:.2f}"]
    ])
    
    amount_table = Table(amount_data, colWidths=[5*inch, 2*inch])
    amount_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        
        # Total section
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        
        # Grid
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor('#e5e7eb')),
        ('GRID', (0, -1), (-1, -1), 1, colors.HexColor('#9ca3af')),
        
        # Alignment
        ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
        ('ALIGN', (1, -1), (-1, -1), 'RIGHT'),
    ]))
    
    elements.append(amount_table)
    elements.append(Spacer(1, 15))
    
    # Payment status
    if payment.status == 'completed':
        status_text = f"<b style='color: #059669; font-size: 14px;'>✓ PAYMENT STATUS: COMPLETED</b><br/>Payment processed on {payment.timestamp.strftime('%B %d, %Y')}"
    elif payment.status == 'refunded':
        status_text = f"<b style='color: #dc2626; font-size: 14px;'>↩ PAYMENT STATUS: REFUNDED</b><br/>Payment was refunded"
    else:
        status_text = f"<b style='color: #f59e0b; font-size: 14px;'>⏳ PAYMENT STATUS: {payment.status.upper()}</b><br/>Payment processed on {payment.timestamp.strftime('%B %d, %Y')}"
    
    elements.append(Paragraph(status_text, normal_style))
    elements.append(Spacer(1, 10))
    
    # Thank you note
    thank_you = Paragraph(
        "<b>Thank you for your payment!</b><br/>This receipt confirms your payment has been processed.",
        ParagraphStyle(
            'ThankYou',
            parent=normal_style,
            alignment=TA_CENTER,
            fontSize=12,
            textColor=colors.HexColor('#1e3a8a'),
            spaceBefore=10
        )
    )
    elements.append(thank_you)
    
    # Add receipt date at bottom right
    elements.append(Spacer(1, 15))
    receipt_date = Paragraph(
        f"Receipt Date: {payment.timestamp.strftime('%B %d, %Y')}",
        ParagraphStyle(
            'ReceiptDate',
            parent=normal_style,
            alignment=TA_RIGHT,
            fontSize=10,
            textColor=colors.HexColor('#374151')
        )
    )
    elements.append(receipt_date)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{str(payment.id)[:8]}.pdf"'
    response.write(pdf)
    
    return response

@login_required
def refund_payment(request, payment_id):
    """Refund payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        if payment.status == 'completed':
            payment.status = 'refunded'
            payment.save()
            messages.success(request, f'Payment #{payment.id} has been refunded successfully!')
        else:
            messages.error(request, 'Only completed payments can be refunded.')
        return redirect('billing:payment_list')
    
    return render(request, 'billing/refund_payment.html', {'payment': payment})

@login_required
def create_invoice(request):
    """Create new invoice"""
    if request.method == 'POST':
        messages.success(request, 'Invoice created successfully!')
        return redirect('billing:invoice_list')
    
    # Get unpaid reservations (stays without invoices)
    from reservations.models import Stay
    unpaid_stays = Stay.objects.filter(
        invoice__isnull=True,
        actual_check_out__isnull=False
    ).select_related('reservation__guest', 'room')
    
    context = {
        'unpaid_stays': unpaid_stays
    }
    
    return render(request, 'billing/create_invoice.html', context)