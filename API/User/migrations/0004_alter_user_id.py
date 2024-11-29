# Generated by Django 5.0.7 on 2024-07-16 21:51

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0003_user_otp_verif_user_phone_verif_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False, unique=True
            ),
        ),
    ]
