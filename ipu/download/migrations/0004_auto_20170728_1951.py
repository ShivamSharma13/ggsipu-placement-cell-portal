# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-07-28 14:21
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('download', '0003_auto_20170726_2240'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zippedfile',
            name='id',
        ),
        migrations.AddField(
            model_name='zippedfile',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
