#!/usr/bin/env python3
"""
Create realistic invoices and payments for checked-in guests
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from reservations.models import Reservation, Stay
from billing.models import Invoice, ChargeItem, Payment, Deposit
from django.utils import timezone

def generate_invoice_number():
    """Generate unique invoice number"""
    import time
    timestamp = str(int(time.time()))[-6:]
    return f"INV-{timestamp}-{random.randint(100, 999)}"

def create_invoices_for_stays():
    """Create invoices for all current stays"""
    print("Creating invoices for current stays...")
    
    # Get all stays that don't have invoices yet
    stays = Stay.objects.filter(invoice__isnull=True, actual_check_out__isnull=True)
    
    for stay in stays:
        reservation = stay.reservation
        
        # Calculate room charges
        nights_stayed = (date.today() - reservation.check_in).days
        if nights_stayed <= 0:
            nights_stayed = 1
        
        room_total = reservation.rate * nights_stayed
        
        # Create invoice
        invoice = Invoice.objects.create(
            stay=stay,
            guest=reservation.guest,
            invoice_number=generate_invoice_number(),
            due_date=date.today() + timedelta(days=7),
            tax_rate=Decimal('10.00'),  # 10% tax
            service_charge=room_total * Decimal('0.05'),  # 5% service charge
            currency=reservation.hotel.currency
        )
        
        # Add room charge
        ChargeItem.objects.create(
            invoice=invoice,
            description=f"Room {reservation.room.room_number} - {nights_stayed} nights",
            charge_type='room',
            quantity=nights_stayed,
            unit_price=reservation.rate,
            amount=room_total
        )
        
        # Add random additional charges
        additional_charges = [
            ('Room Service', 'food', random.uniform(25, 80)),
            ('Minibar', 'minibar', random.uniform(15, 45)),
            ('Laundry Service', 'laundry', random.uniform(20, 60)),
            ('Spa Services', 'spa', random.uniform(50, 150)),
            ('Parking', 'parking', random.uniform(10, 25)),
        ]
        
        # Add 2-4 random additional charges
        num_charges = random.randint(2, 4)
        selected_charges = random.sample(additional_charges, num_charges)
        
        for desc, charge_type, amount in selected_charges:
            ChargeItem.objects.create(
                invoice=invoice,
                description=desc,
                charge_type=charge_type,
                quantity=1,
                unit_price=Decimal(str(round(amount, 2))),
                amount=Decimal(str(round(amount, 2)))
            )
        
        # Create deposit
        deposit_amount = reservation.rate * Decimal('1.5')  # 1.5 nights as deposit
        Deposit.objects.create(
            stay=stay,
            amount=deposit_amount,
            status='collected',
            collected_at=stay.actual_check_in
        )
        
        print(f"✓ Created invoice {invoice.invoice_number} for {reservation.guest.full_name}")
        print(f"  Room: {reservation.room.room_number} at {reservation.hotel.name}")
        print(f"  Total: ${invoice.total_amount}")

def create_payments_for_invoices():
    """Create payments for some invoices"""
    print("\nCreating payments for invoices...")
    
    invoices = Invoice.objects.filter(status='draft')
    
    # Pay 70% of invoices completely, 20% partially, 10% unpaid
    total_invoices = invoices.count()
    fully_paid_count = int(total_invoices * 0.7)
    partially_paid_count = int(total_invoices * 0.2)
    
    invoices_list = list(invoices)
    random.shuffle(invoices_list)
    
    # Fully paid invoices
    for i in range(fully_paid_count):
        invoice = invoices_list[i]
        
        # Create full payment
        payment = Payment.objects.create(
            invoice=invoice,
            method=random.choice(['cash', 'card', 'bank_transfer', 'online']),
            amount=invoice.total_amount,
            status='completed',
            reference_number=f"PAY-{random.randint(100000, 999999)}"
        )
        
        # Update invoice
        invoice.paid_amount = invoice.total_amount
        invoice.status = 'paid'
        invoice.paid_date = date.today() - timedelta(days=random.randint(0, 5))
        invoice.save()
        
        print(f"✓ Full payment: {invoice.invoice_number} - ${payment.amount}")
    
    # Partially paid invoices
    for i in range(fully_paid_count, fully_paid_count + partially_paid_count):
        if i < len(invoices_list):
            invoice = invoices_list[i]
            
            # Create partial payment (50-80% of total)
            partial_percentage = random.uniform(0.5, 0.8)
            partial_amount = invoice.total_amount * Decimal(str(partial_percentage))
            
            payment = Payment.objects.create(
                invoice=invoice,
                method=random.choice(['cash', 'card', 'bank_transfer']),
                amount=partial_amount,
                status='completed',
                reference_number=f"PAY-{random.randint(100000, 999999)}"
            )
            
            # Update invoice
            invoice.paid_amount = partial_amount
            invoice.status = 'partial'
            invoice.save()
            
            print(f"✓ Partial payment: {invoice.invoice_number} - ${payment.amount} of ${invoice.total_amount}")
    
    # Remaining invoices stay as 'sent' (unpaid)
    for i in range(fully_paid_count + partially_paid_count, len(invoices_list)):
        invoice = invoices_list[i]
        invoice.status = 'sent'
        invoice.save()
        print(f"✓ Unpaid invoice: {invoice.invoice_number} - ${invoice.total_amount}")

def main():
    """Main function"""
    print("🧾 Creating Realistic Invoices and Payments")
    print("=" * 50)
    
    try:
        # Clear existing billing data
        print("Clearing existing billing data...")
        Payment.objects.all().delete()
        ChargeItem.objects.all().delete()
        Invoice.objects.all().delete()
        Deposit.objects.all().delete()
        
        create_invoices_for_stays()
        create_payments_for_invoices()
        
        # Summary
        total_invoices = Invoice.objects.count()
        total_payments = Payment.objects.filter(status='completed').count()
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        paid_invoices = Invoice.objects.filter(status='paid').count()
        partial_invoices = Invoice.objects.filter(status='partial').count()
        unpaid_invoices = Invoice.objects.filter(status='sent').count()
        
        print("\n" + "=" * 50)
        print("🎉 Invoices and payments created successfully!")
        print(f"Total invoices: {total_invoices}")
        print(f"Paid invoices: {paid_invoices}")
        print(f"Partially paid: {partial_invoices}")
        print(f"Unpaid invoices: {unpaid_invoices}")
        print(f"Total payments: {total_payments}")
        print(f"Total revenue: ${total_revenue}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    # Import models here to avoid circular import
    from django.db import models
    main()