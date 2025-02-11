# Generated by Django 4.2.5 on 2025-02-11 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, choices=[('Crypto', 'Crypto'), ('Immo', 'Immo'), ('Bourse', 'Bourse'), ('Autre', 'Autre')], max_length=50, null=True)),
                ('type', models.CharField(blank=True, max_length=50, null=True)),
                ('company', models.CharField(blank=True, max_length=50, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('sector', models.CharField(blank=True, max_length=100, null=True)),
                ('industry', models.CharField(blank=True, max_length=100, null=True)),
                ('ticker', models.CharField(max_length=10, unique=True)),
                ('currency', models.CharField(choices=[('EUR', 'Eur'), ('USD', 'Usd'), ('GBP', 'Gbp'), ('JPY', 'Jpy')], default='EUR', max_length=10)),
                ('last_value', models.FloatField()),
                ('date_value', models.DateField()),
                ('market_cap', models.FloatField(blank=True, null=True)),
                ('isin_code', models.IntegerField(blank=True, null=True)),
                ('beta', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.FloatField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('device', models.CharField(choices=[('USD/EUR', 'USD/EUR'), ('EUR/USD', 'EUR/USD'), ('GBP/EUR', 'GBP/EUR'), ('EUR/GBP', 'EUR/GBP'), ('JPY/EUR', 'JPY/EUR'), ('EUR/JPY', 'EUR/JPY')], max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OneYearValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.FloatField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='General.asset')),
            ],
        ),
        migrations.CreateModel(
            name='OldValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.FloatField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='General.asset')),
            ],
        ),
    ]
