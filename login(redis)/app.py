from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
import redis
import psycopg2
import psycopg2.extras
import os
import bcrypt

app = Flask(__name__)

# Исправляем генерацию URL за прокси-сервером (GitHub Codespaces)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1
)

# --- Конфигурация ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key-that-is-long-and-random')
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url(f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379")

# --- Инициализация расширений ---
server_session = Session(app)

# --- Подключение к БД ---
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    return conn

# --- Функции-хелперы ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- Роуты ---
@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('home.html', username=session.get('username'), secret=session.get('secret'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        secret = request.form['secret']

        if not username or not password or not secret:
            flash('Имя пользователя, пароль и секретная информация обязательны!', 'error')
            return render_template('register.html')

        hashed_password = hash_password(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO users (username, password_hash, secret) VALUES (%s, %s, %s)',
                (username, hashed_password.decode('utf-8'), secret)
            )
            conn.commit()
            flash('Регистрация прошла успешно! Пожалуйста, войдите в систему.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Имя пользователя уже существует!', 'error')
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password(password, user['password_hash']):
            session.clear()  
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['secret'] = user['secret']
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Неверное имя пользователя или пароль!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы.', 'success')
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie(app.config.get('SESSION_COOKIE_NAME', 'session'))
    return resp

if __name__ == '__main__':
    app.run(debug=True, port=5001)