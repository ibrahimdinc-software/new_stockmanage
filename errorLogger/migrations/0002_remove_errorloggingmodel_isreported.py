# Generated by Django 3.1.2 on 2021-06-07 00:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('errorLogger', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='errorloggingmodel',
            name='isReported',
        ),
    ]
