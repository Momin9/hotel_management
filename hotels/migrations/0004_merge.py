# Merge migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0003_hotel_deleted_at'),
        ('hotels', '0003_room_models'),
    ]

    operations = [
        # No operations needed for merge
    ]