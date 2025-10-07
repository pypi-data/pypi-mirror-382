class User:
    def __init__(self, client):
        self.client = client

    def login(self, email_or_username, password, send_email=False):
        return self.client.request('POST', '/user/login', {
            'emailOrUsername': email_or_username,
            'password': password,
            'sendEmail': 'true' if send_email else 'false'
        }, {'Content-Type': 'application/json'})

    def revoke_secret(self, email_or_username, password, secret):
        return self.client.request('DELETE', '/user/login', {
            'emailOrUsername': email_or_username,
            'password': password,
            'secret': secret
        })
