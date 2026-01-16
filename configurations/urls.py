from django.urls import path
from . import views

app_name = 'configurations'

urlpatterns = [
    # Room Type URLs
    path('room-types/', views.room_type_list, name='room_type_list'),
    path('room-types/create/', views.room_type_create, name='room_type_create'),
    path('room-types/<uuid:pk>/', views.room_type_detail, name='room_type_detail'),
    path('room-types/<uuid:pk>/edit/', views.room_type_edit, name='room_type_edit'),
    path('room-types/<uuid:pk>/delete/', views.room_type_delete, name='room_type_delete'),
    
    # Room Category URLs
    path('room-categories/', views.room_category_list, name='room_category_list'),
    path('room-categories/create/', views.room_category_create, name='room_category_create'),
    path('room-categories/<uuid:pk>/', views.room_category_detail, name='room_category_detail'),
    path('room-categories/<uuid:pk>/edit/', views.room_category_edit, name='room_category_edit'),
    path('room-categories/<uuid:pk>/delete/', views.room_category_delete, name='room_category_delete'),
    
    # Bed Type URLs
    path('bed-types/', views.bed_type_list, name='bed_type_list'),
    path('bed-types/create/', views.bed_type_create, name='bed_type_create'),
    path('bed-types/<uuid:pk>/', views.bed_type_detail, name='bed_type_detail'),
    path('bed-types/<uuid:pk>/edit/', views.bed_type_edit, name='bed_type_edit'),
    path('bed-types/<uuid:pk>/delete/', views.bed_type_delete, name='bed_type_delete'),
    
    # Floor URLs
    path('floors/', views.floor_list, name='floor_list'),
    path('floors/create/', views.floor_create, name='floor_create'),
    path('floors/<uuid:pk>/', views.floor_detail, name='floor_detail'),
    path('floors/<uuid:pk>/edit/', views.floor_edit, name='floor_edit'),
    path('floors/<uuid:pk>/delete/', views.floor_delete, name='floor_delete'),
    
    # Amenity URLs
    path('amenities/', views.amenity_list, name='amenity_list'),
    path('amenities/create/', views.amenity_create, name='amenity_create'),
    path('amenities/<uuid:pk>/', views.amenity_detail, name='amenity_detail'),
    path('amenities/<uuid:pk>/edit/', views.amenity_edit, name='amenity_edit'),
    path('amenities/<uuid:pk>/delete/', views.amenity_delete, name='amenity_delete'),
]