
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from datetime import datetime , timedelta, date
from django.db.models import Sum

today = date.today()
LAST_MONTH = date(day=1, month=today.month, year=today.year) - timedelta(days=1)
LAST_12_MONTH = LAST_MONTH - timedelta(days=364)

class Organization(models.Model):
    '''
    An Agent works for an Organization, (clinic, hospital, private practice...)
    Need a few "special Organizations"
        - Marketing
        - Patient
        - ? How can the user add special Organizations
        If org_special==True then only require org_name and call it Referral group type
    https://github.com/stefanfoulis/django-phonenumber-field
    pip install django-phonenumber-field
    '''
    org_name = models.CharField(
        "Group Name", max_length=254, unique=True, blank=False, null=True)
    org_contact_name = models.CharField(
        "Contact name", max_length=254, blank=True, null=True)
    org_phone = PhoneNumberField("Phone", blank=True)
    org_email = models.EmailField("Email address", max_length=254, blank=True)
    org_special = models.BooleanField("Special type", default=False)

    def get_absolute_url(self):
        return reverse('add-organization')

    def __str__(self):
        return self.org_name

    def get_agent(self):
        physicians_sort = self.Agent.filter().extra(
            select={'lower_physician_name': 'lower(physician_name)'}
            ).order_by('lower_physician_name')
        return physicians_sort


class Agent(models.Model):
    """
    An Agent works for an Organization; clinic, hospital, private practice...
    Other referral types for example; Other patient, google adds, website.....
    If agent_special==True then only require agent_name but call it "Referral source"
    """
    organization = models.ForeignKey(
        Organization, related_name="Agent",verbose_name="Group")
    agent_name = models.CharField(
        "Practitioner Name", max_length=254, unique=True, blank=False, null=True)
    agent_phone = PhoneNumberField("Phone", blank=True)
    agent_email = models.EmailField(
        "Email address", max_length=254, blank=True)
    agent_special = models.BooleanField("Special type", default=False)

    def __str__(self):
        return self.agent_name

    def get_patient_visits(self, params):
        today = params['to_date']
        week_ago = params['from_date']
        referral_sort = self.Referral.filter(visit_date__range=(str(week_ago), str(today))).values('visit_date').annotate(visit=Sum('visit_count')).order_by('-visit_date')
        return referral_sort


class PatientVisit(models.Model):
    """
    Patient Visit, or Referral, is a patient visit referred to the clinic from 
    an "Agent" that is part of an "Organization".
    Not sure how to do the multiple ForeignKey or if that is right.
    """
    agent = models.ForeignKey(
        Agent, related_name="Referral")
    visit_date = models.DateField("Date", default=date.today)
    visit_count = models.IntegerField("Referrals", default=1)
    referral_date = models.DateTimeField("Referral Date", default=timezone.now)

    def __str__(self):
        return self.physician.organization.org_name

class EmailReport(models.Model):
    """EmailReport for each physician"""
    month = models.IntegerField("month")
    year = models.IntegerField("year")
    is_sent = models.BooleanField("sent", default=False)

    def __str__(self):
        return str(self.month)+" "+str(self.year)

class ThankyouMails(models.Model):
    """
    Mail will be send to Agent at end-of-the-day
    having month and year referrals count
    """
    agent = models.ForeignKey(Agent, related_name="thankyou_mail")
    emailreport = models.ForeignKey(EmailReport, related_name="email_report", default=1)
    month_referrals = models.IntegerField("Month-Referrals")
    year_referrals = models.IntegerField("Year-Referrals")
    active = models.BooleanField("approve", default=False)

    def __str__(self):
        return str(self.physician)
