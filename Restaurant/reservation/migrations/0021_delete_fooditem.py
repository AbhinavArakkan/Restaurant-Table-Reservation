# Generated by Django 4.2.7 on 2023-11-26 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0020_remove_fooditem_food_item_fooditem_name'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FoodItem',
        ),
    ]