# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0005_auto_20160803_0313'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='BACKUP',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='DEBUG',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='HARDCODE',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='LOG',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='WEBVIEW',
            field=models.BooleanField(default=False),
        ),
    ]
