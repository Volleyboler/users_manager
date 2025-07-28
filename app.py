from flask import Flask, jsonify, request
import sqlite3
from werkzeug.exceptions import NotFound
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
DATABASE = 'users.db'

def create_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users')
    users = [{'id': row[0], 'name': row[1], 'email': row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Имя и email используются'}), 400
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', 
                      (data['name'], data['email']))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'id': user_id,
            'name': data['name'],
            'email': data['email']
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Пользователь с таким email уже существует'}), 400

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        raise NotFound(description="Пользователь не найден")
    
    return jsonify({
        'id': user[0],
        'name': user[1],
        'email': user[2]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': error.description}), 404

if __name__ == '__main__':
    create_db()
    app.run(debug=True)
