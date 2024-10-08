# Generated by Django 5.0.7 on 2024-07-15 20:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Setting",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        choices=[("Euro", "Euro"), ("Dollar", "Dollar")],
                        default="Euro",
                        max_length=10,
                    ),
                ),
                ("nightMode", models.BooleanField(default=True)),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("Gray", "Gray"),
                            ("Red", "Red"),
                            ("Pink", "Pink"),
                            ("Purple", "Purple"),
                            ("Blue", "Blue"),
                            ("Green", "Green"),
                            ("Brown", "Brown"),
                            ("Yellow", "Yellow"),
                        ],
                        default="Red",
                        max_length=20,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
