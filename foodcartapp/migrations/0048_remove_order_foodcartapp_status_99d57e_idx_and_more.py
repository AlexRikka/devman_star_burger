# Generated by Django 5.1.4 on 2025-02-25 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_order_payment_type'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='order',
            name='foodcartapp_status_99d57e_idx',
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'payment_type'], name='foodcartapp_status_cbc190_idx'),
        ),
    ]
