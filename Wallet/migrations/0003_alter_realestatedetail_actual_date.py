# Generated by Django 4.2.5 on 2025-02-25 22:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Wallet', '0002_alter_realestatedetail_actual_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realestatedetail',
            name='actual_date',
            field=models.DateField(default=datetime.date(2025, 2, 25)),
        ),
    ]
