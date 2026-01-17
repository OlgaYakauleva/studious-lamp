import os
import logging
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from llm_service import LLMService
from email_service import EmailService

# Загружаем переменные окружения
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Инициализируем сервисы
llm = LLMService()
email_bot = EmailService()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ответ на команду /start"""
    await update.message.reply_text(
        "Привет! Я AI помощник PROFftech.\n\n"
        "Я могу:\n"
        "1. Просто общаться.\n"
        "2. Отправлять письма через Gmail. Просто напиши: 'Отправь письмо на example@gmail.com с текстом Привет'"
    )

async def send_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /email <адрес> <текст>"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Использование: /email адрес@mail.com Текст письма")
        return
    
    recipient = context.args[0]
    body = " ".join(context.args[1:])
    
    await update.message.reply_text(f"Отправляю письмо на {recipient}...")
    result = email_bot.send_email(recipient, "Сообщение от Telegram-бота", body)
    await update.message.reply_text(result)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Интеллектуальная обработка сообщений через LLM"""
    user_text = update.message.text
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Резервный email для уведомлений
    admin_email = os.getenv("EMAIL_USER")
    
    # Системный промпт для классификации намерения
    system_prompt = (
        "Ты - диспетчер задач. Твоя цель - понять, что хочет пользователь.\n"
        "Если пользователь хочет отправить письмо (упоминает 'почту', 'email', 'отправь на...'), "
        "ответь строго в формате JSON: {\"action\": \"email\", \"recipient\": \"адрес\", \"body\": \"текст письма\"}.\n"
        "Если пользователь просто общается, ответь в формате JSON: {\"action\": \"chat\", \"answer\": \"твой ответ\"}.\n"
        "Если запрос непонятный или ты не знаешь как помочь, ответь JSON: {\"action\": \"unknown\"}."
    )
    
    classification_prompt = f"Запрос пользователя: '{user_text}'"
    
    try:
        # Используем LLM для принятия решения
        import json
        llm_response = llm.ask(f"{system_prompt}\n\n{classification_prompt}")
        
        # Пытаемся распарсить JSON (иногда LLM добавляет лишнее, поэтому чистим)
        json_str = re.search(r'\{.*\}', llm_response, re.DOTALL).group()
        data = json.loads(json_str)
        
        if data.get("action") == "email":
            recipient = data.get("recipient")
            body = data.get("body")
            
            # Если адрес не найден в тексте, но действие - email, пробуем найти регуляркой
            if not recipient or "@" not in recipient:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_text)
                recipient = email_match.group() if email_match else admin_email
            
            await update.message.reply_text(f"Принято! Отправляю письмо на {recipient}...")
            result = email_bot.send_email(recipient, f"Сообщение от {user_name} через AI помощник PROFftech", body)
            await update.message.reply_text(result)
            
        elif data.get("action") == "chat":
            await update.message.reply_text(data.get("answer"))
            
        else: # action == "unknown" или ошибка понимания
            error_msg = f"Пользователь {user_name} отправил непонятный запрос: {user_text}"
            await update.message.reply_text("Я не совсем понял ваш запрос, поэтому отправил уведомление администратору.")
            email_bot.send_email(admin_email, "Непонятный запрос в AI помощник PROFftech", error_msg)
            
    except Exception as e:
        print(f"Ошибка логики понимания: {e}")
        # Если всё сломалось - просто отвечаем через LLM как раньше
        response = llm.ask(user_text)
        await update.message.reply_text(response)

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token or token == "your_telegram_token_here":
        print("Ошибка: TELEGRAM_BOT_TOKEN не установлен в файле .env")
    else:
        application = ApplicationBuilder().token(token).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('email', send_email_command))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Бот запущен с функциями Gmail. Остановка: Ctrl+C")
        application.run_polling()
