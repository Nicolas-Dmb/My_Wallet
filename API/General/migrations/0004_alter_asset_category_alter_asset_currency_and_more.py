# Generated by Django 5.0.7 on 2024-09-08 17:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("General", "0003_asset_isin_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Crypto", "Crypto"),
                    ("Immo", "Immo"),
                    ("Bourse", "Bourse"),
                    ("Autre", "Autre"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="currency",
            field=models.CharField(
                choices=[("Eur", "Eur"), ("USD", "Usd")], default="Eur", max_length=10
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="type",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
