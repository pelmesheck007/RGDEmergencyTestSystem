import json
import requests
from kivy.network.urlrequest import UrlRequest
from kivy.logger import Logger


class APIClient:
    def __init__(self, base_url='http://your-api-domain.com/api/v1'):
        self.base_url = base_url
        self.token = None



    def get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def login(self, username, password, on_success, on_error):
        url = f"{self.base_url}/login"
        data = {
            'username': username,
            'password': password
        }

        def success(req, result):
            token = result.get('access_token')
            if token:
                self.set_token(token)
                on_success(result)
            else:
                on_error({'error': 'Invalid response'})

        def fail(req, error):
            Logger.error(f"API: Login failed - {error}")
            on_error(error)

        UrlRequest(
            url,
            on_success=success,
            on_failure=fail,
            on_error=fail,
            req_body=json.dumps(data),
            req_headers=self.get_headers()
        )

    def get_user_profile(self, on_success, on_error):
        url = f"{self.base_url}/users/me"

        def success(req, result):
            on_success(result)

        def fail(req, error):
            Logger.error(f"API: Profile fetch failed - {error}")
            on_error(error)

        UrlRequest(
            url,
            on_success=success,
            on_failure=fail,
            on_error=fail,
            req_headers=self.get_headers()
        )

    # Добавьте другие методы API по аналогии