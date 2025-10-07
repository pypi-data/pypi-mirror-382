class OAuth2:
    def __init__(self, client):
        self.client = client

    def get_access_token(self, code, redirect_uri, client_id, client_secret):
        return self.client.request('POST', '/oauth2/token', {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        })

    def get_profile(self, access_token):
        return self.client.request('GET', '/oauth2/profile', {}, {
            'AccessToken': access_token
        })
