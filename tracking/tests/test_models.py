from django.test import TestCase
from datetime import datetime , timedelta, date

from tracking.models import Agent, PatientVisit, Organization


class OrganizationTest(TestCase):
    ''' a testcases class for Organization model '''

    def setUp(self):
        ''' setup initial objects '''

        self.organization = Organization.objects.create(org_name='org1')

    def test_get_agent_no_agent(self):
        ''' quantifiedcode: ignore it! '''

        self.assertEqual(self.organization.get_agent().count(), 0)

    def test_get_agent(self):
        ''' quantifiedcode: ignore it! '''

        Agent.objects.create(
            agent_name='phys1', organization_id=self.organization.id)
        self.assertEqual(self.organization.get_agent().count(), 1)

    def test_get_agent_sorting(self):
        ''' quantifiedcode: ignore it! '''

        p1 = Agent.objects.create(
            agent_name='phys2', organization_id=self.organization.id)
        p2 = Agent.objects.create(
            agent_name='Phys1', organization_id=self.organization.id)
        p3 = Agent.objects.create(
            agent_name='phys4', organization_id=self.organization.id)
        p4 = Agent.objects.create(
            agent_name='Phys3', organization_id=self.organization.id)
        agents = list(self.organization.get_agent().all())
        self.assertEqual(len(agents), 4)
        self.assertEqual(agents[0], p2)
        self.assertEqual(agents[-1], p3)


class AgentTest(TestCase):
    ''' a testcases class for Agent model '''

    def setUp(self):
        ''' setup initial objects '''

        self.organization = Organization.objects.create(org_name='org1')
        self.agent = Agent.objects.create(
            agent_name='phys1', organization_id=self.organization.id)

    def test_get_patient_visits_no_patient_visit(self):
        ''' quantifiedcode: ignore it! '''

        params = {
            'to_date': datetime.now().date(),
            'from_date': (datetime.now() - timedelta(days=1)).date()
        }

        self.assertEqual(self.agent.get_patient_visits(params).count(), 0)

    def test_get_patient_visits_today(self):
        ''' quantifiedcode: ignore it! '''

        agent2 = Agent.objects.create(
            agent_name='phys2', organization_id=self.organization.id)
        patient_visits = [PatientVisit.objects.create(agent=self.agent)
                     for _ in range(10)]
        not_related_patient_visit = PatientVisit.objects.create(agent=agent2)
        today = datetime.now().date()
        params = {
            'to_date': today,
            'from_date': today
        }
        p_patient_visits = self.agent.get_patient_visits(params).all()

        self.assertEqual(len(p_patient_visits), 1)
        self.assertEqual(p_patient_visits[0]['visit'], 10)
        self.assertEqual(p_patient_visits[0]['visit_date'], today)

    def test_get_patient_visits_10_days(self):
        ''' quantifiedcode: ignore it! '''

        today = datetime.now().date()
        patient_visits = [
            PatientVisit.objects.create(agent=self.agent,
                                    visit_date=today + timedelta(days=i))
            for i in range(10)]
        patient_visits.reverse()
        params = {
            'to_date': today + timedelta(days=10),
            'from_date': today
        }
        p_patient_visits = self.agent.get_patient_visits(params).all()

        self.assertEqual(len(p_patient_visits), 10)
        self.assertSetEqual({p['visit'] for p in p_patient_visits}, {1})
        self.assertListEqual([p['visit_date'] for p in p_patient_visits],
                             [r.visit_date for r in patient_visits])
