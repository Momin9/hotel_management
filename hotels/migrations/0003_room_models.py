# Simple migration for room models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('base_price_multiplier', models.DecimalField(decimal_places=2, default=1.0, max_digits=5)),
                ('amenities', models.TextField(blank=True, help_text='JSON list of amenities')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Room Categories',
            },
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('max_occupancy', models.IntegerField(default=2)),
                ('bed_configuration', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RoomStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('color_code', models.CharField(default='#6B7280', help_text='Hex color code', max_length=7)),
                ('is_available_for_booking', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Room Statuses',
            },
        ),
        migrations.AddField(
            model_name='room',
            name='floor',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='room',
            name='size_sqft',
            field=models.IntegerField(blank=True, help_text='Room size in square feet', null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='view_type',
            field=models.CharField(blank=True, help_text='e.g., Ocean View, City View', max_length=50),
        ),
        migrations.AddField(
            model_name='room',
            name='special_features',
            field=models.TextField(blank=True, help_text='JSON list of special features'),
        ),
        migrations.AddField(
            model_name='room',
            name='room_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='hotels.roomtype'),
        ),
        migrations.AddField(
            model_name='room',
            name='room_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='hotels.roomcategory'),
        ),
        migrations.AddField(
            model_name='room',
            name='room_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='hotels.roomstatus'),
        ),
    ]