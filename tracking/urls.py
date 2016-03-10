from django.conf.urls import patterns, include, url
from tracking.views import *


urlpatterns = patterns(
    '',
    url(r'^logout/$',LogoutView.as_view(), name="logout"),
    url(r'^home/$', IndexView.as_view(), name="index"),
    url(r'^add/organization/$', OrganizationView.as_view(), name="add-organization"),
    url(r'^add/agent/$', AgentView.as_view(), name="add-agent"),
    url(r'^add/doctor/$', DoctorView.as_view(), name="add-doctor"),
    url(r'^add/patient_visit/$', PatientVisitView.as_view(), name="add-patient-visit"),
    url(r'^add/get-patient-visit-view/$', GetPatientVisitReport.as_view(), name="get-patient-visit-view"),
    url(r'^patient-visit-history/$', GetPatientVisitHistory.as_view(), name="patient-visit-history"),
    url(r'^edit/agent/([0-9]+)/$', edit_agent, name="edit-agent"),
    url(r'^edit/organization/([0-9]+)/$', edit_organization, name="edit-organization"),
    url(r'^edit/doctor/([0-9]+)/$', edit_doctor, name="edit-doctor"),
    url(r'^view/organizations/$', OrganizationListView.as_view(), name="view-organizations"),
    url(r'^view/agents/$', AgentListView.as_view(), name="view-agents"),
    url(r'^view/doctors/$', DoctorListView.as_view(), name="view-doctors"),
    url('', include('social.apps.django_app.urls', namespace='social')),

)
