from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


def init_db():
    if not os.path.exists('school_meals.db'):
        connection = sqlite3.connect('school_meals.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                class_number INTEGER NOT NULL,
                class_letter TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        connection.commit()
        connection.close()

init_db()


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        connection = sqlite3.connect('school_meals.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        connection.close()
        
        if user:
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['full_name'] = user[1]
            session['class_info'] = f"{user[2]}{user[3]}"
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
            connection = sqlite3.connect('school_meals.db')
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO users (full_name, class_number, class_letter, username, password) 
                VALUES (?, ?, ?, ?, ?)
            ''', (full_name, class_number, class_letter.upper(), username, password))
            connection.commit()
            connection.close()
            
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
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


if __name__ == '__main__':
    app.run(debug=True)