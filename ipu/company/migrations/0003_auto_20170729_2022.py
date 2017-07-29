# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-07-29 14:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20170613_2043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='corporate_code',
            field=models.CharField(max_length=64, unique=True, verbose_name='LLPIN/CIN/Form 1 Ref. No.'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Company / LLP name (As authorized by MCA)'),
        ),
    ]
