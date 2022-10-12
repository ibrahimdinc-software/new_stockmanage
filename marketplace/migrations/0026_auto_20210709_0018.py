# Generated by Django 3.1.2 on 2021-07-09 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0025_usermarketshipmentrulemodel_cargo'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketproductmodel',
            name='commissionRate',
            field=models.FloatField(default=0, verbose_name='Komisyon Oranı'),
        ),
        migrations.AlterField(
            model_name='marketorderpredcostmodel',
            name='costAmount',
            field=models.FloatField(blank=True, null=True, verbose_name='Tutar'),
        ),
        migrations.AlterField(
            model_name='marketorderpredcostmodel',
            name='costType',
            field=models.CharField(choices=[('shipment', 'Kargo'), ('commission', 'Komisyon'), ('purchasePrice', 'Alım Fiyatı'), ('extra', 'Ekstra')], max_length=255, verbose_name='Gider Türü'),
        ),
    ]