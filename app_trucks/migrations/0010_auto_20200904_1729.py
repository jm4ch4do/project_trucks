# Generated by Django 3.1 on 2020-09-04 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_trucks', '0009_auto_20200903_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='default_pay_rate',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='payrate',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='workday',
            name='income',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
