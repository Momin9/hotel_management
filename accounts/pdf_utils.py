from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from django.http import HttpResponse
from datetime import datetime
import io

def generate_pdf_report(title, data, headers, filename):
    """Generate PDF report with table data"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
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