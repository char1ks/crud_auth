from flask import Flask, jsonify, request, render_template
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Подключение к PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),  # Используем переменную окружения
        database=os.getenv('POSTGRES_DB', 'myHibernate'),  # Используем переменную окружения
        user=os.getenv('POSTGRES_USER', 'postgres'),  # Используем переменную окружения
        password=os.getenv('POSTGRES_PASSWORD', 'expo')  # Используем переменную окружения
    )
    return conn

# Главная страница (Read)
@app.route('/')
def index():
    return render_template('index.html')

# Страница добавления пользователя (Create)
@app.route('/add', methods=['GET'])
def add():
    return render_template('add.html')

# Страница редактирования пользователя (Update)
@app.route('/edit/<int:id>', methods=['GET'])
def edit(id):
    return render_template('edit.html', id=id)

# Получение всех пользователей (Read)
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users;')
    users = cur.fetchall()
    cur.close()
    conn.close()

    # Преобразуем данные в список словарей для JSON
    users_list = [{'id': user[0], 'username': user[1], 'email': user[2]} for user in users]
    return jsonify(users_list)

# Получение одного пользователя по ID (Read)
@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s', (id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        return jsonify({'error': 'User not found'}), 404

    user_dict = {'id': user[0], 'username': user[1], 'email': user[2]}
    return jsonify(user_dict)

# Добавление пользователя (Create)
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({'error': 'Username and email are required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (username, email) VALUES (%s, %s)', (username, email))
        conn.commit()
        return jsonify({'message': 'User added successfully!'}), 201
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Редактирование пользователя (Update)
@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({'error': 'Username and email are required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE users SET username = %s, email = %s WHERE id = %s', (username, email, id))
        conn.commit()
        return jsonify({'message': 'User updated successfully!'}), 200
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Удаление пользователя (Delete)
@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM users WHERE id = %s', (id,))
        conn.commit()
        return jsonify({'message': 'User deleted successfully!'}), 200
    except psycopg2.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)