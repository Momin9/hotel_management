from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_dashboard, name='dashboard'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.create_order, name='create_order'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('menu/', views.menu_management, name='menu'),
    path('menu/add-item/', views.add_menu_item, name='add_item'),
    path('menu/add-category/', views.add_category, name='add_category'),
    path('shift/', views.shift_management, name='shift'),
]