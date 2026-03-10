from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json

# --- ВСПОМОГАТЕЛЬНЫЕ ТАБЛИЦЫ СВЯЗЕЙ ---
# Закон 1: Принцип Паутины (Связь услуг и приемов)
appointment_services = db.Table('appointment_services',
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointment.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """Закон 57: Разграничение прав (Admin/Doctor/Reception)"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='doctor')  # admin, doctor, receptionist
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    """Закон 16, 17, 26: Ядро пациента"""
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), index=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False) # Закон 77: Валидация телефонов
    birth_date = db.Column(db.Date)
    
    # Закон 16: Зубная формула (Храним как JSON-строку)
    dental_formula = db.Column(db.Text, default='{}') 
    
    # Закон 17: Анамнез
    medical_history = db.Column(db.Text)
    
    # Закон 26: Финансовый баланс
    balance = db.Column(db.Float, default=0.0)
    
    # Закон 15: Мягкое удаление
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Связи
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic')
    payments = db.relationship('Payment', backref='patient', lazy='dynamic')

    def update_balance(self):
        """Закон 26: Автоматический пересчет баланса"""
        total_paid = sum(p.amount for p in self.payments if not p.is_deleted)
        total_cost = sum(a.total_price for a in self.appointments if a.status == 'completed' and not a.is_deleted)
        self.balance = total_paid - total_cost

class Doctor(db.Model):
    """Закон 56: Зарплата и статистика"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    specialization = db.Column(db.String(100))
    salary_percent = db.Column(db.Float, default=30.0) # Закон 56
    is_deleted = db.Column(db.Boolean, default=False)
    
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')

class Service(db.Model):
    """Закон 33: Авто-цены"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

class Appointment(db.Model):
    """Закон 46-51: Календарь и Статусы"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, index=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    # Закон 51: Цепочка статусов
    status = db.Column(db.String(20), default='scheduled') # scheduled, in_chair, completed, cancelled
    
    # Закон 18: Локализация (какой зуб лечим)
    target_tooth = db.Column(db.String(50)) 
    
    notes = db.Column(db.Text)
    total_price = db.Column(db.Float, default=0.0)
    
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Связь с услугами (многие ко многим)
    services = db.relationship('Service', secondary=appointment_services, backref='appointments')

class Payment(db.Model):
    """Закон 26-35: Финансы"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50)) # cash, card, qr
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Закон 35: Блокировка редактирования старых оплат (через логику роутов)
    is_deleted = db.Column(db.Boolean, default=False)

class Inventory(db.Model):
    """Закон 66-68: Склад"""
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20)) # мл, шт, уп
    min_threshold = db.Column(db.Float, default=5.0) # Закон 68: Дефицит-контроль
