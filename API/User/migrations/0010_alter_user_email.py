# Generated by Django 5.0.7 on 2024-08-16 14:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0009_user_date_token_user_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]