# Generated by Django 5.0.7 on 2024-08-17 16:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Community", "0004_subject_week_subject_weekly_messages"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subject",
            name="description",
            field=models.TextField(),
        ),
    ]
