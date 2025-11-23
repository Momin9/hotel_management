from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('payments/', views.payment_list, name='payment_list'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),
]