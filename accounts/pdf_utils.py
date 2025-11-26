from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from django.http import HttpResponse
from datetime import datetime
import io

class AuraStayDocTemplate(BaseDocTemplate):
    """Custom document template with AuraStay header and footer"""
    
    def __init__(self, filename, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        
        # Define frame for content (adjusted for centered header/footer)
        frame = Frame(
            0.75*inch, 1.2*inch,  # x, y (more space for footer)
            self.pagesize[0] - 1.5*inch, self.pagesize[1] - 2.4*inch,  # width, height (more space for header/footer)
            leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0
        )
        
        # Create page template
        template = PageTemplate(id='normal', frames=[frame], onPage=self.add_page_decorations)
        self.addPageTemplates([template])
    
    def add_page_decorations(self, canvas, doc):
        """Add centered header and footer to each page with AuraStay branding"""
        from accounts.models import Footer
        from django.conf import settings
        import os
        
        # Get site configuration with fallback
        try:
            from accounts.models import SiteConfiguration
            site_config = SiteConfiguration.get_instance()
        except:
            # Fallback if SiteConfiguration doesn't exist yet
            class FallbackConfig:
                company_name = "AuraStay"
                company_logo = None
                site_description = "Hotel Management System"
            site_config = FallbackConfig()
        
        try:
            footer_info = Footer.objects.first()
        except:
            footer_info = None
        
        canvas.saveState()
        page_width = doc.pagesize[0]
        
        # Header Section - All Centered
        header_y = doc.pagesize[1] - 0.7*inch
        
        # Company logo (centered)
        if hasattr(site_config, 'company_logo') and site_config.company_logo:
            try:
                logo_path = os.path.join(settings.MEDIA_ROOT, site_config.company_logo.name)
                if os.path.exists(logo_path):
                    logo_width = 0.8*inch
                    logo_x = (page_width - logo_width) / 2
                    canvas.drawImage(logo_path, logo_x, header_y + 0.2*inch, width=logo_width, height=0.6*inch, preserveAspectRatio=True)
            except:
                pass
        
        # Company name (centered)
        canvas.setFont('Helvetica-Bold', 20)
        canvas.setFillColor(colors.HexColor('#0284c7'))
        company_name = site_config.company_name
        name_width = canvas.stringWidth(company_name, 'Helvetica-Bold', 20)
        canvas.drawString((page_width - name_width) / 2, header_y, company_name)
        
        # Site description (centered)
        canvas.setFont('Helvetica', 12)
        canvas.setFillColor(colors.HexColor('#475569'))
        description = site_config.site_description
        desc_width = canvas.stringWidth(description, 'Helvetica', 12)
        canvas.drawString((page_width - desc_width) / 2, header_y - 0.25*inch, description)
        
        # Generation timestamp (centered)
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        timestamp = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        time_width = canvas.stringWidth(timestamp, 'Helvetica', 9)
        canvas.drawString((page_width - time_width) / 2, header_y - 0.45*inch, timestamp)
        
        # Header line (centered)
        canvas.setStrokeColor(colors.HexColor('#0284c7'))
        canvas.setLineWidth(2)
        line_margin = 1*inch
        canvas.line(line_margin, header_y - 0.6*inch, page_width - line_margin, header_y - 0.6*inch)
        
        # Footer Section - All Centered
        footer_y = 0.8*inch
        
        # Footer line (centered)
        canvas.setStrokeColor(colors.HexColor('#0284c7'))
        canvas.setLineWidth(1)
        canvas.line(line_margin, footer_y + 0.3*inch, page_width - line_margin, footer_y + 0.3*inch)
        
        # Copyright text (centered)
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        
        if footer_info:
            footer_text = f"{footer_info.copyright_line1} | {footer_info.copyright_line2}"
        else:
            footer_text = "© 2025 AuraStay. All rights reserved. | Design: MA Qureshi | Development: Momin Ali"
        
        footer_width = canvas.stringWidth(footer_text, 'Helvetica', 9)
        canvas.drawString((page_width - footer_width) / 2, footer_y, footer_text)
        
        # Contact info (centered)
        if footer_info and footer_info.email and footer_info.phone:
            contact_info = f"{footer_info.email} | {footer_info.phone}"
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#475569'))
            contact_width = canvas.stringWidth(contact_info, 'Helvetica', 8)
            canvas.drawString((page_width - contact_width) / 2, footer_y - 0.2*inch, contact_info)
        
        # Page number (centered)
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#0284c7'))
        page_text = f"Page {doc.page}"
        page_width_text = canvas.stringWidth(page_text, 'Helvetica-Bold', 10)
        canvas.drawString((page_width - page_width_text) / 2, footer_y - 0.4*inch, page_text)
        
        canvas.restoreState()

def generate_pdf_report(title, data, headers, filename):
    """Generate PDF report with AuraStay header and footer"""
    buffer = io.BytesIO()
    doc = AuraStayDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#0284c7')
    )
    
    # Add some space from header
    elements.append(Spacer(1, 20))
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Date
    date_str = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    elements.append(Paragraph(date_str, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Table
    if data:
        table_data = [headers] + data
        table = Table(table_data)
        
        # Table style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("No data available", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Create response
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def hotels_pdf_report(hotels):
    """Generate PDF report for hotels"""
    headers = ['Hotel Name', 'Owner', 'City', 'Country', 'Currency', 'Status']
    data = []
    
    for hotel in hotels:
        data.append([
            hotel.name,
            hotel.owner.get_full_name(),
            hotel.city,
            hotel.country,
            hotel.currency,
            'Active' if hotel.is_active else 'Inactive'
        ])
    
    return generate_pdf_report('Hotels Report', data, headers, 'hotels_report.pdf')

def subscriptions_pdf_report(subscriptions):
    """Generate PDF report for subscriptions"""
    headers = ['Hotel', 'Plan', 'Status', 'Start Date', 'End Date', 'Billing']
    data = []
    
    for sub in subscriptions:
        data.append([
            sub.hotel.name,
            sub.plan.name,
            sub.status.title(),
            sub.start_date.strftime('%Y-%m-%d'),
            sub.end_date.strftime('%Y-%m-%d'),
            sub.billing_cycle.title()
        ])
    
    return generate_pdf_report('Subscriptions Report', data, headers, 'subscriptions_report.pdf')

def plans_pdf_report(plans):
    """Generate PDF report for subscription plans"""
    headers = ['Plan Name', 'Monthly Price', 'Yearly Price', 'Max Rooms', 'Free Trial', 'Status']
    data = []
    
    for plan in plans:
        data.append([
            plan.name,
            f'${plan.price_monthly}',
            f'${plan.price_yearly}' if plan.price_yearly else 'N/A',
            str(plan.max_rooms),
            'Yes' if plan.is_free_trial else 'No',
            'Active' if plan.is_active else 'Inactive'
        ])
    
    return generate_pdf_report('Subscription Plans Report', data, headers, 'plans_report.pdf')

def hotel_detailed_report(hotel):
    """Generate detailed PDF report for a specific hotel"""
    from accounts.models import SiteConfiguration
    
    buffer = io.BytesIO()
    doc = AuraStayDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=1,
        textColor=colors.HexColor('#0284c7')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#475569')
    )
    
    # Add space from header
    elements.append(Spacer(1, 30))
    
    # Title
    elements.append(Paragraph(f'Hotel Report: {hotel.name}', title_style))
    elements.append(Spacer(1, 20))
    
    # Hotel Information Section
    elements.append(Paragraph('Hotel Information', subtitle_style))
    
    hotel_info = [
        ['Hotel Name:', hotel.name],
        ['Owner:', hotel.owner.get_full_name()],
        ['Email:', hotel.email or 'Not provided'],
        ['Phone:', hotel.phone or 'Not provided'],
        ['Address:', f"{hotel.address}, {hotel.city}, {hotel.country}" if hotel.address else 'Not provided'],
        ['Currency:', hotel.get_currency_display()],
        ['Status:', 'Active' if hotel.is_active else 'Inactive'],
        ['Created:', hotel.created_at.strftime('%B %d, %Y')],
    ]
    
    info_table = Table(hotel_info, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Rooms Summary
    if hasattr(hotel, 'rooms'):
        elements.append(Paragraph('Rooms Summary', subtitle_style))
        
        rooms = hotel.rooms.all()
        if rooms:
            room_data = [['Room Number', 'Type', 'Category', 'Price', 'Status']]
            for room in rooms:
                room_data.append([
                    room.room_number,
                    room.get_type_display(),
                    room.get_category_display(),
                    f'{hotel.currency} {room.price}',
                    room.get_status_display()
                ])
            
            rooms_table = Table(room_data)
            rooms_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(rooms_table)
        else:
            elements.append(Paragraph('No rooms configured for this hotel.', styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{hotel.name}_detailed_report.pdf"'
    return response