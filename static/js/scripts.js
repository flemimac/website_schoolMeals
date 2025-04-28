// Обработка переключения типа питания
document.getElementById('specialDiet').addEventListener('change', function() {
    document.getElementById('specialDietNotes').style.display = this.checked ? 'block' : 'none';
});
document.getElementById('regularDiet').addEventListener('change', function() {
    document.getElementById('specialDietNotes').style.display = 'none';
});

// Обработка отмены заявки
document.getElementById('cancelRequestBtn')?.addEventListener('click', function() {
    if (confirm('Вы уверены, что хотите отменить текущую заявку?')) {
        alert('Заявка успешно отменена');
        this.closest('.card-body').querySelector('.badge').className = 'badge bg-secondary';
        this.closest('.card-body').querySelector('.badge').textContent = 'Отменено';
        this.disabled = true;
    }
});

// Установка текущего месяца
const months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 
               'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'];
const currentDate = new Date();
const currentMonthElement = document.getElementById('current-month');
if (currentMonthElement) {
    currentMonthElement.textContent = months[currentDate.getMonth()];
}

// Валидация формы регистрации
document.querySelector('form')?.addEventListener('submit', function(e) {
    const classNumber = document.getElementById('class_number');
    const classLetter = document.getElementById('class_letter');
    
    if (classNumber && (classNumber.value < 1 || classNumber.value > 11)) {
        alert('Номер класса должен быть от 1 до 11');
        e.preventDefault();
        return;
    }
    
    if (classLetter && !/^[А-Яа-яA-Za-z]$/.test(classLetter.value)) {
        alert('Буква класса должна быть одной буквой (А, Б, В и т.д.)');
        e.preventDefault();
        return;
    }
});