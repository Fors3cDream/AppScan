# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0003_auto_20160803_0235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticanalyzerandroid',
            name='DATE',
            field=models.DateTimeField(verbose_name=models.DateTimeField(default=b'2016-08-03')),
        ),
    ]
