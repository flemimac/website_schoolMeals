from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from models import db, User, Meal, Application, Ticket
from functools import wraps
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_meals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or not session.get('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница']
    menu = {}
    for day in days:
        menu[day] = {
            'breakfast': Meal.query.filter_by(weekday=day, meal_type='breakfast').all(),
            'soup': Meal.query.filter_by(weekday=day, meal_type='soup').all(),
            'main': Meal.query.filter_by(weekday=day, meal_type='main').all(),
        }
    return render_template('index.html', menu=menu)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Проверка на админа
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['is_admin'] = True
            session['full_name'] = 'Администратор'
            return redirect(url_for('admin_dashboard'))
        # Обычный пользователь
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['logged_in'] = True
            session['user_id'] = user.id
            session['full_name'] = user.full_name
            session['class_info'] = f"{user.class_number}{user.class_letter}"
            session['is_admin'] = False
            return redirect(url_for('personal_account'))
        else:
            flash('Неверный логин или пароль', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        class_number = request.form.get('class_number')
        class_letter = request.form.get('class_letter')
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            class_number = int(class_number)
            if class_number < 1 or class_number > 11:
                flash('Номер класса должен быть от 1 до 11', 'error')
                return redirect(url_for('register'))
            if len(class_letter) != 1 or not class_letter.isalpha():
                flash('Буква класса должна быть одной буквой (А, Б, В и т.д.)', 'error')
                return redirect(url_for('register'))
        except ValueError:
            flash('Номер класса должен быть числом', 'error')
            return redirect(url_for('register'))
        try:
            user = User(full_name=full_name, class_number=class_number, class_letter=class_letter.upper(), username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except Exception:
            db.session.rollback()
            flash('Этот логин уже занят', 'error')
    return render_template('register.html')


@app.route('/personal-account')
def personal_account():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('personal-account.html', 
                         full_name=session.get('full_name'),
                         class_info=session.get('class_info', 'Не указан'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Главная админки (статистика)
@app.route('/admin')
@admin_required
def admin_dashboard():
    total_applications = Application.query.count()
    active_tickets = Ticket.query.filter_by(active=True).count()
    return render_template('admin/dashboard.html',
                           total_applications=total_applications,
                           active_tickets=active_tickets)

# Управление блюдами
@app.route('/admin/meals')
@admin_required
def admin_meals():
    meals = Meal.query.all()
    return render_template('admin/meals.html', meals=meals)


@app.route('/admin/meals/add', methods=['GET', 'POST'])
@admin_required
def admin_add_meal():
    if request.method == 'POST':
        meal_type = request.form['meal_type']
        name = request.form['name']
        weekday = request.form['weekday']
        calories = request.form.get('calories') or 0
        proteins = request.form.get('proteins') or 0
        fats = request.form.get('fats') or 0
        carbs = request.form.get('carbs') or 0
        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        meal = Meal(
            meal_type=meal_type,
            name=name,
            weekday=weekday,
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbs=carbs,
            image=image_filename
        )
        db.session.add(meal)
        db.session.commit()
        flash('Блюдо добавлено', 'success')
        return redirect(url_for('admin_meals'))
    return render_template('admin/meal_form.html', meal=None)


@app.route('/admin/meals/edit/<int:meal_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    if request.method == 'POST':
        # Здесь обработка формы и загрузки фото
        # ...
        pass
    return render_template('admin/meal_form.html', meal=meal)


@app.route('/admin/meals/delete/<int:meal_id>', methods=['POST'])
@admin_required
def admin_delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    flash('Блюдо удалено', 'success')
    return redirect(url_for('admin_meals'))


@app.route('/admin/applications')
@admin_required
def admin_applications():
    status = request.args.get('status')
    query = Application.query
    if status:
        query = query.filter_by(status=status)
    applications = query.order_by(Application.date_submitted.desc()).all()
    return render_template('admin/applications.html', applications=applications)


@app.route('/admin/applications/<int:app_id>', methods=['GET', 'POST'])
@admin_required
def admin_application_detail(app_id):
    application = Application.query.get_or_404(app_id)
    if request.method == 'POST':
        action = request.form.get('action')
        reason = request.form.get('reason')
        if action == 'approve':
            application.status = 'approved'
            application.status_reason = ''
            # Выдача талона
            ticket = Ticket(application_id=application.id)
            db.session.add(ticket)
        elif action == 'reject':
            application.status = 'rejected'
            application.status_reason = reason
        db.session.commit()
        return redirect(url_for('admin_applications'))
    return render_template('admin/application_detail.html', application=application)


@app.route('/admin/tickets/download')
@admin_required
def admin_tickets_download():
    import io, csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'ФИО', 'Класс', 'Дата выдачи', 'Активен'])
    for ticket in Ticket.query.all():
        user = ticket.application.user
        writer.writerow([ticket.id, user.full_name, f"{user.class_number}{user.class_letter}", ticket.date_issued.strftime('%d.%m.%Y'), 'Да' if ticket.active else 'Нет'])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='tickets.csv')


if __name__ == '__main__':
    app.run(debug=True)