from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.finance_dashboard, name='dashboard'),
    path('expenses/', views.expense_management, name='expenses'),
    path('employee-expenses/', views.employee_expenses, name='employee_expenses'),
    path('payroll/', views.payroll_management, name='payroll'),
    path('international/', views.international_transactions, name='international'),
    path('reports/', views.financial_reports, name='reports'),
]