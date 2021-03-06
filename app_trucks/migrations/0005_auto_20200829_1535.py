# Generated by Django 3.1 on 2020-08-29 20:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_trucks', '0004_auto_20200827_1857'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ['name'], 'verbose_name': 'Company', 'verbose_name_plural': 'Companies'},
        ),
        migrations.AlterModelOptions(
            name='delivery',
            options={'verbose_name': 'Delivery', 'verbose_name_plural': 'Deliveries'},
        ),
        migrations.AlterModelOptions(
            name='payrate',
            options={'ordering': ['ini_date', 'id'], 'verbose_name': 'Payrate', 'verbose_name_plural': 'Payrates'},
        ),
        migrations.AlterModelOptions(
            name='truck',
            options={'ordering': ['-year'], 'verbose_name': 'Truck', 'verbose_name_plural': 'Trucks'},
        ),
        migrations.AlterModelOptions(
            name='workday',
            options={'ordering': ['-date_created'], 'verbose_name': 'Workday', 'verbose_name_plural': 'Workdays'},
        ),
        migrations.AlterField(
            model_name='delivery',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='app_trucks.company'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='workday',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='app_trucks.workday'),
        ),
        migrations.AlterField(
            model_name='payrate',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pay_rates', to='app_trucks.company'),
        ),
        migrations.AlterField(
            model_name='workday',
            name='truck',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workdays', to='app_trucks.truck'),
        ),
        migrations.AlterField(
            model_name='workday',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workdays', to=settings.AUTH_USER_MODEL),
        ),
    ]
