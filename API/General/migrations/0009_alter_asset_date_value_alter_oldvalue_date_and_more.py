# Generated by Django 5.0.7 on 2024-11-28 13:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("General", "0008_alter_asset_date_value_alter_currency_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="date_value",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="oldvalue",
            name="date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="oneyearvalue",
            name="date",
            field=models.DateField(),
        ),
    ]
