// Обработка переключения типа питания
document.getElementById('specialDiet').addEventListener('change', function() {
    const specialDietNotes = document.getElementById('specialDietNotes');
    specialDietNotes.style.display = this.checked ? 'block' : 'none';
});

document.getElementById('regularDiet').addEventListener('change', function() {
    document.getElementById('specialDietNotes').style.display = 'none';
});

// Установка текущего месяца
const months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 
               'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'];
const currentDate = new Date();
document.getElementById('current-month').textContent = months[currentDate.getMonth()];

// Инициализация скрытия блока особого питания при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('specialDietNotes').style.display = 'none';
});