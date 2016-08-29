# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0009_auto_20160815_0223'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='HASHUSER',
            field=models.CharField(default=b'', max_length=50),
        ),
    ]
