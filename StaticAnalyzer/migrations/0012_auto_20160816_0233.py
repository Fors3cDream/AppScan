# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0011_auto_20160816_0150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticanalyzerandroid',
            name='MD5',
            field=models.CharField(max_length=100),
        ),
    ]
