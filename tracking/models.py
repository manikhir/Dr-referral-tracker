
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

class TrackedModel(models.Model):
    creation_time = models.DateTimeField("Creation Timestamp", blank=True, null=True)
    modification_time = models.DateTimeField("Modification Timestamp", blank=True, null=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.creation_time = timezone.now()
        modification_time = timezone.now()
        super(TrackedModel, self).save(*args, **kwargs)    

class Organization(TrackedModel):
    '''
    A ReferringEntity works for a Organization, (clinic, hospital, private practice...)
    Need a few "special Organizations"
        - Marketing
        - Patient
        - ? How can the user add special Organizations
        If org_special==True then only require org_name and call it PatientVisit group type
    https://github.com/stefanfoulis/django-phonenumber-field
    pip install django-phonenumber-field
    '''
    ORG_TYPE_MARKETING         = "MAR"
    ORG_TYPE_INSURANCE         = "INS"
    ORG_TYPE_INTERNAL          = "INT"
    ORG_TYPE_WORKCOMP          = "WKC"
    ORG_TYPE_HEATHCAREPROVIDER = "HCP"
    ORG_TYPE_CHOICES = (
        (ORG_TYPE_MARKETING        , "Marketing"          ), 
        (ORG_TYPE_INSURANCE        , "Insurance"          ), 
        (ORG_TYPE_INTERNAL         , "Internal"           ), 
        (ORG_TYPE_WORKCOMP         , "Work comp."         ), 
        (ORG_TYPE_HEATHCAREPROVIDER, "Healthcare Provider")
    )
    org_name = models.CharField(                   
        "Group Name", max_length=254, unique=True, blank=False, null=True)
    org_type = models.CharField(
        "Group Type", max_length=3, choices=ORG_TYPE_CHOICES, blank=True)
    org_contact_name = models.CharField(
        "Contact name", max_length=254, blank=True, null=True)
    org_phone = PhoneNumberField("Phone", blank=True)
    org_email = models.EmailField("Email address", max_length=254, blank=True)
    org_special = models.BooleanField("Special type", default=False)

    def get_absolute_url(self):
        return reverse('add-organization')

    def __str__(self):
        return self.org_name

    def get_referring_entity(self):
        referring_entitys_sort = self.ReferringEntity.filter().extra(
            select={'lower_entity_name': 'lower(entity_name)'}
            ).order_by('lower_entity_name')
        return referring_entitys_sort


class ReferringEntity(TrackedModel):
    """
    A ReferringEntity works for an Organization; clinic, hospital, private practice...
    Other patient_visit types for example; Other patient, google adds, website.....
    If entity_special==True then only require entity_name but call it "PatientVisit source"
    """
    organization = models.ForeignKey(
        Organization, related_name="ReferringEntity",verbose_name="Group")
    entity_name = models.CharField(
        "Name", max_length=254, unique=True, blank=False, null=True)   
    entity_title = models.CharField("Title", max_length=50, blank=True)    
    entity_phone = PhoneNumberField("Phone", blank=True)
    entity_email = models.EmailField(
        "Email address", max_length=254, blank=True)
    entity_special = models.BooleanField("Special type", default=False)

    def __str__(self):
        return self.entity_name

    def get_patient_visit(self, params):
        today = params['to_date']
        week_ago = params['from_date']
        patient_visit_sort = self.PatientVisit.filter(visit_date__range=(str(week_ago), str(today))).values('visit_date').annotate(visit=Sum('visit_count')).order_by('-visit_date')
        return patient_visit_sort
        
class TreatingProvider(TrackedModel):
    PROVIDER_TYPE_PHYSICIAN_ASSISTANT = "PA"
    PROVIDER_TYPE_DOCTOR              = "D"
    PROVIDER_TYPE_NURSE               = "N"
    PROVIDER_TYPE_NURSE_PRACTITIONER  = "NP"
    PROVIDER_TYPE_CHOICES = (
        (PROVIDER_TYPE_PHYSICIAN_ASSISTANT, "Physician Assistant"),
        (PROVIDER_TYPE_DOCTOR             , "Doctor"),
        (PROVIDER_TYPE_NURSE              , "Nurse"),
        (PROVIDER_TYPE_NURSE_PRACTITIONER , "Nurse Practitioner"),
    )
    provider_name = models.CharField(
        "Name", max_length=254, unique=True, blank=False, null=True)   
    provider_title = models.CharField("Title", max_length=50, blank=True)
    provider_type = models.CharField(
        "Provider Type", max_length=2, choices=PROVIDER_TYPE_CHOICES, blank=True)
    
    def __str__(self):
        return self.provider_name


class PatientVisit(TrackedModel):
    """
    PatientVisit is a patient visit referred to the clinic from a "ReferringEntity" that is part of an "Organization"
    Not sure how to do the multiple ForeignKey or if that is right.
    """
    referring_entity = models.ForeignKey(
        ReferringEntity, related_name="PatientVisit",verbose_name="Referring Entity")
    treating_provider = models.ForeignKey(
        TreatingProvider, related_name="TreatingProvider",verbose_name="Treating Provider", null=True)
    visit_date = models.DateField("Visit Date", default=date.today)
    visit_appointment_time = models.TimeField("Appointment Time", blank=True, null=True, default=None)
    visit_actual_time = models.TimeField("Actual Time", blank=True, null=True, default=None)
    visit_count = models.IntegerField("Visit Count", default=1)

    def __str__(self):
        return self.referring_entity.organization.org_name

class EmailReport(models.Model):
    """EmailReport for each referring_entity"""
    month = models.IntegerField("month")
    year = models.IntegerField("year")
    is_sent = models.BooleanField("sent", default=False)

    def __str__(self):
        return str(self.month)+" "+str(self.year)

class ThankyouMails(models.Model):
    """
    Mail will be send to ReferringEntity at end-of-the-day
    having month and year patient_visits count
    """
    referring_entity = models.ForeignKey(ReferringEntity, related_name="thankyou_mail")
    emailreport = models.ForeignKey(EmailReport, related_name="email_report", default=1)
    month_referrals = models.IntegerField("Month-PatientVisits")
    year_referrals = models.IntegerField("Year-PatientVisits")
    active = models.BooleanField("approve", default=False)

    def __str__(self):
        return str(self.referring_entity)
