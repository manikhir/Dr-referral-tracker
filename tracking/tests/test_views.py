from datetime import datetime, timedelta
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from tracking.models import Organization, Agent, PatientVisit


def date2str(d):
    '''convert date to string format like 2016-01-03 01:01:01'''
    return d.strftime('%Y-%m-%d %H:%M:%S')


class LoginBaseTest(TestCase):
    ''' a base class for testcases which need login '''

    def setUp(self):
        '''initial default user to be login in '''
        self.default_pass = 'pass1234'
        self.user = User.objects.create_user(username='user1',
                                             password=self.default_pass)

    def _login(self):
        ''' do login on client '''

        return self.client.post(reverse('user_login'),
                                {'username': self.user.username,
                                 'password': self.default_pass})


class IndexViewTest(LoginBaseTest):
    ''' testcases class for IndexView '''

    def test_no_login_get(self):
        ''' quantifiedcode: ignore it! '''

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        ''' quantifiedcode: ignore it! '''

        self._login()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        today = datetime.today().date()
        context = response.context
        self.assertEqual(len(context["agent_visit_sum"]), 0)
        self.assertEqual(len(context["org_visit_sum"]), 0)
        self.assertEqual(len(context["special_visit_sum"]), 0)
        self.assertEqual(len(context["patient_visits"]), 0)
        self.assertEqual(len(context["all_orgs"]), 0)
        self.assertEqual(context['today'], today)
        self.assertEqual(context['week_ago'], today - timedelta(days=7))

    def test_post_phyform(self):
        ''' quantifiedcode: ignore it! '''

        org = Organization.objects.create(org_name='org1')
        self._login()
        data = {
            'phyform': 'submit',
            'organization': org.id,
            'agent_name': 'phys1',
            'agent_phone': '+442083661177',
            'agent_email': 'test@email.com',
            'agent_special': 'on'
        }
        response = self.client.post(reverse('index'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        agents = Agent.objects.all()
        self.assertEqual(len(agents), 1)
        created_agent = agents[0]
        self.assertEqual(created_agent.organization, org)
        self.assertEqual(created_agent.agent_name,
                         data['agent_name'])
        self.assertEqual(created_agent.agent_phone,
                         data['agent_phone'])
        self.assertEqual(created_agent.agent_email,
                         data['agent_email'])
        self.assertEqual(created_agent.agent_special, True)

    def test_post_orgform(self):
        ''' quantifiedcode: ignore it! '''

        self._login()
        data = {
            'orgform': 'submit',
            'org_name': 'org1',
            'org_contact_name': 'contact1',
            'org_phone': '+442083661177',
            'org_email': 'test@email.com',
            'org_special': 'on'
        }
        response = self.client.post(reverse('index'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        organizations = Organization.objects.all()
        self.assertEqual(len(organizations), 1)
        created_org = organizations[0]
        self.assertEqual(created_org.org_name, data['org_name'])
        self.assertEqual(created_org.org_contact_name,
                         data['org_contact_name'])
        self.assertEqual(created_org.org_phone, data['org_phone'])
        self.assertEqual(created_org.org_email, data['org_email'])
        self.assertEqual(created_org.org_special, True)


class LogoutViewTest(LoginBaseTest):
    ''' testcases class for LogoutView '''

    def test_logout(self):
        ''' quantifiedcode: ignore it! '''

        self._login()
        response = self.client.get(reverse('index'))
        self.assertEqual(str(self.user.id),
                         self.client.session.get('_auth_user_id'))
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, '/')
        self.assertIsNone(self.client.session.get('_auth_user_id'))


class PatientVisitViewTest(LoginBaseTest):
    ''' testcases class for PatientVisitView '''

    def test_add_get_form(self):
        ''' quantifiedcode: ignore it! '''

        self._login()
        response = self.client.get(reverse('add-patient-visit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracking/patient_visit.html')

    def test_add_post_form(self):
        ''' quantifiedcode: ignore it! '''

        self._login()
        organization = Organization.objects.create(org_name='org1')
        agent = Agent.objects.create(
            agent_name='phys1', organization=organization)
        today = timezone.now()
        data = {
            'agent': agent.id,
            'visit_date': str(today.date()),
            'visit_count': 1,
            'patient_visit_date': str(today)
        }
        response = self.client.post(reverse('add-patient-visit'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('add-patient-visit'))
        patient_visits = PatientVisit.objects.all()
        self.assertEqual(len(patient_visits), 1)
        created_ref = patient_visits[0]
        self.assertEqual(created_ref.agent, agent)
        self.assertEqual(created_ref.visit_count, data['visit_count'])
        self.assertEqual(created_ref.visit_date, today.date())
        self.assertEqual(date2str(created_ref.patient_visit_date),
                         date2str(today))


class GetPatientVisitReportViewTest(LoginBaseTest):
    ''' testcases class for GetPatientVisitReportView '''

    def test_get(self):
        ''' quantifiedcode: ignore it! '''

        self._login()
        response = self.client.get(reverse('get-patient-visit-view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracking/show_patient_visit_report.html')


class GetPatientVisitHistoryViewTest(LoginBaseTest):
    ''' testcases class for GetPatientVisitHistoryView '''

    def test_get(self):
        ''' quantifiedcode: ignore it! '''

        self._login()
        response = self.client.get(reverse('patient-visit-history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'tracking/show_patient_visit_history.html')

    def test_post(self):
        ''' quantifiedcode: ignore it! '''

        organization = Organization.objects.create(org_name='org1')
        agent = Agent.objects.create(
            agent_name='phys1', organization=organization)
        today = datetime.now().date()
        patient_visits = [
            PatientVisit.objects.create(agent=agent,
                                    visit_date=today + timedelta(days=i))
            for i in range(10)]

        self._login()
        data = {
            'from_date': str(today),
            'to_date': str(today)
        }
        response = self.client.post(reverse('patient-visit-history'), data)
        context = response.context
        self.assertEqual(len(context['patient_visits']), 1)
        self.assertEqual(context['patient_visits'][0], patient_visits[0])

        data = {
            'from_date': str(today),
            'to_date': str(today+timedelta(days=len(patient_visits)))
        }
        response = self.client.post(reverse('patient-visit-history'), data)
        context = response.context
        self.assertEqual(len(context['patient_visits']), len(patient_visits))
        self.assertSetEqual({r.id for r in context['patient_visits']},
                            {r.id for r in patient_visits})


class EditAgentViewTest(LoginBaseTest):
    ''' testcases class for EditAgentView '''

    def test_edit(self):
        ''' quantifiedcode: ignore it! '''

        organization = Organization.objects.create(org_name='org1')
        agent = Agent.objects.create(
            agent_name='phys1', organization=organization,
            agent_email='test@email.com', agent_phone='+442083660000',
            agent_special=False)
        data = {
            'organization': organization.id,
            'agent_name': 'new_name',
            'agent_phone': '+442083661177',
            'agent_email': 'new_email@email.com',
            'agent_special': 'on'
        }
        response = self.client.post(
            reverse('edit-agent', args=(agent.id,)), data)
        self.assertEqual(response.status_code, 200)
        agent = Agent.objects.get(id=agent.id)
        self.assertEqual(agent.agent_name, data['agent_name'])
        self.assertEqual(agent.agent_phone, data['agent_phone'])
        self.assertEqual(agent.agent_email, data['agent_email'])
        self.assertEqual(agent.agent_special, True)


class EditOrganizationViewTest(LoginBaseTest):
    ''' testcases class for EditOrganizationView '''

    def test_edit(self):
        ''' quantifiedcode: ignore it! '''

        organization = Organization.objects.create(
            org_name='phys1', org_contact_name="contact1",
            org_email='test@email.com', org_phone='+442083660000',
            org_special=False)
        data = {
            'org_name': 'new_name',
            'org_contact_name': 'new_contact',
            'org_phone': '+442083661177',
            'org_email': 'new_email@email.com',
            'org_special': 'on'
        }
        response = self.client.post(
            reverse('edit-organization', args=(organization.id,)), data)
        self.assertEqual(response.status_code, 200)
        organization = Organization.objects.get(id=organization.id)
        self.assertEqual(organization.org_name, data['org_name'])
        self.assertEqual(organization.org_contact_name,
                         data['org_contact_name'])
        self.assertEqual(organization.org_phone, data['org_phone'])
        self.assertEqual(organization.org_email, data['org_email'])
        self.assertEqual(organization.org_special, True)
