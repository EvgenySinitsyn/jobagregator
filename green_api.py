import aiohttp


class GreenApi:
    green_api_url = 'https://1103.api.green-api.com'
    headers = {
        'Content-Type': 'application/json'
    }

    def __init__(self, instance_id, instance_token):
        self.instance_id = instance_id
        self.instance_token = instance_token

    async def get_qr(self):
        async with aiohttp.ClientSession() as session:
            url = f'{self.green_api_url}/waInstance{self.instance_id}/qr/{self.instance_token}'
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data

    async def receive_notification(self):
        async with aiohttp.ClientSession() as session:
            url = f'{self.green_api_url}/waInstance{self.instance_id}/receiveNotification/{self.instance_token}'
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data

    async def logout(self):
        async with aiohttp.ClientSession() as session:
            url = f'{self.green_api_url}/waInstance{self.instance_id}/logout/{self.instance_token}'
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data

    async def delete_notification(self, receipt_id):
        async with aiohttp.ClientSession() as session:
            url = f'{self.green_api_url}/waInstance{self.instance_id}/deleteNotification/{self.instance_token}/{receipt_id}'
            async with session.delete(url, headers=self.headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data

    async def send_message(self, phone, message):
        payload = {
            "chatId": f"{phone}@c.us",
            "message": message,
        }
        async with aiohttp.ClientSession() as session:
            url = f'{self.green_api_url}/waInstance{self.instance_id}/sendMessage/{self.instance_token}'
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data
