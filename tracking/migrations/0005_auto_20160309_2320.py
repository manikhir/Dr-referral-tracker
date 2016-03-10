# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0004_referral_to_patientvisit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agent',
            old_name='referral_special',
            new_name='agent_special',
        ),
    ]
