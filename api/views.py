from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .serializers import *
from hotels.models import Hotel, Room
from reservations.models import Reservation
from front_desk.models import CheckInOut
from housekeeping.models import HousekeepingTask
from maintenance.models import MaintenanceIssue
from pos.models import POSOrder
from billing.models import Invoice

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated]

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available rooms"""
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if check_in and check_out:
            # Filter rooms that are not reserved for the given dates
            occupied_rooms = Reservation.objects.filter(
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=['confirmed', 'checked_in']
            ).values_list('room_type__rooms__id', flat=True)
            
            available_rooms = Room.objects.exclude(id__in=occupied_rooms).filter(status='clean')
        else:
            available_rooms = Room.objects.filter(status='clean')
        
        serializer = self.get_serializer(available_rooms, many=True)
        return Response(serializer.data)

class GuestProfileViewSet(viewsets.ModelViewSet):
    queryset = GuestProfile.objects.all()
    serializer_class = GuestProfileSerializer
    permission_classes = [IsAuthenticated]

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def arrivals_today(self, request):
        """Get today's arrivals"""
        today = timezone.now().date()
        arrivals = Reservation.objects.filter(
            check_in=today,
            status__in=['confirmed', 'checked_in']
        )
        serializer = self.get_serializer(arrivals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def departures_today(self, request):
        """Get today's departures"""
        today = timezone.now().date()
        departures = Reservation.objects.filter(
            check_out=today,
            status='checked_in'
        )
        serializer = self.get_serializer(departures, many=True)
        return Response(serializer.data)

class CheckInOutViewSet(viewsets.ModelViewSet):
    queryset = CheckInOut.objects.all()
    serializer_class = CheckInOutSerializer
    permission_classes = [IsAuthenticated]

class HousekeepingTaskViewSet(viewsets.ModelViewSet):
    queryset = HousekeepingTask.objects.all()
    serializer_class = HousekeepingTaskSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.notes = request.data.get('notes', task.notes)
        task.save()
        
        # Update room status if it's a cleaning task
        if task.task_type == 'checkout_cleaning':
            task.room.status = 'clean'
            task.room.save()
        
        return Response({'status': 'Task completed successfully'})

class MaintenanceIssueViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceIssue.objects.all()
    serializer_class = MaintenanceIssueSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def resolve_issue(self, request, pk=None):
        """Mark issue as resolved"""
        issue = self.get_object()
        issue.status = 'resolved'
        issue.resolved_at = timezone.now()
        issue.resolution_notes = request.data.get('resolution_notes', '')
        issue.actual_cost = request.data.get('actual_cost', issue.estimated_cost)
        issue.save()
        
        return Response({'status': 'Issue resolved successfully'})

class POSOrderViewSet(viewsets.ModelViewSet):
    queryset = POSOrder.objects.all()
    serializer_class = POSOrderSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(POSOrder.STATUS_CHOICES):
            order.status = new_status
            if new_status == 'served':
                order.served_at = timezone.now()
                order.served_by = request.user
            order.save()
            
            return Response({'status': f'Order status updated to {new_status}'})
        
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    today = timezone.now().date()
    
    # Room statistics
    total_rooms = Room.objects.count()
    occupied_rooms = CheckInOut.objects.filter(
        status='checked_in',
        checked_out_at__isnull=True
    ).count()
    available_rooms = total_rooms - occupied_rooms
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Revenue statistics
    total_revenue = Invoice.objects.filter(
        date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Maintenance and housekeeping
    pending_maintenance = MaintenanceIssue.objects.filter(
        status__in=['open', 'in_progress']
    ).count()
    
    housekeeping_tasks = HousekeepingTask.objects.filter(
        status='pending'
    ).count()
    
    stats = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'occupancy_rate': round(occupancy_rate, 2),
        'total_revenue': total_revenue,
        'pending_maintenance': pending_maintenance,
        'housekeeping_tasks': housekeeping_tasks,
    }
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def occupancy_chart_data(request):
    """Get occupancy data for charts"""
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Calculate occupancy for each day
        total_rooms = Room.objects.count()
        occupied = CheckInOut.objects.filter(
            checked_in_at__date__lte=current_date
        ).filter(
            Q(checked_out_at__date__gt=current_date) | Q(checked_out_at__isnull=True)
        ).count()
        
        occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0
        
        # Calculate revenue for the day
        revenue = Invoice.objects.filter(
            date__date=current_date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        data.append({
            'date': current_date,
            'occupancy_rate': round(occupancy_rate, 2),
            'revenue': revenue
        })
        
        current_date += timedelta(days=1)
    
    serializer = OccupancyDataSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue_chart_data(request):
    """Get revenue data for charts"""
    months = int(request.query_params.get('months', 12))
    
    data = []
    current_date = timezone.now().date().replace(day=1)
    
    for i in range(months):
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        # Room revenue
        room_revenue = Invoice.objects.filter(
            date__date__range=[month_start, month_end]
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # POS revenue
        pos_revenue = POSOrder.objects.filter(
            order_time__date__range=[month_start, month_end],
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        data.append({
            'month': current_date.strftime('%Y-%m'),
            'room_revenue': room_revenue,
            'pos_revenue': pos_revenue,
            'total_revenue': room_revenue + pos_revenue
        })
        
        # Move to previous month
        if current_date.month == 1:
            current_date = current_date.replace(year=current_date.year - 1, month=12)
        else:
            current_date = current_date.replace(month=current_date.month - 1)
    
    serializer = RevenueDataSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_checkin(request):
    """Quick check-in API endpoint"""
    reservation_id = request.data.get('reservation_id')
    room_id = request.data.get('room_id')
    
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        room = Room.objects.get(id=room_id)
        
        # Create check-in record
        checkin = CheckInOut.objects.create(
            reservation=reservation,
            guest=reservation.guest,
            room=room,
            checked_in_at=timezone.now(),
            checked_in_by=request.user,
            number_of_guests=request.data.get('number_of_guests', reservation.adults)
        )
        
        # Update statuses
        reservation.status = 'checked_in'
        reservation.save()
        
        room.status = 'occupied'
        room.save()
        
        serializer = CheckInOutSerializer(checkin)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except (Reservation.DoesNotExist, Room.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_checkout(request):
    """Quick check-out API endpoint"""
    checkin_id = request.data.get('checkin_id')
    
    try:
        checkin = CheckInOut.objects.get(id=checkin_id)
        
        # Update check-in record
        checkin.checked_out_at = timezone.now()
        checkin.checked_out_by = request.user
        checkin.status = 'checked_out'
        checkin.save()
        
        # Update reservation and room status
        checkin.reservation.status = 'checked_out'
        checkin.reservation.save()
        
        checkin.room.status = 'dirty'
        checkin.room.save()
        
        serializer = CheckInOutSerializer(checkin)
        return Response(serializer.data)
        
    except CheckInOut.DoesNotExist:
        return Response({'error': 'Check-in record not found'}, status=status.HTTP_404_NOT_FOUND)