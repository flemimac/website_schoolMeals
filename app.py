from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_meals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    class_number = db.Column(db.Integer, nullable=False)
    class_letter = db.Column(db.String(1), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
# Модель блюда
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    calories = db.Column(db.Integer)
    proteins = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    weekday = db.Column(db.String(10))

# Модель заявки
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    diet_type = db.Column(db.String(50))
    special_reason = db.Column(db.String(120))
    special_details = db.Column(db.Text)
    file = db.Column(db.String(255))
    status = db.Column(db.String(20), default='new')
    status_reason = db.Column(db.String(255))

    user = db.relationship('User', backref='applications')

# Модель талона
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    date_issued = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    application = db.relationship('Application', backref='tickets')

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
    return render_template('index.html')


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
        # Здесь обработка формы и загрузки фото
        # ...
        pass
    return render_template('admin/meal_form.html')


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


# Обработка заявок
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


# Отчёты (выгрузка талонов)
@app.route('/admin/tickets/download')
@admin_required
def admin_tickets_download():
    # Здесь формируется файл (например, CSV) и отправляется пользователю
    # Пример заглушки:
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