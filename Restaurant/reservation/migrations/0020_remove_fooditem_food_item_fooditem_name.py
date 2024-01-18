# Generated by Django 4.2.7 on 2023-11-26 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0019_fooditem_remove_reservation_food_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fooditem',
            name='food_item',
        ),
        migrations.AddField(
            model_name='fooditem',
            name='name',
            field=models.CharField(default='Default Food Item Name', max_length=255),
        ),
    ]