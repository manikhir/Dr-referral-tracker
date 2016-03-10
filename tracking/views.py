from .forms import *
from django.views.generic import View, TemplateView, ListView
from django.views.generic.edit import FormView

import calendar
from django.db.models import Sum,Count
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from datetime import datetime , timedelta, date
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from tracking.models import PatientVisit, Agent, Organization, LAST_MONTH, LAST_12_MONTH
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from tracking.templatetags.visite_counts import get_organization_counts, \
    get_organization_counts_month_lastyear, get_organization_counts_year, \
    get_organization_counts_year_lastyear
from Practice_Referral.settings import TIME_ZONE


class IndexView(View):
    # display the Organization form
    # template_name = "index.html"
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        orgform = OrganizationForm()
        phyform = AgentForm()
        refform = PatientVisitForm()

        today_date = datetime.now().date()
        start_date = today_date - timedelta(days=365)
        end_date = today_date - timedelta(days=1)

        agent_visit_sum = Agent.objects.filter(
            Referral__visit_date__range=(start_date,end_date)).annotate(
            total_visits=Sum('Referral__visit_count')
            ).order_by('-total_visits')[:10]

        org_visit_sum =  Organization.objects.filter(
            Agent__Referral__visit_date__range=(start_date,end_date)).annotate(
            total_org_visits=Sum('Agent__Referral__visit_count')
            ).order_by('-total_org_visits')[:5]

        special_visit_sum =  Organization.objects.filter(org_special=True).filter(
            Agent__Referral__visit_date__range=(start_date,end_date)).annotate(
            total_org_special_visits=Sum('Agent__Referral__visit_count')
            ).order_by('-total_org_special_visits')[:5]

        patient_visits = PatientVisit.objects.filter(visit_date__range=[LAST_12_MONTH,LAST_MONTH])

        if patient_visits:
            try:
                patient_visits = patient_visits.extra(select={'month': 'STRFTIME("%m",visit_date)'})
                print (patient_visits[0].month)
            except:
                patient_visits = patient_visits.extra(select={'month': 'EXTRACT(month FROM visit_date)'})
            patient_visits = patient_visits.values('month').annotate(total_visit_count=Sum('visit_count'))

            for patient_visit in patient_visits:
                if LAST_MONTH.month <= int(patient_visit['month']) :
                    current_month = date(day=LAST_MONTH.day, month= int(patient_visit['month']), year=LAST_MONTH.year)
                else:
                    current_month = date(day=LAST_12_MONTH.day, month= int(
                        patient_visit['month']), year=LAST_12_MONTH.year)

                last_month = current_month-timedelta(days=364)
                patient_visits_year = PatientVisit.objects.filter(
                    visit_date__range=[last_month, current_month]).aggregate(year_total=Sum('visit_count'))
                patient_visit['year_total'] = patient_visits_year['year_total']
                patient_visit['year_from'] = last_month
                patient_visit['year_to'] = current_month
        today = date.today()
        week_ago = today - timedelta(days=7)
        all_orgs = Agent.objects.order_by('agent_name')
        all_ref = {}
        for phys in all_orgs :
            phys_ref = phys.get_patient_visits({'from_date' : week_ago, 'to_date' : today});
            if phys_ref.count() :
                for ref in phys_ref :
                    if not phys.id in all_ref :
                        all_ref[phys.id] = {'name' : phys.agent_name, 'refs' :  [ ref ] }
                    else :
                        all_ref[phys.id]['refs'].append(ref)

        ctx = {
            "orgform": orgform,
            "phyform": phyform,
            "refform": refform,
            "agent_visit_sum": agent_visit_sum,
            "org_visit_sum": org_visit_sum,
            "special_visit_sum": special_visit_sum,
            "patient_visits":patient_visits,
            "all_orgs" : all_ref,
            'today': today,
            'week_ago' : week_ago,
            'timezone': TIME_ZONE,
            }
        return render(request,"index.html",ctx )

    def post(self, request, *args, **kwargs):

        phyform = AgentForm()
        orgform = OrganizationForm()
        refform = PatientVisitForm()

        if 'phyform' in request.POST:
            phyform = AgentForm(request.POST)
            if phyform.is_valid():
                phyform.save()
                return redirect(reverse('index'))

        elif 'orgform' in request.POST:
            orgform = OrganizationForm(request.POST)
            if orgform.is_valid():
                orgform.save()
                return redirect(reverse('index'))

        elif 'refform' in request.POST:
            refform = PatientVisitForm(request.POST)
            if refform.is_valid():
                refform.save()
                return redirect(reverse('index'))

        ctx = {
            "orgform": orgform,
            "phyform": phyform,
            "refform": refform,
            'timezone': TIME_ZONE,
          }

        return render(request,"index.html",ctx )

class OrganizationView(View):
    # display the Organization form
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = OrganizationForm()
        ctx = {"form": form}
        return render(request,"tracking/organization.html",ctx )

    def post(self, request, *args, **kwargs):
        form = OrganizationForm(request.POST)
        ctx = {"form": form}
        if form.is_valid():
            form.save()
            return redirect(reverse('add-agent'))

        return render(request,"tracking/organization.html",ctx )


