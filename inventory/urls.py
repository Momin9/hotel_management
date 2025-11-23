from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_dashboard, name='dashboard'),
    path('items/', views.item_list, name='item_list'),
    path('items/new/', views.create_item, name='create_item'),
    path('items/<uuid:item_id>/', views.item_detail, name='item_detail'),
    path('stock-movements/', views.stock_movements, name='stock_movements'),
    path('purchase-orders/', views.purchase_orders, name='purchase_orders'),
    path('suppliers/', views.supplier_list, name='suppliers'),
    path('stock-take/', views.stock_take, name='stock_take'),
]