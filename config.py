import os
from dotenv import load_dotenv

# Загрузка переменных из файла .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Генеральный конфигуратор MEDOS PRO (Закон 103)"""
    
    # --- ЯДРО СИСТЕМЫ ---
    # Секретный ключ для сессий (Закон 59)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'medos-pro-god-mode-hidden-key-2024'
    
    # --- БАЗА ДАННЫХ (Закон 1) ---
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- ТЕЛЕГРАМ ИНТЕГРАЦИЯ (Закон 36) ---
    TELEGRAM_TOKEN = os.environ.get('7816425413:AAH52Pu5elcAcIJDbocK4M7hbOYuy8sQ3Rg')
    # Список ID администраторов через запятую (превращаем в список)
    ADMIN_IDS = [int(i) for i in os.environ.get('7436456028', '6356355374').split(',') if i]
    # ID группы для уведомлений (Закон 38)
    GROUP_ID = os.environ.get('-1003771272642')

    # --- ПАРАМЕТРЫ КЛИНИКИ (Закон 56, 68) ---
    DEFAULT_SALARY_PERCENT = 30.0
    LOW_STOCK_THRESHOLD = 5.0  # Порог для уведомления склада

    # --- ПУТИ ДЛЯ БЭКАПОВ (Закон 72) ---
    BACKUP_DIR = os.path.join(basedir, 'backups')
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # --- ПРЕДОТВРАЩЕНИЕ КЭШИРОВАНИЯ (Закон 87) ---
    SEND_FILE_MAX_AGE_DEFAULT = 0
