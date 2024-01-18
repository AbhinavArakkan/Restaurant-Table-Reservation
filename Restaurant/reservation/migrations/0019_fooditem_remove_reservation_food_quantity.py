# Generated by Django 4.2.7 on 2023-11-26 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0018_reservation_food_quantity'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_item', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='food_quantity',
        ),
    ]
