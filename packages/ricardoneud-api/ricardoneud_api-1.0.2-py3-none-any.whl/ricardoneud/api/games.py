class Games:
    def __init__(self, client):
        self.client = client

    def minecraft(self, address, port='25565'):
        return self.client.request('GET', '/games/minecraft/lookup', {}, {
            'X-Address': address,
            'X-Port': port
        })

    def fivem(self, address, port='30120'):
        return self.client.request('GET', '/games/fivem/lookup', {}, {
            'X-Address': address,
            'X-Port': port
        })
