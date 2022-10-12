# Generated by Django 3.1.2 on 2021-07-23 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0028_auto_20210723_0132'),
    ]

    operations = [
        migrations.RenameField(
            model_name='marketorderdetailmodel',
            old_name='comissionRate',
            new_name='commissionRate',
        ),
        migrations.AlterField(
            model_name='marketordermodel',
            name='cargo',
            field=models.CharField(blank=True, choices=[('tumu', 'Bütün Firmalar'), ('hepsi', 'HepsiJet'), ('aras', 'Aras Kargo'), ('surat', 'Sürat Kargo')], max_length=255, null=True, verbose_name='Kargo Firması'),
        ),
        migrations.AlterField(
            model_name='usermarketshipmentrulemodel',
            name='cargo',
            field=models.CharField(blank=True, choices=[('tumu', 'Bütün Firmalar'), ('hepsi', 'HepsiJet'), ('aras', 'Aras Kargo'), ('surat', 'Sürat Kargo')], max_length=255, null=True, verbose_name='Kargo Firması'),
        ),
    ]
