import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import CONFIG

# Настройки SMTP
smtp_host = 'smtp.mail.ru'
smtp_port = 465
username = CONFIG.get('email')
password = CONFIG.get('mailru_password')

print('start')
# Создание сообщения
msg = MIMEMultipart()
msg['From'] = username
msg['To'] = 'evg3nysinitz@yandex.ru'
msg['Subject'] = 'Тест jobagregator'
print('set')
body = 'Это типа письмо от jobagregator 123'
msg.attach(MIMEText(body, 'plain'))

# Подключение к SMTP-серверу
server = smtplib.SMTP_SSL(smtp_host, smtp_port)
server.ehlo()
# server.starttls()\
print(username)
print(password)
print('ok')
server.login(username, password)
print('ok1')
# Отправка сообщения
text = msg.as_string()
server.sendmail(username, 'evg3nysinitz@yandex.ru', text)

# Закрытие соединения
server.quit()

print("Письмо отправлено успешно!")