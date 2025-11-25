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
        
        # Define frame for content
        frame = Frame(
            0.75*inch, 0.75*inch,  # x, y
            self.pagesize[0] - 1.5*inch, self.pagesize[1] - 1.5*inch,  # width, height
            leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0
        )
        
        # Create page template
        template = PageTemplate(id='normal', frames=[frame], onPage=self.add_page_decorations)
        self.addPageTemplates([template])
    
    def add_page_decorations(self, canvas, doc):
        """Add header and footer to each page"""
        from accounts.models import Footer
        
        # Get footer info
        footer_info = Footer.objects.first()
        company_name = footer_info.company_name if footer_info else "AuraStay"
        
        # Header
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.HexColor('#0284c7'))  # Royal blue
        canvas.drawCentredText(doc.pagesize[0]/2, doc.pagesize[1] - 0.5*inch, company_name)
        
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredText(doc.pagesize[0]/2, doc.pagesize[1] - 0.7*inch, "Hotel Management System")
        
        # Header line
        canvas.setStrokeColor(colors.HexColor('#0284c7'))
        canvas.setLineWidth(2)
        canvas.line(0.75*inch, doc.pagesize[1] - 0.85*inch, doc.pagesize[0] - 0.75*inch, doc.pagesize[1] - 0.85*inch)
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        
        # Footer info
        if footer_info:
            footer_text = f"{footer_info.copyright_line1} | {footer_info.copyright_line2}"
        else:
            footer_text = "© 2025 AuraStay. All rights reserved. | Design: MA Qureshi | Development: Momin Ali"
        
        canvas.drawCentredText(doc.pagesize[0]/2, 0.5*inch, footer_text)
        
        # Page number
        canvas.drawRightString(doc.pagesize[0] - 0.75*inch, 0.3*inch, f"Page {doc.page}")
        
        # Footer line
        canvas.setStrokeColor(colors.HexColor('#0284c7'))
        canvas.setLineWidth(1)
        canvas.line(0.75*inch, 0.7*inch, doc.pagesize[0] - 0.75*inch, 0.7*inch)
        
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