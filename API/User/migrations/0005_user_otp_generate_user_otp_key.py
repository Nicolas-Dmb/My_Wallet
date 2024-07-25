# Generated by Django 5.0.7 on 2024-07-25 14:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0004_alter_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="otp_generate",
            field=models.DateTimeField(default=datetime.datetime(2000, 1, 1, 1, 1, 1)),
        ),
        migrations.AddField(
            model_name="user",
            name="otp_key",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]