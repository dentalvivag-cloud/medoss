from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, flash, send_file
from app import db
from app.models import Patient, Appointment, Payment, Doctor, Expense, Service, AuditLog
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, date
import os
import json
import atexit

# Интеграция с Telegram-ботом и Планировщиком (Логика 105)
from app.telegram_bot import send_morning_report, notify_new_appointment, start_bot_listener
from apscheduler.schedulers.background import BackgroundScheduler

bp = Blueprint('main', __name__)

# --- СЛУЖБЫ АВТОМАТИЗАЦИИ ---

scheduler = BackgroundScheduler()

def start_scheduler(app):
    """Запуск фоновых задач: Отчеты и Бот (Законы №36-39)"""
    if not scheduler.running:
        with app.app_context():
            # Утренний отчет владельцу в 08:00
            scheduler.add_job(
                func=send_morning_report, 
                trigger="cron", 
                hour=8, minute=0, 
                args=[app], 
                id='morning_report',
                replace_existing=True
            )
            scheduler.start()
            # Запуск прослушки команд Telegram
            try:
                start_bot_listener()
            except Exception as e:
                app.logger.error(f"Ошибка запуска бота: {e}")
            
            atexit.register(lambda: scheduler.shutdown())

# --- ГЛОБАЛЬНЫЕ ФУНКЦИИ (Финансы) ---

@bp.app_template_global()
def get_balance(patient):
    """Расчет баланса пациента в реальном времени (Законы №26-28)"""
    if not patient: return 0, 0, 0
    # Считаем только неудаленные записи
    valid_appts = [a for a in patient.appointments if not getattr(a, 'is_deleted', False)]
    total_cost = sum(a.total_cost for a in valid_appts if a.total_cost) or 0
    total_paid = sum(p.amount for a in valid_appts for p in a.payments) or 0
    return total_cost, total_paid, total_paid - total_cost

# --- ОСНОВНЫЕ МАРШРУТЫ ---

@bp.route('/')
def dashboard():
    """Главный экран: Календарь + Должники + Инициализация служб"""
    # Гарантируем запуск планировщика при первом входе
    start_scheduler(current_app._get_current_object())
    
    today = date.today()
    patients = Patient.query.filter_by(is_deleted=False).all()
    doctors = Doctor.query.all()
    
    # Сбор должников для боковой панели
    debtors = []
    for p in patients:
        _, _, balance = get_balance(p)
        if balance < -1:
            debtors.append({'name': p.full_name, 'debt': abs(balance), 'id': p.id})
    
    return render_template('dashboard.html', 
                           patients=patients, 
                           doctors=doctors,
                           debtors=sorted(debtors, key=lambda x: x['debt'], reverse=True)[:10],
                           today=today)

@bp.route('/add_appointment', methods=['POST'])
def add_appointment():
    """Умная запись: Создание пациента + Проверка конфликтов + Уведомление"""
    data = request.form
    patient_id = data.get('patient_id')
    
    try:
        # 1. Логика 105: Авто-создание пациента, если его нет в базе
        if not patient_id or patient_id == "" or data.get('create_new_patient') == '1':
            new_p = Patient(
                full_name=data.get('new_patient_name'),
                phone=data.get('new_patient_phone'),
                is_deleted=False
            )
            db.session.add(new_p)
            db.session.flush()
            patient_id = new_p.id

        # 2. Обработка времени и даты
        date_obj = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        start_t = datetime.strptime(data.get('start_time'), '%H:%M').time()
        # Если время окончания не указано, ставим +1 час
        if data.get('end_time'):
            end_t = datetime.strptime(data.get('end_time'), '%H:%M').time()
        else:
            end_t = (datetime.combine(date_obj, start_t) + timedelta(hours=1)).time()

        doc_id = int(data.get('doctor_id'))

        # 3. Закон №47: Проверка на наложение (Conflict Detection)
        conflict = Appointment.query.filter(
            Appointment.doctor_id == doc_id,
            Appointment.date == date_obj,
            Appointment.is_deleted == False,
            or_(
                and_(Appointment.start_time <= start_t, Appointment.end_time > start_t),
                and_(Appointment.start_time < end_t, Appointment.end_time >= end_t)
            )
        ).first()

        if conflict:
            flash(f"Внимание! Врач уже занят в это время (запись #{conflict.id})", "danger")
            return redirect(url_for('main.dashboard'))

        # 4. Создание записи
        new_appt = Appointment(
            patient_id=patient_id,
            doctor_id=doc_id,
            date=date_obj,
            start_time=start_t,
            end_time=end_t,
            tooth_number=data.get('tooth_number'),
            complaints=data.get('complaint'),
            total_cost=float(data.get('price') or 0),
            is_deleted=False
        )
        db.session.add(new_appt)
        
        # 5. Аудит (Закон №71)
        db.session.add(AuditLog(action='CREATE_APPOINTMENT', target_id=patient_id, details=f"Запись на {date_obj} {start_t}"))
        
        db.session.commit()

        # 6. Telegram-уведомление (Мгновенно)
        try:
            notify_new_appointment(new_appt)
        except:
            pass

        flash('Запись успешно создана и добавлена в график!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
        
    return redirect(url_for('main.dashboard'))

# --- API ДЛЯ КАЛЕНДАРЯ (FullCalendar) ---

@bp.route('/api/appointments')
def get_appointments_json():
    """Отдает данные для отрисовки плиток в календаре"""
    appts = Appointment.query.filter_by(is_deleted=False).all()
    events = []
    for a in appts:
        events.append({
            'id': a.id,
            'title': f"{a.patient.full_name} | {a.tooth_number or '?'}",
            'start': datetime.combine(a.date, a.start_time).isoformat(),
            'end': datetime.combine(a.date, a.end_time).isoformat(),
            'resourceId': str(a.doctor_id),
            'backgroundColor': a.doctor.color_code,
            'extendedProps': {
                'phone': a.patient.phone,
                'complaint': a.complaints
            }
        })
    return jsonify(events)

@bp.route('/api/move_appointment', methods=['POST'])
def move_appointment():
    """Обработка Drag-and-Drop перетаскивания"""
    data = request.json
    appt = Appointment.query.get(data.get('id'))
    if appt:
        new_start = datetime.fromisoformat(data.get('start').replace('Z', ''))
        appt.date = new_start.date()
        appt.start_time = new_start.time()
        # Если перетащили к другому врачу (в другую колонку)
        if data.get('doctor_id'):
            appt.doctor_id = data.get('doctor_id')
        
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

# --- МОДУЛИ АНАЛИТИКИ И СИСТЕМЫ ---

@bp.route('/doctor_stats')
def doctor_stats():
    """Эффективность врачей: Деньги и Приемы (Закон №32)"""
    stats = db.session.query(
        Doctor.full_name,
        func.count(Appointment.id).label('total_appts'),
        func.sum(Appointment.total_cost).label('total_revenue')
    ).join(Appointment).filter(Appointment.is_deleted == False).group_by(Doctor.id).all()
    return render_template('doctor_stats.html', stats=stats)

@bp.route('/settings/backup')
def create_backup():
    """Закон №72: Безопасность данных"""
    if not os.path.exists('backups'): os.makedirs('backups')
    filename = f"backups/clinic_db_{date.today()}.db"
    import shutil
    shutil.copyfile('instance/clinic.db', filename)
    return send_file(filename, as_attachment=True)