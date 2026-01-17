from email_service import EmailService
import os
from dotenv import load_dotenv

def test_gmail():
    load_dotenv()
    print(f"Тестируем подключение для: {os.getenv('EMAIL_USER')}")
    
    service = EmailService()
    # Пробуем отправить тестовое письмо самому себе
    result = service.send_email(
        recipient_email=os.getenv('EMAIL_USER'),
        subject="Тестовое письмо от бота",
        body="Если вы видите это письмо, значит Gmail настроен верно!"
    )
    print(result)

if __name__ == "__main__":
    test_gmail()
