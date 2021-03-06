# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StaticAnalyzerAndroid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('TITLE', models.TextField()),
                ('APP_NAME', models.TextField()),
                ('SIZE', models.CharField(max_length=50)),
                ('MD5', models.CharField(max_length=30)),
                ('SHA1', models.TextField()),
                ('SHA256', models.TextField()),
                ('PACKAGENAME', models.TextField()),
                ('MAINACTIVITY', models.TextField()),
                ('TARGET_SDK', models.CharField(max_length=50)),
                ('MAX_SDK', models.CharField(max_length=50)),
                ('MIN_SDK', models.CharField(max_length=50)),
                ('ANDROVERNAME', models.CharField(max_length=100)),
                ('ANDROVER', models.CharField(max_length=50)),
                ('MANIFEST_ANAL', models.TextField()),
                ('PERMISSIONS', models.TextField()),
                ('FILES', models.TextField()),
                ('CERTZ', models.TextField()),
                ('ACTIVITIES', models.TextField()),
                ('RECEIVERS', models.TextField()),
                ('PROVIDERS', models.TextField()),
                ('SERVICES', models.TextField()),
                ('LIBRARIES', models.TextField()),
                ('CNT_ACT', models.CharField(max_length=50)),
                ('CNT_PRO', models.CharField(max_length=50)),
                ('CNT_SER', models.CharField(max_length=50)),
                ('CNT_BRO', models.CharField(max_length=50)),
                ('CERT_INFO', models.TextField()),
                ('ISSUED', models.CharField(max_length=50)),
                ('NATIVE', models.CharField(max_length=50)),
                ('DYNAMIC', models.CharField(max_length=50)),
                ('REFLECT', models.CharField(max_length=50)),
                ('CRYPTO', models.CharField(max_length=50)),
                ('OBFUS', models.CharField(max_length=50)),
                ('API', models.TextField()),
                ('DANG', models.TextField()),
                ('URLS', models.TextField()),
                ('DOMAINS', models.TextField()),
                ('EMAILS', models.TextField()),
                ('STRINGS', models.TextField()),
                ('ZIPPED', models.TextField()),
                ('MANI', models.TextField()),
                ('EXPORTED_ACT', models.TextField()),
                ('E_ACT', models.CharField(max_length=50)),
                ('E_SER', models.CharField(max_length=50)),
                ('E_BRO', models.CharField(max_length=50)),
                ('E_CNT', models.CharField(max_length=50)),
            ],
        ),
    ]
