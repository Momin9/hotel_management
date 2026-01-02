from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()

class ExpenseCategory(models.Model):
    """Expense categories for hotel operations"""
    CATEGORY_TYPES = [
        ('OPERATIONAL', 'Operational Expenses'),
        ('ADMIN', 'Administrative Expenses'),
        ('MARKETING', 'Marketing Expenses'),
        ('MAINTENANCE', 'Maintenance Costs'),
        ('UTILITY', 'Utility Expenses'),
        ('SALARY', 'Salary & Benefits'),
        ('TRAVEL', 'Travel & Conveyance'),
        ('CAPEX', 'Capital Expenditures'),
        ('SUPPLIES', 'Supplies & Inventory'),
        ('PROFESSIONAL', 'Professional Services'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    budget_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

class HotelExpense(models.Model):
    """Hotel operational expenses"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense_date = models.DateField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    vendor_name = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    receipt = models.FileField(upload_to='expense_receipts/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_expenses')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vendor_name} - ${self.amount}"

class EmployeeExpense(models.Model):
    """Employee expense reimbursements"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Reimbursed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    expense_date = models.DateField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    description = models.TextField()
    receipt = models.FileField(upload_to='employee_receipts/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_employee_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - ${self.amount}"

class PayrollRecord(models.Model):
    """Employee payroll records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payroll_records')
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'Draft'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid'),
    ], default='DRAFT')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_payrolls')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_net_salary(self):
        overtime_pay = self.overtime_hours * self.overtime_rate
        gross_salary = self.basic_salary + overtime_pay + self.bonus
        self.net_salary = gross_salary - self.deductions - self.tax_deduction
        return self.net_salary

class InternationalTransaction(models.Model):
    """International financial transactions"""
    TRANSACTION_TYPES = [
        ('PAYMENT', 'Payment'),
        ('RECEIPT', 'Receipt'),
        ('TRANSFER', 'Transfer'),
        ('EXCHANGE', 'Currency Exchange'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    from_currency = models.CharField(max_length=3)
    to_currency = models.CharField(max_length=3)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    original_amount = models.DecimalField(max_digits=12, decimal_places=2)
    converted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()
    counterparty = models.CharField(max_length=200)
    swift_code = models.CharField(max_length=20, blank=True)
    reference_number = models.CharField(max_length=50, unique=True)
    compliance_docs = models.FileField(upload_to='international_docs/', blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ], default='PENDING')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class FinancialAlert(models.Model):
    """Financial alerts and notifications"""
    ALERT_TYPES = [
        ('BUDGET_OVERRUN', 'Budget Overrun'),
        ('TAX_DUE', 'Tax Payment Due'),
        ('PAYROLL_DUE', 'Payroll Processing Due'),
        ('EXPENSE_APPROVAL', 'Expense Approval Required'),
        ('LOW_BALANCE', 'Low Bank Balance'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM')
    title = models.CharField(max_length=200)
    message = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']