# Generated by Django 5.1.4 on 2025-02-23 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_order_foodcartapp_status_99d57e_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default='', verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('proc', 'В обработке'), ('cook', 'Готовится'), ('dlvr', 'Передан в доставку'), ('end', 'Завершен')], max_length=4, verbose_name='Статус'),
        ),
    ]
