from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Patient, Doctor, Appointment, Service, Payment
from datetime import datetime, timedelta

# --- ПРИБОРНАЯ ПАНЕЛЬ (Закон 96) ---
@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Закон 46: Данные для календаря и сводка за день
    today = datetime.utcnow().date()
    appointments = Appointment.query.filter(
        db.func.date(Appointment.start_time) == today,
        Appointment.is_deleted == False
    ).all()
    return render_template('index.html', title='Главная', appointments=appointments)

# --- УПРАВЛЕНИЕ ПАЦИЕНТАМИ (Закон 16, 26, 77) ---
@bp.route('/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        # Закон 103: Валидация входных данных
        phone = request.form.get('phone')
        if Patient.query.filter_by(phone=phone).first():
            flash('Пациент с таким номером уже существует!', 'danger')
            return redirect(url_for('main.add_patient'))
        
        patient = Patient(
            full_name=request.form.get('full_name'),
            phone=phone,
            birth_date=datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None,
            medical_history=request.form.get('medical_history')
        )
        db.session.add(patient)
        db.session.commit()
        flash('Пациент успешно добавлен', 'success')
        return redirect(url_for('main.patient_profile', id=patient.id))
    return render_template('add_patient.html')

@bp.route('/patient/<int:id>')
@login_required
def patient_profile(id):
    patient = Patient.query.get_or_404(id)
    if patient.is_deleted:
        flash('Пациент удален', 'warning')
        return redirect(url_for('main.index'))
    return render_template('patient_profile.html', patient=patient)

# --- ЯДРО ЗАПИСЕЙ (Закон 47: ЗАЩИТА ОТ КОНФЛИКТОВ) ---
@bp.route('/appointment/add', methods=['POST'])
@login_required
def add_appointment():
    data = request.form
    start_time = datetime.strptime(data.get('start_time'), '%Y-%m-%dT%H:%M')
    end_time = start_time + timedelta(minutes=int(data.get('duration', 30)))
    doctor_id = data.get('doctor_id')

    # Закон 47: Проверка наложения (Conflict Check)
    conflict = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.is_deleted == False,
        Appointment.start_time < end_time,
        Appointment.end_time > start_time
    ).first()

    if conflict:
        return jsonify({'status': 'error', 'message': 'Это время у врача уже занято!'}), 409

    appointment = Appointment(
        patient_id=data.get('patient_id'),
        doctor_id=doctor_id,
        start_time=start_time,
        end_time=end_time,
        target_tooth=data.get('target_tooth'), # Закон 18
        notes=data.get('notes'),
        status='scheduled'
    )
    db.session.add(appointment)
    db.session.commit()
    
    # Закон 38: Здесь будет триггер уведомления в Telegram через bot.send_push()
    return jsonify({'status': 'success', 'id': appointment.id})

# --- ФИНАНСОВЫЙ МОДУЛЬ (Закон 26, 101) ---
@bp.route('/payment/add', methods=['POST'])
@login_required
def add_payment():
    patient_id = request.form.get('patient_id')
    amount = float(request.form.get('amount'))
    
    payment = Payment(
        patient_id=patient_id,
        amount=amount,
        payment_method=request.form.get('method', 'cash')
    )
    db.session.add(payment)
    db.session.commit()
    
    # Закон 101: Синхронный пересчет баланса
    patient = Patient.query.get(patient_id)
    patient.update_balance()
    db.session.commit()
    
    flash(f'Оплата {amount} принята. Баланс обновлен.', 'success')
    return redirect(url_for('main.patient_profile', id=patient_id))

# --- API ДЛЯ ЗУБНОЙ ФОРМУЛЫ (Закон 16) ---
@bp.route('/api/patient/<int:id>/formula', methods=['POST'])
@login_required
def update_formula(id):
    patient = Patient.query.get_or_404(id)
    new_formula = request.json.get('formula') # Ожидаем JSON
    patient.dental_formula = new_formula
    db.session.commit()
    return jsonify({'status': 'updated'})

# --- МЯГКОЕ УДАЛЕНИЕ (Закон 15) ---
@bp.route('/patient/<int:id>/delete', methods=['POST'])
@login_required
def delete_patient(id):
    if current_user.role != 'admin': # Закон 57
        return "Доступ запрещен", 403
    patient = Patient.query.get_or_404(id)
    patient.is_deleted = True
    db.session.commit()
    flash('Пациент перемещен в архив', 'info')
    return redirect(url_for('main.index'))
