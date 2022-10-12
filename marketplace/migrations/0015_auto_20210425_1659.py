# Generated by Django 3.1.2 on 2021-04-25 16:59

from django.db import migrations


def customMig(apps, schema_editor):
    marketProductModel = apps.get_model('marketplace', 'MarketProductModel')
    userMaketPlaceModel = apps.get_model('marketplace', 'UserMarketPlaceModel').objects.all()

    for mp in marketProductModel.objects.all():
        ump = userMaketPlaceModel.get(marketType=mp.marketType)
        mp.userMarket = ump
        mp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0014_auto_20210425_1659'),
    ]

    operations = [
        migrations.RunPython(customMig),
    ]