# Generated by Django 5.0.7 on 2024-07-26 13:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0005_user_otp_generate_user_otp_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="otp_generate",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 26, 13, 29, 16, 436778, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="otp_verif",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 7, 26, 13, 29, 16, 436380, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
