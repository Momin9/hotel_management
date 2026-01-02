from django.urls import path, include
from . import views

app_name = 'hotels'

urlpatterns = [
    # API URLs
    path('api/', include('hotels.api_urls')),
    path('dashboard/', views.hotel_dashboard, name='dashboard'),
    path('overview/', views.hotel_overview, name='overview'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/create/', views.hotel_create, name='hotel_create'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('hotels/<int:hotel_id>/rooms/', views.room_list, name='room_list'),
    path('hotels/<int:hotel_id>/rooms/create/', views.room_create, name='room_create'),
    path('hotels/<int:hotel_id>/rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('hotels/<int:hotel_id>/rooms/<int:room_id>/edit/', views.room_edit, name='room_edit'),
    
    # Floor Management
    path('hotels/<int:hotel_id>/floors/', views.floor_list, name='floor_list'),
    path('hotels/<int:hotel_id>/floors/create/', views.floor_create, name='floor_create'),
    path('hotels/<int:hotel_id>/floors/<int:floor_id>/edit/', views.floor_edit, name='floor_edit'),
    
    # Room Category Management
    path('hotels/<int:hotel_id>/room-categories/', views.room_category_list, name='room_category_list'),
    path('hotels/<int:hotel_id>/room-categories/create/', views.room_category_create, name='room_category_create'),
    path('hotels/<int:hotel_id>/room-categories/<int:category_id>/edit/', views.room_category_edit, name='room_category_edit'),
    
    # Company Management
    path('hotels/<int:hotel_id>/companies/', views.company_list, name='company_list'),
    path('hotels/<int:hotel_id>/companies/create/', views.company_create, name='company_create'),
    path('hotels/<int:hotel_id>/companies/<int:company_id>/edit/', views.company_edit, name='company_edit'),
    
    # Service Management
    path('hotels/<int:hotel_id>/services/', views.service_list, name='service_list'),
    path('hotels/<int:hotel_id>/services/create/', views.service_create, name='service_create'),
    path('hotels/<int:hotel_id>/services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('hotels/<int:hotel_id>/services/<int:service_id>/edit/', views.service_edit, name='service_edit'),
    path('hotels/<int:hotel_id>/services/<int:service_id>/delete/', views.service_delete, name='service_delete'),
    
    # Google Drive Configuration
    path('hotels/<int:hotel_id>/google-drive-config/', views.google_drive_config, name='google_drive_config'),
    
    # Room Activity Log
    path('rooms/<int:room_id>/add-note/', views.add_room_note, name='add_room_note'),
]