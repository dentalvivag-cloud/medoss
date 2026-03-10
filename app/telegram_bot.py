import telebot
import threading
from flask import current_app
from app.models import Appointment, Patient, Payment
from sqlalchemy import func
from datetime import date, datetime
import time

# Глобальный объект бота
bot = None

def get_bot():
    global bot
    if bot is None:
        # Важно: TELEGRAM_BOT_TOKEN должен быть в config.py
        token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        if token:
            bot = telebot.TeleBot(token)
    return bot

def notify_new_appointment(appt):
    """Отправка уведомления о новой записи (Закон №38)"""
    tb = get_bot()
    chat_id = current_app.config.get('TELEGRAM_CHAT_ID')
    if not tb or not chat_id: return

    msg = (f"🆕 *НОВАЯ ЗАПИСЬ*\n"
           f"👤 Пациент: {appt.patient.full_name}\n"
           f"📅 Дата: {appt.date.strftime('%d.%m.%Y')}\n"
           f"⏰ Время: {appt.start_time.strftime('%H:%M')}\n"
           f"👨‍⚕️ Врач: {appt.doctor.full_name if appt.doctor else '---'}")
    try:
        tb.send_message(chat_id, msg, parse_mode='Markdown')
    except Exception as e:
        print(f"Ошибка TG: {e}")

def send_morning_report(app):
    """Утренний отчет для планировщика (Закон №37)"""
    with app.app_context():
        tb = get_bot()
        chat_id = app.config.get('TELEGRAM_CHAT_ID')
        if not tb or not chat_id: return

        today = date.today()
        appts = Appointment.query.filter_by(date=today, is_deleted=False).all()
        
        report = f"📊 *План на {today.strftime('%d.%m.%Y')}*\n"
        report += f"Всего записей: {len(appts)}\n"
        # ... тут можно добавить детализацию ...
        
        try:
            tb.send_message(chat_id, report, parse_mode='Markdown')
        except Exception as e:
            print(f"Ошибка отчета: {e}")

def start_bot_listener():
    """Запуск прослушки команд бота (Закон №36)"""
    tb = get_bot()
    if not tb: return

    @tb.message_handler(commands=['start'])
    def send_welcome(message):
        tb.reply_to(message, "🤖 MedosPro Assistant активен!")

    # Запуск в отдельном потоке, чтобы не вешать Flask
    def run_polling():
        tb.infinity_polling()

    thread = threading.Thread(target=run_polling, daemon=True)
    thread.start()