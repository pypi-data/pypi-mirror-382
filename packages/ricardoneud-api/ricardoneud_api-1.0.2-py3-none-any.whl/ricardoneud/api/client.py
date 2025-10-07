import requests

class RicardoNeudAPI:
    def __init__(self, api_key=None, secret=None, base_url='https://api.ricardoneud.com', version='v4', timeout=30):
        self.api_key = api_key
        self.secret = secret
        self.base_url = f"{base_url}/{version}"
        self.timeout = timeout
        self.version = version
        from .games import Games
        from .tools import Tools
        from .reseller import Reseller
        from .user import User
        from .oauth2 import OAuth2
        self.games = Games(self)
        self.tools = Tools(self)
        self.reseller = Reseller(self)
        self.user = User(self)
        self.oauth2 = OAuth2(self)

    def _get_headers(self):
        headers = {}
        if self.secret:
            headers['Authorization'] = f"Bearer {self.secret}"
        elif self.api_key:
            headers['Basic'] = self.api_key
        return headers

    def request(self, method, endpoint, data=None, custom_headers=None):
        if data is None:
            data = {}
        if custom_headers is None:
            custom_headers = {}
        url = f"{self.base_url}{endpoint}"
        headers = {**self._get_headers(), **custom_headers}
        try:
            if method.upper() == 'GET':
                r = requests.get(url, headers=headers, params=data, timeout=self.timeout)
            elif method.upper() == 'POST':
                r = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            elif method.upper() == 'PUT':
                r = requests.put(url, headers=headers, json=data, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                r = requests.delete(url, headers=headers, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method {method}")
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"API Error: {r.text}") from e

    def set_version(self, version):
        self.version = version
        self.base_url = f"{self.base_url.rsplit('/', 1)[0]}/{version}"
        return self

    def set_api_key(self, api_key):
        self.api_key = api_key
        self.secret = None
        return self

    def set_secret(self, secret):
        self.secret = secret
        self.api_key = None
        return self
