/**
 * MEDOS PRO: GLOBAL SCRIPT ENGINE (Закон 104)
 * Синхронизация Календаря, Формулы и Финансов
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. ИНИЦИАЛИЗАЦИЯ КАЛЕНДАРЯ (Закон 46, 50) ---
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'timeGridDay',
            slotMinTime: '08:00:00',
            slotMaxTime: '21:00:00',
            editable: true,
            selectable: true,
            locale: 'ru',
            events: '/api/appointments', // Эндпоинт, который мы создали в app/main.py

            // Закон 50: Перетаскивание (Drag-and-Drop)
            eventDrop: function(info) {
                updateAppointmentTime(info.event);
            },

            // Закон 47: Проверка конфликтов при создании
            select: function(info) {
                const title = prompt('Введите имя пациента:');
                if (title) {
                    saveAppointment({
                        start: info.startStr,
                        end: info.endStr,
                        title: title
                    });
                }
            },
            
            eventDidMount: function(info) {
                // Вызов функции раскраски из base.html
                if (window.updateEventStyles) window.updateEventStyles(info);
            }
        });
        calendar.render();
    }

    // --- 2. УПРАВЛЕНИЕ ЗУБНОЙ ФОРМУЛОЙ (Закон 16) ---
    const teeth = document.querySelectorAll('.tooth-unit');
    teeth.forEach(tooth => {
        tooth.addEventListener('click', function() {
            const toothId = this.dataset.id;
            const patientId = document.getElementById('patient-id').value;
            
            // Переключение состояния (Здоровый / Лечение / Удален)
            this.classList.toggle('needs-treatment');
            
            saveDentalState(patientId, toothId, this.classList.contains('needs-treatment'));
        });
    });
});

/**
 * ЗАКОН 103: ФУНКЦИИ ОТПРАВКИ ДАННЫХ (Zero-Trust)
 */
async function saveAppointment(data) {
    try {
        const response = await fetch('/appointment/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams(data)
        });
        const result = await response.json();
        if (result.status === 'success') {
            location.reload(); // Перезагрузка для синхронизации "Паутины"
        } else {
            alert('Ошибка: ' + result.message);
        }
    } catch (e) {
        console.error("System Error:", e);
    }
}

async function saveDentalState(patientId, toothId, status) {
    // Закон 16: Асинхронное сохранение состояния зуба
    fetch(`/api/patient/${patientId}/formula`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tooth: toothId, status: status })
    });
}
