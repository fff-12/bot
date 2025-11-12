from flask import Flask, render_template, request
from database import Database
from config import DATABASE

app = Flask(__name__)
db = Database(DATABASE)

# Створюємо таблицю записів (один раз)
db.create_table(
    "entries",
    ["id", "name", "email", "phone", "type"],
    ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT NOT NULL", "TEXT NOT NULL", "TEXT NOT NULL", "TEXT NOT NULL"]
)

# Створюємо таблицю користувачів бота (один раз)
db.create_table(
    "users",
    ["id", "chat_id", "username", "registered", "notify"],
    ["INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER UNIQUE", "TEXT", "INTEGER DEFAULT 0", "INTEGER DEFAULT 0"]
)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    """Обробка форми та запис у базу"""
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    type_ = request.form.get('type')
    if not (name and email and phone and type_):
        return "❌ Будь ласка, заповніть усі поля!"
    db.insert_data("entries", ["name", "email", "phone", "type"], (name, email, phone, type_))
    return "✅ Дані успішно додані!"

if __name__ == '__main__':
    app.run(debug=True)
