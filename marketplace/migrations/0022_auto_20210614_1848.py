# Generated by Django 3.1.2 on 2021-06-14 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0021_auto_20210505_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermarketplacemodel',
            name='marketType',
            field=models.CharField(choices=[('hepsiburada', 'Hepsiburada'), ('trendyol', 'Trendyol'), ('n11', 'N11'), ('wix', 'Wix')], max_length=255, verbose_name='Market Tipi'),
        ),
    ]
