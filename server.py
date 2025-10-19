# Доповнюй код на українській мові
from flask import Flask, render_template, request
from database import Database

app = Flask(__name__)
def create_entries_table():
    entries_db = Database("entries.db")
    entries_db.create_table(
        "entries",
        ["id", "name", "email", "phone", "type"],
        ["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT NOT NULL", "TEXT NOT NULL", "TEXT NOT NULL", "TEXT NOT NULL"]
    )
    entries_db.close()

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Отримання даних з форми
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    type_ = request.form.get('type')

    entries = Database("entries.db")
    entries.insert_data(
        "entries",
        ["name", "email", "phone", "type"],
        (name, email, phone, type_)
    )
    entries.close()
    return "Дані успішно додані!"

if __name__ == '__main__':
    create_entries_table()
    app.run(debug=True)
    