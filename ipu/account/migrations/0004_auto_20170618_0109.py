# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-17 19:39
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_unsuccessfulemail_unsuccessfulsms'),
    ]

    operations = [
        migrations.AddField(
            model_name='unsuccessfulemail',
            name='domain',
            field=models.CharField(default='placements.ggsipu.ac.in', max_length=64),
        ),
        migrations.AddField(
            model_name='unsuccessfulsms',
            name='template_vars',
            field=models.CharField(blank=True, help_text='Comma Separated', max_length=256),
        ),
        migrations.AlterField(
            model_name='unsuccessfulsms',
            name='phone_numbers',
            field=models.TextField(help_text='Comma Separated', validators=[django.core.validators.RegexValidator('^([7-9]\\d{9}(,[7-9]\\d{9})*)$')]),
        ),
    ]