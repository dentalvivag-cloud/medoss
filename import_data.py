from app import app, db
from models import ServiceCategory, Doctor, Patient, Service, Appointment, Expense
from datetime import datetime

def import_all_data():
    with app.app_context():
        # 1. Очистка старых данных (опционально, осторожно!)
        # db.drop_all()
        # db.create_all()

        print("Начинаю импорт данных...")

        # --- КАТЕГОРИИ УСЛУГ ---
        categories = [
            ServiceCategory(id=1, name='Терапия'),
            ServiceCategory(id=2, name='Хирургия'),
            ServiceCategory(id=3, name='Ортопедия'),
            ServiceCategory(id=4, name='Имплантация'),
            ServiceCategory(id=5, name='ЛОР'),
            ServiceCategory(id=6, name='Процедурная')
        ]
        
        # --- ВРАЧИ ---
        doctors = [
            Doctor(id=1, full_name='Dr. Kamron', specialization='Имплантолог', phone='336680808'),
            Doctor(id=2, full_name='Dr. Burxoniddin', specialization='Стоматолог', phone='934566336'),
            Doctor(id=3, full_name='Массаж', specialization='Массаж', phone=None)
        ]

        # --- ПАЦИЕНТЫ ---
        patients = [
            Patient(id=1, full_name='Эргашев Тимур', phone='903536844', gender='male', created_at=datetime(2026, 1, 24)),
            Patient(id=2, full_name='Исмаилходжа Султонов', phone='974808981', gender='male', created_at=datetime(2026, 1, 24)),
            Patient(id=3, full_name='Лейлакулова Рухноза', phone='912570980', gender='female', created_at=datetime(2026, 1, 23)),
            Patient(id=4, full_name='Азиза опа', phone='934433190', gender='female', created_at=datetime(2026, 1, 19))
        ]

        # --- УСЛУГИ ---
        services = [
            Service(id=1, category_id=1, name='Реставрация жевательных зубов', price=150000.0),
            Service(id=2, category_id=1, name='Эндо 1 канала', price=80000.0),
            Service(id=3, category_id=2, name='Сложное удаление', price=200000.0)
        ]

        # --- РАСХОДЫ (из вашего дампа) ---
        expenses = [
            Expense(id=1, category='Зарплата', amount=1000000.0, description='Выплата Dr. Kamron', date=datetime(2026, 1, 20)),
            Expense(id=2, category='Хозрасходы', amount=50000.0, description='Газ свет такси', date=datetime(2026, 1, 21))
        ]

        # Добавляем всё в сессию
        db.session.add_all(categories)
        db.session.add_all(doctors)
        db.session.add_all(patients)
        db.session.add_all(services)
        db.session.add_all(expenses)
        
        # Сохраняем первую порцию, чтобы работали внешние ключи для записей
        db.session.commit()

        # --- ПРИЕМЫ (Appointments) ---
        # Здесь важно, чтобы patient_id и doctor_id совпадали с ID выше
        appointments = [
            Appointment(
                patient_id=1, 
                doctor_id=1, 
                date=datetime.strptime('2026-01-20', '%Y-%m-%d').date(),
                start_time=datetime.strptime('13:00', '%H:%M').time(),
                status='completed',
                complaint='Осмотр',
                diagnosis='Кариес',
                total_cost=250000.0
            )
        ]
        db.session.add_all(appointments)
        db.session.commit()

        print("Импорт успешно завершен!")

if __name__ == "__main__":
    import_all_data()