class AgentView(View):
    # display the agent form
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = AgentForm()
        ctx = {"form": form}
        return render(request,"tracking/agent.html",ctx )


    def post(self, request, *args, **kwargs):
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            form = AgentForm()

        ctx = {"form": form}
        return render(request,"tracking/agent.html",ctx )
        
class DoctorView(View):
    # display the doctor form
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = DoctorForm()
        ctx = {"form": form}
        return render(request,"tracking/doctor.html",ctx )


    def post(self, request, *args, **kwargs):
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            form = DoctorForm()

        ctx = {"form": form}
        return render(request,"tracking/doctor.html",ctx )        


class PatientVisitView(View):
    # display the patient_visit form
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = PatientVisitForm()
        ctx = {"form": form, 'timezone': TIME_ZONE}
        return render(request,"tracking/patient_visit.html",ctx )

    def post(self, request, *args, **kwargs):
        form = PatientVisitForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add/patient_visit/')
        ctx = {"form": form, 'timezone': TIME_ZONE}
        return render(request,"tracking/patient_visit.html",ctx )

class GetPatientVisitReport(View):
    """
    Display a summary of patient_visits by Organization:provider:
    """
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        all_orgs = Organization.objects.all().order_by('org_name')
        today = datetime.now().date()
        last_year = today.year - 1
        orgs_counts = {}
        total_counts = dict(counts=0, counts_month_lastyear=0,
                            counts_year=0, counts_year_lastyear=0)
        for org in all_orgs:
            counts = get_organization_counts(org)
            counts_month_lastyear = get_organization_counts_month_lastyear(org)
            counts_year = get_organization_counts_year(org)
            counts_year_lastyear = get_organization_counts_year_lastyear(org)
            orgs_counts[org.id] = dict(
                counts=counts,
                counts_month_lastyear=counts_month_lastyear,
                counts_year=counts_year,
                counts_year_lastyear=counts_year_lastyear,
            )
            total_counts['counts'] += counts
            total_counts['counts_month_lastyear'] += counts_month_lastyear
            total_counts['counts_year'] += counts_year
            total_counts['counts_year_lastyear'] += counts_year_lastyear

        ctx = {
                'all_orgs': all_orgs,
                'last_year': last_year,
                'orgs_counts': orgs_counts,
                'total_counts': total_counts
            }
        return render(request, "tracking/show_patient_visit_report.html", ctx)


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return redirect('/')

class GetPatientVisitHistory(View):
    """
    Display a summary of patient_visits by Date:Agent:Organization:Count:
    """
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        today = date.today()
        patient_visits = PatientVisit.objects.filter(visit_date=today).order_by('-visit_date')
        form = PatientVisitHistoryForm(initial={'from_date': today, 'to_date' : today})
        ctx = {
                'patient_visits': patient_visits,
                'timezone': TIME_ZONE,
                "form": form
            }
        return render(request,"tracking/show_patient_visit_history.html",ctx )


    def post(self, request, *args, **kwargs):

        form = PatientVisitHistoryForm(request.POST)
        if form.is_valid():
            cleaned_data = form.clean()
            patient_visits = PatientVisit.objects\
                .filter(visit_date__gte=cleaned_data['from_date'])\
                .filter(visit_date__lte=cleaned_data['to_date'])\
                .order_by('-visit_date')
            if cleaned_data['agent']:
                patient_visits = patient_visits.filter(agent__in=cleaned_data['agent'])
        else:
            patient_visits = []

        ctx = {
            'patient_visits': patient_visits,
            'timezone': TIME_ZONE,
            "form": form
        }
        return render(request,"tracking/show_patient_visit_history.html",ctx )

def edit_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            return render(request, 'tracking/organization_edit.html', {
                'form': form,
                'success': True})

    else:
        form = OrganizationForm(instance=organization)

    return render(request, 'tracking/organization_edit.html', {'form': form})
    
def edit_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            return render(request, 'tracking/agent_edit.html', {
                'form': form,
                'success': True})

    else:
        form = AgentForm(instance=agent)

    return render(request, 'tracking/agent_edit.html', {'form': form})    
    
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return render(request, 'tracking/doctor_edit.html', {
                'form': form,
                'success': True})

    else:
        form = DoctorForm(instance=doctor)

    return render(request, 'tracking/doctor_edit.html', {'form': form})    

class OrganizationListView(ListView):
    model = Organization
    template_name = 'tracking/organization_list.html'
    context_object_name = "organizations"
    paginate_by = 10

class AgentListView(ListView):
    model = Agent
    template_name = 'tracking/agent_list.html'
    context_object_name = "agents"
    paginate_by = 10
    
class DoctorListView(ListView):
    model = Doctor
    template_name = 'tracking/doctor_list.html'
    context_object_name = "doctors"
    paginate_by = 10    
