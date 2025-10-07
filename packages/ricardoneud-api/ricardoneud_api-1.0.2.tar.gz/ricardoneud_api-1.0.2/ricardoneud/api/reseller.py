class Reseller:
    def __init__(self, client):
        self.client = client

    def check_license(self, license_key):
        return self.client.request('GET', f"/reseller/{license_key}/check")

    def generate_license(self, data):
        headers = {
            'X-Registered-To': data['registeredTo'],
            'X-Domain-Or-IP': data['domainOrIp'],
            'X-Status': data['status'],
            'X-Product-Id': str(data['productId']),
            'X-Project-Id': str(data['projectId'])
        }
        return self.client.request('POST', '/reseller/licenses/generate', {}, headers)

    def update_license(self, license_key, data):
        headers = {}
        if 'registeredTo' in data:
            headers['X-Registered-To'] = data['registeredTo']
        if 'domainOrIp' in data:
            headers['X-Domain-Or-IP'] = data['domainOrIp']
        if 'status' in data:
            headers['X-Status'] = data['status']
        if 'productId' in data:
            headers['X-Product-Id'] = str(data['productId'])
        if 'projectId' in data:
            headers['X-Project-Id'] = str(data['projectId'])
        return self.client.request('PUT', f"/reseller/{license_key}/update", {}, headers)

    def delete_license(self, license_key):
        return self.client.request('DELETE', f"/reseller/{license_key}/delete")
