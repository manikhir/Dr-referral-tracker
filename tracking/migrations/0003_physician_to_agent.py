# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.migrations.operations import RenameModel, RenameField, AlterField

from tracking.models import Organization, Agent


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0002_referral_referral_date'),
    ]

    operations = [
        RenameModel("Physician", "Agent"),
        RenameField("Agent","physician_name","agent_name"),
        RenameField("Agent","physician_phone","agent_phone"),
        RenameField("Agent","physician_email","agent_email"),
        AlterField("Agent", "organization", models.ForeignKey(
                      Organization, related_name="Agent",verbose_name="Group")),
        RenameField("Referral","physician","agent"),
        AlterField("Referral", "agent", models.ForeignKey(
                                          Agent, related_name="Referral")),
        RenameField("ThankyouMails","physician","agent"),
        AlterField("ThankyouMails", "agent", models.ForeignKey(
                                          Agent, related_name="thankyou_mail")),
        
    ]
