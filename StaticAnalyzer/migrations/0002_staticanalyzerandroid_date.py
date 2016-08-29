# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('StaticAnalyzer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticanalyzerandroid',
            name='DATE',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 3, 2, 19, 59, 108145, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
