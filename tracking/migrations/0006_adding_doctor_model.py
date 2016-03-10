# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0005_auto_20160309_2320'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('doctor_name', models.CharField(max_length=254, verbose_name='Doctor Name', null=True, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='agent',
            name='agent_name',
            field=models.CharField(max_length=254, verbose_name='Agent Name', null=True, unique=True),
        ),
        migrations.AddField(
            model_name='patientvisit',
            name='doctor',
            field=models.ForeignKey(null=True, to='tracking.Doctor', related_name='Referral'),
        ),
    ]
