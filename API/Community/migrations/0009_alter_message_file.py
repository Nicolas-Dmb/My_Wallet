# Generated by Django 5.0.7 on 2024-08-28 16:54

import Community.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Community", "0008_alter_message_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="file",
            field=models.FileField(
                blank=True, null=True, upload_to=Community.models.upload_to
            ),
        ),
    ]
