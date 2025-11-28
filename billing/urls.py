from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<uuid:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<uuid:invoice_id>/mark-paid/', views.mark_invoice_paid, name='mark_paid'),
    path('invoices/<uuid:invoice_id>/download/', views.download_invoice_pdf, name='download_pdf'),
    path('checkout/<uuid:stay_id>/', views.checkout_guest, name='checkout_guest'),
    path('payments/', views.payment_list, name='payment_list'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),
]