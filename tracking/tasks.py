from __future__ import absolute_import

from datetime import date
from django.core.mail import send_mail
from celery.decorators import periodic_task
from celery.schedules import crontab
from django.db.models import Sum
from Practice_Referral import settings
from django.template.loader import render_to_string
from tracking.models import Agent, ThankyouMails, EmailReport, LAST_MONTH, LAST_12_MONTH

@periodic_task(run_every=crontab(minute=0, hour=0))
def thankyou_insertion_cron():
    """
    thankyou_cron will be called at specific time(at end of the every miniut)
    to insert data of last month and year
    python manage.py celeryd -B -l info
    """
    print ('Thankyou-cron')
    today_date = date.today()

    year_count = Agent.objects.filter(PatientVisit__visit_date__range=[LAST_12_MONTH,LAST_MONTH]).annotate(
        total_visits=Sum('PatientVisit__visit_count')).order_by('-total_visits')
    month_count = Agent.objects.filter(PatientVisit__visit_date__month=today_date.month-1,
        PatientVisit__visit_date__year=today_date.year).annotate(
        total_visits=Sum('PatientVisit__visit_count')).order_by('-total_visits')
    agents = Agent.objects.all()

    if agents:
        for agent in agents:
            email = EmailReport.objects.get_or_create(month=today_date.month-1, year=today_date.year)

            month_ = month_count.filter(agent_name=agent.agent_name)
            year_ = year_count.filter(agent_name=agent.agent_name)
            try:
                thank = ThankyouMails.objects.get(agent=agent, emailreport=email)
            except ThankyouMails.DoesNotExist:
                thank = ThankyouMails()
                thank.agent=agent
            if month_:
                thank.month_referrals = month_[0].total_visits
            if year_:
                thank.year_referrals = year_[0].total_visits
            thank.emailreport = email[0]
            thank.save()


@periodic_task(run_every=crontab(0, 0, day_of_month='1'))
def send_mail_cron():
    """
    thankyou_cron will be called at specific time(at the end of the every month)
    python manage.py celeryd -B -l info
    """
    print ('send mail-cron')
    agents = Agent.objects.all()
    today_date = date.today()
    last_month = date(today_date.year, today_date.month-1, today_date.day)

    for agent in agents:
        get_phy = ThankyouMails.objects.filter(agent=agent, emailreport__month=last_month.month,
            emailreport__year=today_date.year, emailreport__is_sent=False)
        if get_phy:
            subject = "Patient refferal status"
            email = agent.agent_email

            ctx = {
              'month_count':get_phy[0].month_referrals,
              'year_count':get_phy[0].year_referrals,
              'name':get_phy[0].agent.agent_name,
              'last_month':last_month.strftime('%B'),
              'last_year':today_date.year-1,
            }

            html = render_to_string("tracking/email_content.html",ctx)
            send_mail(subject,html, settings.DEFAULT_EMAIL_FROM, [email,], fail_silently=True)
            get_phy[0].is_sent = True
            get_phy[0].save()
