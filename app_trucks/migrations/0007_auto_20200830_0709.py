# Generated by Django 3.1 on 2020-08-30 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_trucks', '0006_auto_20200829_2016'),
    ]

    operations = [
        migrations.RenameField(
            model_name='delivery',
            old_name='deliveries',
            new_name='amount',
        ),
    ]
