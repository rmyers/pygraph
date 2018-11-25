import json

from django import http
from django.views import View

from .models import PreferenceController


class PreferenceAPI(View):

    def respond_with_error(
        self,
        error_message: str = 'Unknown Error',
        data: dict = None,
        status: int = 400,
    )-> http.HttpResponse:
        try:
            response = json.dumps({
                'data': data,
                'errors': [
                    {'error': f'{error_message}'}
                ]
            })
        except json.decoder.JSONDecodeError:
            # log something here to record it as this should not happen
            message = 'Unknown Error: Problem with error message formatting'
            return self.respond_with_error(error_message=message)
        return http.HttpResponse(
            response,
            content_type='application/json',
            status=status,
        )

    def get_auth_token(self) -> str:
        auth_token = self.request.META.get('HTTP_X_AUTH_TOKEN')
        if auth_token is None:
            return self.respond_with_error(
                error_message='Missing Auth Token',
                status=403,
            )
        return auth_token

    def get(self, request: http.HttpRequest, site: str) -> http.HttpResponse:
        preferences = PreferenceController.get(
            auth_token=self.get_auth_token(),
            site_url=site,
        )

        preference_list = [
            {
                'site_url': p.site_url,
                'user_id': p.user_id,
                'kind': p.kind,
                'key': p.key,
                'value': p.value,
            }
            for p in preferences
        ]

        try:
            response = json.dumps({
                'data': {
                    'preferences': preference_list
                }
            })
        except json.decoder.JSONDecodeError:
            return self.respond_with_error('Unable to serialize JSON')
        return http.HttpResponse(
            response,
            content_type='application/json'
        )

    def post(self, request: http.HttpRequest, site: str) -> http.HttpResponse:
        key = None
        value = None

        try:
            data = json.loads(request.body)
            if not isinstance(data, dict):
                return self.respond_with_error('Unable to parse body.')

            key = data.get('key')
            value = data.get('value')

            if key is None:
                return self.respond_with_error('Body missing key attribute.')

            if value is None:
                return self.respond_with_error('Body missing value attribute.')

        except json.decoder.JSONDecodeError:
            return self.respond_with_error('Unable to parse JSON')
        except Exception:
            return self.respond_with_error()

        PreferenceController.update(
            auth_token=self.get_auth_token(),
            site_url=site,
            key=key,
            value=value,
        )
