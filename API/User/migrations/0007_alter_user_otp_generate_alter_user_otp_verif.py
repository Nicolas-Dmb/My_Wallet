# Generated by Django 5.0.7 on 2024-07-26 13:45

import User.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0006_alter_user_otp_generate_alter_user_otp_verif"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="otp_generate",
            field=models.DateTimeField(default=User.models.default_otp_time),
        ),
        migrations.AlterField(
            model_name="user",
            name="otp_verif",
            field=models.DateTimeField(default=User.models.default_otp_time),
        ),
    ]
