# Generated by Django 5.0.7 on 2024-09-05 14:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("General", "0002_remove_asset_fee_remove_asset_holding_percentages_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="isin_code",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
