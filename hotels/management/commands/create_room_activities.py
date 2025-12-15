from django.core.management.base import BaseCommand
from hotels.models import Room
from hotels.activity_models import RoomActivityLog
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial room activities for existing rooms'

    def handle(self, *args, **options):
        system_user = User.objects.filter(is_superuser=True).first()
        
        for room in Room.objects.all():
            # Create room creation activity if not exists
            if not room.activity_logs.filter(action='other', description__contains='created').exists():
                RoomActivityLog.log_activity(
                    room=room,
                    user=system_user,
                    action='other',
                    description=f'Room {room.room_number} created',
                    metadata={'room_type': room.room_type.name if room.room_type else None}
                )
                self.stdout.write(f'Created activity for room {room.room_number}')
        
        self.stdout.write(self.style.SUCCESS('Successfully created room activities'))