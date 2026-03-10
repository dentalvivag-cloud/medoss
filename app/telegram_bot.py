import telebot
from telebot import types
from app.models import User, Appointment, Doctor, Patient
from app import db
from datetime import datetime
import os

# Инициализация (Закон 36)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_user_by_tg(message):
    """Закон 79: Поиск привязанного пользователя"""
    return User.query.filter_by(telegram_id=str(message.from_user.id)).first()

# --- ОБРАБОТЧИКИ КОМАНД ---

@bot.message_with_type_conversion
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("📅 Моё расписание")
    item2 = types.KeyboardButton("📊 Статистика клиники")
    markup.add(item1, item2)
    
    bot.reply_to(message, 
        "🤖 СИСТЕМА MEDOS PRO АКТИВИРОВАНА.\n"
        "Для синхронизации отправьте ваш ID из профиля системы.", 
        reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📅 Моё расписание")
def show_schedule(message):
    """Закон 44: Команды для врачей"""
    user = get_user_by_tg(message)
    if not user or user.role != 'doctor':
        bot.send_message(message.chat.id, "❌ Ошибка доступа. Аккаунт не привязан.")
        return

    today = datetime.utcnow().date()
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        db.func.date(Appointment.start_time) == today,
        Appointment.is_deleted == False
    ).order_by(Appointment.start_time).all()

    if not appointments:
        bot.send_message(message.chat.id, "✅ На сегодня записей нет. Отдыхайте!")
        return

    res = f"📅 Расписание на {today}:\n\n"
    for app in appointments:
        res += f"⏰ {app.start_time.strftime('%H:%M')} — {app.patient.full_name}\n"
    
    bot.send_message(message.chat.id, res)

# --- СИСТЕМНЫЕ УВЕДОМЛЕНИЯ (Закон 38, 101) ---

def send_instant_push(appointment_id):
    """Мгновенное уведомление о новой записи"""
    app = Appointment.query.get(appointment_id)
    if not app: return

    msg = (f"🔔 НОВАЯ ЗАПИСЬ!\n"
           f"👤 Пациент: {app.patient.full_name}\n"
           f"👨‍⚕️ Врач: {app.doctor.user.username}\n"
           f"📅 Время: {app.start_time.strftime('%d.%m %H:%M')}")
    
    # Отправляем админам
    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        if admin.telegram_id:
            try:
                bot.send_message(admin.telegram_id, msg)
            except Exception as e:
                print(f"Ошибка отправки: {e}")

# --- УТРЕННИЙ ОТЧЕТ (Закон 37) ---

def send_morning_report():
    """Запуск через APScheduler в app/__init__.py"""
    with db.app.app_context():
        today = datetime.utcnow().date()
        total_apps = Appointment.query.filter(
            db.func.date(Appointment.start_time) == today,
            Appointment.is_deleted == False
        ).count()
        
        msg = f"☀️ ДОБРОЕ УТРО!\n📅 Сегодня: {today}\n🏥 Всего записей в клинике: {total_apps}"
        
        # Рассылка всем сотрудникам с привязанным TG
        users = User.query.filter(User.telegram_id != None).all()
        for u in users:
            bot.send_message(u.telegram_id, msg)

# Запуск бота в отдельном потоке (вызывается из app.py)
def run_bot():
    bot.infinity_polling()
