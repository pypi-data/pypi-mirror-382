class Tools:
    def __init__(self, client):
        self.client = client

    def dns_check(self, domain, record_type):
        return self.client.request('GET', '/tools/dnscheck', {}, {
            'X-Domain': domain,
            'X-Record-Type': record_type
        })

    def domain_check(self, domain):
        return self.client.request('GET', '/tools/domaincheck', {}, {
            'X-Domain': domain
        })

    def mail_check(self, domain, dkim_selector=None):
        headers = {'X-Domain': domain}
        if dkim_selector:
            headers['X-DKIM-Selector'] = dkim_selector
        return self.client.request('GET', '/tools/mailcheck', {}, headers)

    def mail_host_check(self, domain, dkim_selector=None):
        headers = {'X-Domain': domain}
        if dkim_selector:
            headers['X-DKIM-Selector'] = dkim_selector
        return self.client.request('POST', '/tools/mailhostcheck', {}, headers)

    def subdomain_finder(self, domain):
        return self.client.request('GET', '/tools/subdomainfinder', {}, {
            'X-Domain': domain
        })

    def geo_ip(self, ip):
        return self.client.request('GET', '/tools/geo-ip', {}, {
            'X-IP': ip
        })
