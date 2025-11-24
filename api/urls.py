from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'hotels', views.HotelViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'guests', views.GuestProfileViewSet)
router.register(r'reservations', views.ReservationViewSet)
router.register(r'checkins', views.CheckInOutViewSet)
router.register(r'housekeeping', views.HousekeepingTaskViewSet)
router.register(r'maintenance', views.MaintenanceIssueViewSet)
router.register(r'pos-orders', views.POSOrderViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/occupancy/', views.occupancy_chart_data, name='occupancy_data'),
    path('dashboard/revenue/', views.revenue_chart_data, name='revenue_data'),
    path('quick-checkin/', views.quick_checkin, name='quick_checkin'),
    path('quick-checkout/', views.quick_checkout, name='quick_checkout'),
]