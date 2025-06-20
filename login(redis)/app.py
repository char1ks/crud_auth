from flask import Flask, render_template, request, redirect, url_for, session, flash
import redis
import os

app = Flask(__name__)
app.secret_key = 'qwertyoreveryother'  # Секретный ключ для сессий

# Подключение к Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')  # Используем переменную окружения
redis_port = int(os.getenv('REDIS_PORT', 6379))    # Используем переменную окружения
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)

@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверяем, существует ли пользователь в Redis
        if redis_client.hexists('users', username):
            flash('Username already exists!', 'error')
        else:
            # Сохраняем пользователя в Redis
            redis_client.hset('users', username, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверяем, существует ли пользователь и совпадает ли пароль
        if redis_client.hexists('users', username) and redis_client.hget('users', username).decode('utf-8') == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)