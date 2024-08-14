# Generated by Django 5.0.7 on 2024-08-14 16:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0008_alter_setting_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="date_token",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="token",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
