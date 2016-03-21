# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-04 22:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kibali', '0002_signatureconfiguration'),
    ]

    operations = [
        migrations.AddField(
            model_name='signatureconfiguration',
            name='label',
            field=models.TextField(default='', verbose_name='The human-readable name for the application using the signatures. Primarily used for record-keeping and organization.'),
            preserve_default=False,
        ),
    ]