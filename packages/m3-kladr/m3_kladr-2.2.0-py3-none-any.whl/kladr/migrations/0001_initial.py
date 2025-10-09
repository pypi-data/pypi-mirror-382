# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KladrGeo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40, db_index=True)),
                ('socr', models.CharField(max_length=10, db_index=True)),
                ('code', models.CharField(max_length=13, db_index=True)),
                ('zipcode', models.CharField(max_length=6)),
                ('gni', models.CharField(max_length=4)),
                ('uno', models.CharField(max_length=4)),
                ('okato', models.CharField(max_length=11)),
                ('status', models.CharField(max_length=1)),
                ('level', models.IntegerField(null=True, blank=True)),
                ('parent', models.ForeignKey(blank=True, to='kladr.KladrGeo', null=True, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='KladrStreet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40, db_index=True)),
                ('socr', models.CharField(max_length=10, db_index=True)),
                ('code', models.CharField(max_length=17, db_index=True)),
                ('zipcode', models.CharField(max_length=6)),
                ('gni', models.CharField(max_length=4)),
                ('uno', models.CharField(max_length=4)),
                ('okato', models.CharField(max_length=11)),
                ('parent', models.ForeignKey(blank=True, to='kladr.KladrGeo', null=True, on_delete=models.CASCADE)),
            ],
        ),
    ]
