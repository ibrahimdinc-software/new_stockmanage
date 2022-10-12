# Generated by Django 3.1.2 on 2021-04-17 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_remove_marketordermodel_customername'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketBuyBoxTraceModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minPrice', models.FloatField(verbose_name='Alt Fiyat')),
                ('maxPrice', models.FloatField(verbose_name='Üst Fiyat')),
                ('priceStep', models.FloatField(verbose_name='Değişim Miktarı')),
                ('marketProduct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.marketproductmodel')),
            ],
        ),
    ]
