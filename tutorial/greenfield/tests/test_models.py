from django.test import TestCase

from pref.store import models


class PreferenceControllerTest(TestCase):

    def test_update_returns_new_preference(self):
        site = models.Site.objects.create(
            url='example.com',
            auth_url='identity.foo.com',
        )
        models.Kind.objects.create(
            site=site,
            kind='STRING',
            key='test-key',
            deprecated=False,
            value='test-default',
        )

        actual = models.PreferenceController.update(
            auth_token='fake-token',
            site_url='example.com',
            key='test-key',
            value='custom_value',
        )

        expected = models.Preference(
            site_url='example.com',
            user_id='identity.foo.com',
            kind='STRING',
            key='test-key',
            value='custom_value',
        )

        self.assertEqual(actual, expected)

    def test_get_returns_preference_list(self):
        site = models.Site.objects.create(
            url='example.com',
            auth_url='identity.foo.com',
        )
        models.Kind.objects.create(
            site=site,
            kind='STRING',
            key='test-key',
            deprecated=False,
            value='test-default',
        )
        models.PreferenceController.update(
            auth_token='fake-token',
            site_url='example.com',
            key='test-key',
            value='custom_value',
        )

        actual = models.PreferenceController.get(auth_token='fake', site_url=site.url)

        expected = [
            models.Preference(
                site_url='example.com',
                user_id='identity.foo.com',
                kind='STRING',
                key='test-key',
                value='custom_value',
            ),
        ]

        self.assertEqual(actual, expected)

    def test_update_removes_override_if_reset_to_default_for_key(self):
        site = models.Site.objects.create(
            url='example.com',
            auth_url='identity.foo.com',
        )
        models.Kind.objects.create(
            site=site,
            kind='STRING',
            key='test-key',
            deprecated=False,
            value='test-default',
        )

        count_before_initial_update = models.Override.objects.count()

        models.PreferenceController.update(
            auth_token='fake-token',
            site_url='example.com',
            key='test-key',
            value='custom_value',
        )

        count_after_initial_update = models.Override.objects.count()

        self.assertEquals(
            count_after_initial_update,
            count_before_initial_update + 1
        )

        models.PreferenceController.update(
            auth_token='fake-token',
            site_url='example.com',
            key='test-key',
            value='test-default',
        )

        count_after_reset_to_default = models.Override.objects.count()

        self.assertEquals(
            count_after_reset_to_default,
            count_before_initial_update
        )
