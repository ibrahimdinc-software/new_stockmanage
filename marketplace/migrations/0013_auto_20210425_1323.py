# Generated by Django 3.1.2 on 2021-04-25 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0012_usermarketplacemodel_usermarketshipmentrulemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermarketplacemodel',
            name='supplierId',
            field=models.CharField(max_length=255, unique=True, verbose_name='Trendyol Satıcı ID / Hepsiburada Merchant ID'),
        ),
    ]
