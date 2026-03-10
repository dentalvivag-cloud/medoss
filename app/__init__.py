import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

# Инициализация расширений (Закон 1: Единое ядро)
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = "Пожалуйста, войдите в систему."

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация плагинов в контексте приложения
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # --- РЕГИСТРАЦИЯ BLUEPRINTS (Закон 75) ---
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_for_security='auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # --- ГЛОБАЛЬНЫЕ КОНТЕКСТЫ (Закон 76) ---
    @app.context_processor
    def inject_globals():
        """Автоматическая доступность данных во всех шаблонах"""
        from app.models import Patient, Appointment
        return {
            'total_patients': Patient.query.filter_by(is_deleted=False).count(),
            'today_appointments': Appointment.query.filter(
                db.func.date(Appointment.start_time) == db.func.current_date()
            ).count()
        }

    # --- ОБРАБОТКА ОШИБОК (Закон 86) ---
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback() # Защита целостности БД
        return render_template('errors/500.html'), 500

    # --- ПЛАНИРОВЩИК ЗАДАЧ (Закон 37, 39) ---
    scheduler = BackgroundScheduler()
    
    @scheduler.scheduled_job('cron', hour=8, minute=0)
    def daily_report():
        """Закон 37: Утренний отчет в Telegram через bot.py"""
        with app.app_context():
            # Здесь будет вызов из logic/bot.py
            print("Отправка утреннего отчета...")

    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.start()

    return app

# Импорт моделей для корректной работы миграций
from app import models
