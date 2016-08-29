# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0006_auto_20160803_0745'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='USER',
            field=models.CharField(default=b'', max_length=50),
        ),
        migrations.AlterField(
            model_name='staticanalyzerandroid',
            name='DATE',
            field=models.CharField(default=b'2016-08-11', max_length=50),
        ),
    ]
