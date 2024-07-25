# Generated by Django 5.0.7 on 2024-07-16 20:50

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0002_setting"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="otp_verif",
            field=models.DateTimeField(default=datetime.datetime(2000, 1, 1, 1, 1, 1)),
        ),
        migrations.AddField(
            model_name="user",
            name="phone_verif",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]