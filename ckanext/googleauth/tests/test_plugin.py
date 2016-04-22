import unittest

import ckan.tests.helpers as helpers

from ckanext.googleauth.plugin import email_to_ckan_user


class TestPlugin(unittest.TestCase):
    @helpers.change_config('ckan.googleauth_omit_domain_from_username',
                           'false')
    def test_user_name_is_email_with_underscores(self):
        email = 'alice_b@example.com'
        user_name = email_to_ckan_user(email)

        self.assertEqual(user_name, 'alice_b_example_com')

    @helpers.change_config('ckan.googleauth_omit_domain_from_username',
                           'true')
    def test_domain_omitted_with_config_option(self):
        email = 'alice.b@example.com'
        user_name = email_to_ckan_user(email)

        self.assertEqual(user_name, 'alice_b')
