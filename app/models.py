from datetime import datetime
from app import db
import json

class User(db.Model):
    """Пользователи системы (Администраторы)"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='admin')

class Doctor(db.Model):
    """Врачи клиники (Законы №18, №35)"""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    color_code = db.Column(db.String(7), default='#0d6efd')  # Для календаря
    salary_percent = db.Column(db.Float, default=0.0)       # Для аналитики
    is_active = db.Column(db.Boolean, default=True)         # Тот самый missing column
    is_deleted = db.Column(db.Boolean, default=False)       # Закон №15
    
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Patient(db.Model):
    """Карточка пациента (Законы №1, №16)"""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date)
    address = db.Column(db.String(200))
    anamnesis = db.Column(db.Text)                          # Мед. анкета
    tooth_formula = db.Column(db.Text, default='{}')        # JSON статус зубов (Закон №16)
    balance = db.Column(db.Float, default=0.0)              # Динамический баланс
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    payments = db.relationship('Payment', backref='patient', lazy=True)

class ServiceCategory(db.Model):
    """Категории услуг (Терапия, Хирургия и т.д.)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    services = db.relationship('Service', backref='category', lazy=True)

class Service(db.Model):
    """Прайс-лист услуг (Закон №51)"""
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('service_category.id'))
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)

class Appointment(db.Model):
    """Приемы и записи в календаре (Закон №47)"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    tooth_number = db.Column(db.Integer)                    # Конкретный зуб
    complaints = db.Column(db.Text)                         # Жалобы
    treatment_plan = db.Column(db.Text)                     # План лечения
    total_cost = db.Column(db.Float, default=0.0)           # Сколько начислено
    amount_paid = db.Column(db.Float, default=0.0)          # Сколько оплачено (Закон №26)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    is_deleted = db.Column(db.Boolean, default=False)

class Payment(db.Model):
    """Финансовые транзакции (Закон №56)"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20))               # Нал, Карта, Kaspi
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

class Expense(db.Model):
    """Расходы клиники (Закон №35)"""
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))                     # Зарплата, Аренда, Материалы
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

class AuditLog(db.Model):
    """Журнал безопасности (Закон №71)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100))                      # "Удаление пациента", "Смена цены"
    target_type = db.Column(db.String(50))                  # "Patient", "Appointment"
    target_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)                            # JSON изменений