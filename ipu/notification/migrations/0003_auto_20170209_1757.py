# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-09 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_issue_issuereply'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issuereply',
            name='actor',
        ),
        migrations.AddField(
            model_name='issue',
            name='solver_username',
            field=models.CharField(blank=True, max_length=32, verbose_name='Solver'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='solved_by',
            field=models.CharField(blank=True, max_length=64, verbose_name='Answered By'),
        ),
    ]