# Generated migration to add temp_id field for customer mapping

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0012_order_orderitem_order_dashboard_o_order_n_60b43e_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='temp_id',
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name="Временен ID",
                help_text="Оригинален Customer-ID от старата система",
                unique=True
            ),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['temp_id'], name='dashboard_customer_temp_id_idx'),
        ),
    ]
