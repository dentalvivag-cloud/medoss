from app import create_app, db
import os

# Создаем экземпляр приложения[cite: 5]
app = create_app()

def initialize_system():
    """Проверка готовности системы перед взлетом (Логика 105)"""
    with app.app_context():
        # 1. Создаем папку для базы данных, если её нет[cite: 7]
        if not os.path.exists('instance'):
            os.makedirs('instance')
            print("📁 Папка instance создана")

        # 2. Создаем таблицы в БД (если их еще нет)[cite: 7]
        db.create_all()
        print("✅ База данных проверена/инициализирована")

        # 3. Создаем папку для бэкапов[cite: 7]
        if not os.path.exists('backups'):
            os.makedirs('backups')
            print("📁 Папка backups готова")

if __name__ == '__main__':
    # Инициализируем папки и БД[cite: 7]
    initialize_system()
    
    # Запуск сервера
    # debug=True: показывает ошибки в реальном времени[cite: 7]
    # use_reloader=False: КРИТИЧНО для работы бота. 
    # Предотвращает двойной запуск Flask и ошибку 409 в Telegram
    print("🚀 MedosPro System запущен на http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)