# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-27 09:22
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_auto_20160824_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='techprofile',
            name='codechef',
            field=models.CharField(blank=True, help_text='Please provide your Codechef username.', max_length=14, validators=[django.core.validators.RegexValidator('^[a-z]{1}[a-z0-9_]{3,13}$')]),
        ),
    ]