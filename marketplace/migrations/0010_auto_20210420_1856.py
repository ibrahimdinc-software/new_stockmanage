# Generated by Django 3.1.2 on 2021-04-20 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0009_marketbuyboxtracemodel_uncomp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='marketbuyboxtracemodel',
            name='uncomp',
        ),
        migrations.AddField(
            model_name='marketproductbuyboxlistmodel',
            name='uncomp',
            field=models.BooleanField(default=False, verbose_name='Rekabet edilebilir mi?'),
        ),
    ]
