# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0002_staticanalyzerandroid_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticanalyzerandroid',
            name='DATE',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
