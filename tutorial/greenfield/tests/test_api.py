
from django.test import TestCase

from pref.store import models


class PreferenceAPITests(TestCase):

    def test_api_returns_json_preferences_list(self):
        site = models.Site.objects.create(
            url='example.com',
            auth_url='identity.foo.com',
        )
        models.Kind.objects.create(
            site=site,
            kind='INTEGER',
            key='test-key',
            deprecated=False,
            value='1',
        )
        models.PreferenceController.update(
            auth_token='fake-token',
            site_url='example.com',
            key='test-key',
            value='42',
        )

        resp = self.client.get(
            '/api/v1/preference/example.com',
            HTTP_X_AUTH_TOKEN='fake-token',
        )

        self.assertEquals(resp.status_code, 200)

        expected = {
            'data': {
                'preferences': [
                    {
                        'site_url': site.url,
                        'kind': 'INTEGER',
                        'user_id': 'identity.foo.com',
                        'key': 'test-key',
                        'value': 42
                    }
                ]
            }
        }

        self.assertEqual(resp.json(), expected)
