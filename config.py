import os

class Config:
    # Базовые настройки Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'viva-dental-super-secret-150'
    
    # Путь к базе данных (Закон №15)
    # Создаст файл dentist.db в папке instance
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dentist.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Telegram Integration (Закон №36, №38)
    # Получи токен у @BotFather
    TELEGRAM_BOT_TOKEN = '7816425413:AAH52Pu5elcAcIJDbocK4M7hbOYuy8sQ3Rg' 
    
    # Твой личный ID (узнай у @userinfobot)
    TELEGRAM_CHAT_ID = '-1003771272642' 
    
    # Список ID администраторов, которым разрешен доступ к финансам через бота
    ADMIN_IDS = [7436456028, 6356355374]

    # Настройки бэкапов (Закон №72)
    BACKUP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backups')