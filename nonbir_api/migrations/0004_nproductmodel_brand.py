# Generated by Django 3.1.2 on 2021-05-06 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nonbir_api', '0003_auto_20210505_0024'),
    ]

    operations = [
        migrations.AddField(
            model_name='nproductmodel',
            name='brand',
            field=models.CharField(default='', max_length=255, verbose_name='Marka'),
            preserve_default=False,
        ),
    ]