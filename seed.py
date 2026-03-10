import sqlite3
from datetime import datetime

def seed_database():
    # Подключение к базе данных (создаст файл, если его нет)
    conn = sqlite3.connect('drb.db')
    cursor = conn.cursor()

    # 1. Категории услуг
    categories = [
        (1, 'Терапия'),
        (2, 'Хирургия'),
        (3, 'Ортопедия'),
        (4, 'Имплантация'),
        (5, 'ЛОР'),
        (6, 'Процедурная')
    ]
    cursor.executemany("INSERT OR IGNORE INTO service_categories (id, name) VALUES (?, ?)", categories)

    # 2. Врачи (Doctors)
    doctors = [
        (1, 'Dr. Kamron', 'Имплантолог', '336680808'),
        (2, 'Dr. Burxoniddin', 'Стоматолог', '934566336'),
        (3, 'Массаж', 'Массаж', None)
    ]
    cursor.executemany("INSERT OR IGNORE INTO doctors (id, full_name, specialization, phone) VALUES (?, ?, ?, ?)", doctors)

    # 3. Пациенты (Patients)[cite: 1]
    # Данные извлечены из дампа (имена и телефоны)
    patients = [
        (1, 'Эргашев Тимур', '903536844', 'male', '2026-01-24'),
        (2, 'Исмаилходжа Султонов', '974808981', 'male', '2026-01-24'),
        (3, 'Лейлакулова Рухноза', '912570980', 'female', '2026-01-23'),
        (4, 'Азиза опа', '934433190', 'female', '2026-01-19')
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO patients (id, full_name, phone, gender, created_at) 
        VALUES (?, ?, ?, ?, ?)
    """, patients)

    # 4. Услуги (Services)[cite: 1]
    services = [
        (1, 1, 'Реставрация жевательных зубов', 150000.0),
        (2, 1, 'Эндо 1 канала', 80000.0),
        (3, 2, 'Сложное удаление', 200000.0),
        (4, 6, 'Промывание', 50000.0)
    ]
    cursor.executemany("INSERT OR IGNORE INTO services (id, category_id, name, price) VALUES (?, ?, ?, ?)", services)

    # 5. Приемы (Appointments)[cite: 1]
    appointments = [
        (1, 1, 1, '2026-01-20', '13:00:00', '14:00:00', 'completed', 'Осмотр', 'Кариес', 250000.0, 0.0)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO appointments 
        (id, patient_id, doctor_id, date, start_time, end_time, status, complaint, diagnosis, total_cost, discount) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, appointments)

    # Сохранение изменений
    conn.commit()
    print("Database seeded successfully!")
    conn.close()

if __name__ == "__main__":
    seed_database()
