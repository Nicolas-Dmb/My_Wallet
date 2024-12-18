# Generated by Django 5.0.7 on 2024-11-30 16:57

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Wallet", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="date_price",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="bourse",
            name="amount",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="bourse",
            name="amount_action",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="bourse",
            name="amount_etf",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="bourse",
            name="amount_forex",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="bourse",
            name="amount_matieres_premieres",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="bourse",
            name="amount_obligation",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="bourse",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="buy",
            name="date_buy",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="cash",
            name="amount",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="cash",
            name="amount_Ass_Vie",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="cash",
            name="amount_CC",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="cash",
            name="amount_CSL_LEP",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="cash",
            name="amount_Livret_A",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="cash",
            name="amount_autre",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="cash",
            name="amount_cto",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="cash",
            name="amount_pea",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="cash",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="amount",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="amount_altcoins",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="amount_btc",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="amount_eth",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="amount_nft",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="amount_stablecoins",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="crypto",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="historicalprice",
            name="date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="historicalwallet",
            name="date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="realestate",
            name="amount",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="realestate",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="realestatedetail",
            name="actual_date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="realestatedetail",
            name="buy_date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="realestatedetail",
            name="sell_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="sells",
            name="date_sold",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="wallet",
            name="date",
            field=models.DateField(auto_now=True),
        ),
    ]
