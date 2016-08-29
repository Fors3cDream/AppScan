# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0008_auto_20160812_0331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticanalyzerandroid',
            name='DATE',
            field=models.CharField(default=b'2016-08-15', max_length=50),
        ),
    ]
