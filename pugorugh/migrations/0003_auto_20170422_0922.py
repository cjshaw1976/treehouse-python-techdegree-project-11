# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-04-22 09:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pugorugh', '0002_auto_20170421_1101'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userdog',
            unique_together=set([('user', 'dog')]),
        ),
    ]