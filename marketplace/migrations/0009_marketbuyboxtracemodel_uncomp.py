# Generated by Django 3.1.2 on 2021-04-20 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0008_marketbuyboxtracemodel_isactive'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketbuyboxtracemodel',
            name='uncomp',
            field=models.BooleanField(default=False, verbose_name='Rekabet edilebilir mi?'),
        ),
    ]
