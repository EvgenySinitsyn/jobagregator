import asyncio
import pprint

import websockets
import json
import jwt
from config import CONFIG
from base import User, WhatsappInstance
import aiohttp

whatsapp_listeners = {}

SECRET_KEY = CONFIG.get('secret_key')
ALGORITHM = "HS256"


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


def check_text_message(obj):
    body = obj.get('body')
    if not body:
        return False
    message_data = body.get('messageData')
    if not message_data.get('typeMessage') == 'textMessage':
        return False
    return True


async def handler(websocket):
    async def check_notification(green_api, websocket):
        nonlocal logged_in
        if not logged_in:
            while not logged_in:
                notification = await green_api.receive_notification()
                if notification:
                    await green_api.delete_notification(notification.get('receiptId'))
                    if notification.get('body').get('stateInstance') == 'authorized':
                        logged_in = True
                        return
        else:
            while True:
                notification = await green_api.receive_notification()
                if notification:
                    await green_api.delete_notification(notification.get('receiptId'))
                    pprint.pprint(notification)
                    if not check_text_message(notification):
                        continue
                    income_message = {
                        'sender': notification['body']['senderData'],
                        'text': notification['body']['messageData'],
                    }
                    await websocket.send(json.dumps([income_message]))

    async def send_qr(green_api):
        logged = logged_in
        while not logged:
            qr = await green_api.get_qr()
            await websocket.send(json.dumps([qr]))
            await asyncio.sleep(1)
            logged = logged_in

    try:
        async for message in websocket:
            data = json.loads(message)
            token = data.get('access_token')

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            username = payload.get("sub")
            user = User.get_by_username(username)
            if not user:
                return
            instance = WhatsappInstance.get_by_user_id(user.id)
            if not instance:
                instance = WhatsappInstance.set_user(user.id)
                if not instance:
                    return
                green_api = GreenApi(instance.instance_id, instance.instance_token)

                logged_in = False
                qr_task = asyncio.create_task(send_qr(green_api))
                login_task = asyncio.create_task(check_notification(green_api, websocket))
                await login_task
                qr_task.cancel()
                try:
                    await qr_task
                except asyncio.CancelledError:
                    pass
                WhatsappInstance.login_user(user.id)

            else:
                logged_in = True

                green_api = GreenApi(instance.instance_id, instance.instance_token)
                print(whatsapp_listeners)
                if websocket not in whatsapp_listeners:
                    whatsapp_listeners[websocket] = asyncio.create_task(check_notification(green_api, websocket))
                await green_api.send_message(79857848287, data.get('text'))
                print(data.get('text'))

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        if websocket in whatsapp_listeners:
            whatsapp_listeners[websocket].cancel()
            try:
                await whatsapp_listeners[websocket]
            except asyncio.CancelledError:
                pass
            del whatsapp_listeners[websocket]
        print(f"canceled")


async def main():
    # Запускаем WebSocket-сервер
    start_server = websockets.serve(handler, 'localhost', 8081)

    # Запуск сервера
    async with start_server:
        print("Сервер запущен на ws://localhost:8081")
        await asyncio.Future()  # Блокируем выполнение


# Запускаем цикл событий
if __name__ == "__main__":
    asyncio.run(main())
