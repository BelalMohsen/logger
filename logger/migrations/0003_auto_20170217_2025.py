# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-17 19:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0002_auto_20161226_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datum',
            name='type',
            field=models.CharField(choices=[('INT', 'Integer'), ('FLOAT', 'Float'), ('STRING', 'String'), ('DATE', 'Date'), ('DATETIME', 'Date & time'), ('TIMESTAMP', 'Timestamp')], default='STRING', max_length=15),
        ),
    ]
