# Generated by Django 4.2.7 on 2023-11-26 07:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0014_food'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='menu',
        ),
    ]
