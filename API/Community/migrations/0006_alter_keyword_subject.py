# Generated by Django 5.0.7 on 2024-08-17 17:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Community", "0005_alter_subject_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="keyword",
            name="subject",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="keyword",
                to="Community.subject",
            ),
        ),
    ]