import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, recipient_email, subject, body):
        if not self.user or not self.password:
            return "Ошибка: Учетные данные почты не настроены в .env"

        try:
            # Создаем сообщение
            message = MIMEMultipart()
            message["From"] = self.user
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            # Подключаемся к серверу и отправляем
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Шифрование
            server.login(self.user, self.password)
            server.send_message(message)
            server.quit()

            return "Письмо успешно отправлено!"
        except Exception as e:
            return f"Ошибка при отправке почты: {e}"
