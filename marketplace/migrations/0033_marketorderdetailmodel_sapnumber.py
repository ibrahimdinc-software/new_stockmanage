# Generated by Django 4.0.1 on 2022-01-11 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0032_alter_marketbuyboxtracemodel_isactive'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketorderdetailmodel',
            name='sapNumber',
            field=models.IntegerField(default=0, verbose_name='Kalem Numarası'),
        ),
    ]
