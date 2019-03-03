import asyncio
import websockets
import requests
import logging

OAUTH_SERVICE_URL = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token=%s'

class QTClient:

    def __init__(self, refresh_token):
        auth_response = self.__initialize_auth_request(refresh_token)

        self.access_token = auth_response['access_token']
        self.refresh_token = auth_response['refresh_token']
        self.api_uri = auth_response['api_server']

    def __initialize_auth_request(self, refresh_token):
        r = requests.get(OAUTH_SERVICE_URL % refresh_token)
        return r.json()

    def __build_auth_header(self):
        auth = 'Bearer %s' % self.access_token
        return {'Authorization': auth}

    def get_account(self):
        request_url = '%sv1/%s' % (self.api_uri, 'accounts')
        r = requests.get(request_url, headers=self.__build_auth_header())
        return r.json()

    def get_account_positions(self, account_id):
        request_url = '%sv1/accounts/%s/positions' % (self.api_uri, account_id)
        r = requests.get(request_url, headers=self.__build_auth_header())
        return r.json()

    def get_security_information(self, symbol_id):
        request_url = '%sv1/symbols/%i' % (self.api_uri, symbol_id)
        r = requests.get(request_url, headers=self.__build_auth_header())
        return r.json()

    def get_streaming_port(self, symbol_ids):
        request_url = '%sv1/markets/quotes?ids=%s&stream=true&mode=WebSocket' % (self.api_uri, ",".join(symbol_ids))
        r = requests.get(request_url, headers=self.__build_auth_header())
        return r.json()['streamPort']
    
    def get_candles(self, symbol_id, start_time, end_time, interval):
        request_url = '%sv1/markets/candles/%s?startTime=%s&endTime=%s&interval=%s' % (self.api_uri, 
            symbol_id, start_time, end_time, interval)
        r = requests.get(request_url, headers=self.__build_auth_header())
        return r.json()

    async def consume(self, message):
        print(message)

    async def subscribe(self, symbol_id, fun):
        request_url = '%s:%i' % (self.api_uri[:-1], self.get_streaming_port(symbol_id))
        request_url = request_url.replace('https', 'wss')
        async with websockets.connect(request_url) as websocket:
            await websocket.send(self.access_token)
            async for message in websocket:
                await fun(message)