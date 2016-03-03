from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.db import models
from .forms import RegistrationForm
from django.test import Client
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class UserTestCase(TestCase):
    """BASIC TESTS"""
    fixtures = ["tests.json"]
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.dummny_username="john"
        self.dummy_first_name="John"
        self.dummy_last_name="Albert"
        self.dummy_email="john@gmail.com"
        self.dummy_password="13245678"
        self.dummy_password2="13245678"

        self.sample_user = User.objects.create_user(username=self.dummny_username, first_name=self.dummy_first_name, last_name=self.dummy_last_name, password=self.dummy_password, email=self.dummy_email)

    def test_check_user_is_inactive(self):
        """ test for check new user is active or not """
        self.assertEqual(self.sample_user.is_active, False, 'New user is inactive')

    def test_make_new_user_active_by_admin(self):
        """ change new user to active """

        users = User.objects.filter(pk=self.sample_user.id).update(is_active=True, username="yogesh04")
        after_updation = User.objects.filter(pk=self.sample_user.id)
        self.assertEqual(after_updation[0].is_active, True, 'New user is active')

    def test_check_user_is_inactive(self):
        """ test for check new user is active or not """
        self.assertEqual(self.sample_user.is_active, True, 'New user is inactive')

