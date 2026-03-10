import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    # Получаем абсолютный путь к папке Medos/app
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Импорт маршрутов
        from app.main import bp as main_blueprint
        app.register_blueprint(main_blueprint)
        
        # Запуск бота только если это не основной процесс релоадера
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or app.debug is False:
            from app.telegram_bot import start_bot_listener
            try:
                start_bot_listener()
                print("🚀 Telegram Bot запущен")
            except Exception as e:
                print(f"⚠️ Ошибка бота: {e}")

    return app