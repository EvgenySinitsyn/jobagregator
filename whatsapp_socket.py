import asyncio
import pprint

import websockets
import json
import jwt
from config import CONFIG
from base import User, WhatsappInstance, WhatsappMessage, WhatsappSubscriber, WhatsappUserSubscriber
from green_api import GreenApi


not_logged_users = set()
user_websockets = {}
whatsapp_listeners = {}

SECRET_KEY = CONFIG.get('secret_key')
ALGORITHM = "HS256"


def check_text_message(obj):
    body = obj.get('body')
    if not body:
        return False
    message_data = body.get('messageData')
    if not message_data:
        return
    if not message_data.get('typeMessage') == 'textMessage':
        return False
    return True


async def clean_user(user_id, websocket):
    del user_websockets[user_id]
    if websocket in whatsapp_listeners:
        whatsapp_listeners[websocket].cancel()
        try:
            await whatsapp_listeners[websocket]
        except asyncio.CancelledError:
            pass
        del whatsapp_listeners[websocket]


async def handler(websocket):
    async def check_notification(green_api, user_id):
        try:
            nonlocal logged_in
            if not logged_in:
                while user_id in not_logged_users:
                    notification = await green_api.receive_notification()
                    if notification:
                        await green_api.delete_notification(notification.get('receiptId'))
                        if notification.get('body').get('stateInstance') == 'authorized':

                            for user_websocket in user_websockets[user_id]:
                                logged_message = {
                                    'type': 'whatsapp logged',
                                }
                                await user_websocket.send(json.dumps([logged_message]))
                            not_logged_users.remove(user_id)
                            return
            else:
                print('logged')
                while True:
                    instance = WhatsappInstance.get_by_logged_user(user_id)
                    if not instance:
                        await clean_user(user_id, websocket)
                        return
                    print('check notifications logged')
                    notification = await green_api.receive_notification()
                    if notification:
                        await green_api.delete_notification(notification.get('receiptId'))
                        if not check_text_message(notification):
                            continue
                        try:
                            phone = notification['body']['senderData']['chatId'].split('@')[0]
                            name = notification['body']['senderData']['chatName']
                            income_message = {
                                'user_id': user_id,
                                'subscriber_phone': int(phone),
                                'subscriber_name': name,
                                'text': notification['body']['messageData']['textMessageData']['textMessage'],
                                'type': WhatsappMessage.TYPE_INCOMING,
                            }
                            whatsapp_subscriber = WhatsappSubscriber.add(phone, name)
                            WhatsappUserSubscriber.add(user_id, whatsapp_subscriber.id)
                            WhatsappMessage.add(**income_message)
                            for user_websocket in user_websockets[user_id]:
                                await user_websocket.send(json.dumps([income_message]))
                        except Exception as ex:
                            print(ex)

        except Exception as ex:
            print(ex)

    async def send_qr(green_api, user_id):
        while user_id in not_logged_users:
            qr = await green_api.get_qr()
            if qr.get('type') == 'alreadyLogged':
                return
            for user_websocket in user_websockets[user_id]:
                try:
                    print(f'send qr to {user_websocket}')
                    print(qr)
                    await user_websocket.send(json.dumps([qr]))
                    await asyncio.sleep(1)
                except Exception as ex:
                    user_websockets[user_id].remove(user_websocket)

    try:
        async for message in websocket:
            data = json.loads(message)
            token = data.get('access_token')

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            username = payload.get("sub")
            user = User.get_by_username(username)
            if not user:
                return
            instance = WhatsappInstance.get_by_logged_user(user.id)
            if not instance:
                instance = WhatsappInstance.set_user(user.id)
                if not instance:
                    return
                green_api = GreenApi(instance.instance_id, instance.instance_token)
                not_logged_users.add(user.id)
                logged_in = False
                if user.id in user_websockets:
                    print('ERROR')
                    if websocket not in user_websockets[user.id]:

                        user_websockets[user.id].append(websocket)
                else:
                    user_websockets[user.id] = [websocket]
                    qr_task = asyncio.create_task(send_qr(green_api, user.id))
                    whatsapp_listeners[websocket] = asyncio.create_task(check_notification(green_api, user.id))
                    await qr_task
                    print('login')
                    WhatsappInstance.login_user(user.id)

                    if user.id in user_websockets:
                        if websocket not in user_websockets[user.id]:
                            user_websockets[user.id].append(websocket)
                        else:
                            logged_in = True
                            user_websockets[user.id] = [websocket]
                            whatsapp_listeners[websocket] = asyncio.create_task(check_notification(green_api, user.id))

            else:
                logged_in = True
                if data.get('type') == WhatsappMessage.TYPE_OUTGOING:
                    outgoing_message = {
                        'user_id': user.id,
                        'subscriber_phone': data.get('subscriber_phone'),
                        'subscriber_name': data.get('subscriber_name'),
                        'text': data.get('text'),
                        'type': WhatsappMessage.TYPE_OUTGOING,
                    }
                    whatsapp_subscriber = WhatsappSubscriber.add(data.get('subscriber_phone'), data.get('subscriber_name'))
                    WhatsappUserSubscriber.add(user.id, whatsapp_subscriber.id)
                    WhatsappMessage.add(**outgoing_message)
                green_api = GreenApi(instance.instance_id, instance.instance_token)
                if user.id in user_websockets:
                    if websocket not in user_websockets[user.id]:
                        user_websockets[user.id].append(websocket)
                else:
                    user_websockets[user.id] = [websocket]
                    whatsapp_listeners[websocket] = asyncio.create_task(check_notification(green_api, user.id))
                await green_api.send_message(79857848287, data.get('text'))

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as ex:
        print(ex)
    finally:
        if websocket in whatsapp_listeners:
            if user.id in user_websockets and websocket in user_websockets[user.id]:
                user_websockets[user.id].remove(websocket)
                print(f"canceled not all")
                print(user_websockets[user.id])

            if not user_websockets[user.id]:
                del user_websockets[user.id]
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
