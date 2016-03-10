# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.migrations.operations import RenameModel


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0003_physician_to_agent'),
    ]

    operations = [
        RenameModel("Referral", "PatientVisit"),
    ]
