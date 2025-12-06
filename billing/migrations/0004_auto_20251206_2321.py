from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0003_reservationexpense'),
        ('billing', '0003_taxconfiguration_invoice_paid_date_invoice_tax_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='stay',
            field=models.OneToOneField(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='invoice',
                to='reservations.stay'
            ),
        ),
    ]