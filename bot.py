import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from database import Database  # твій клас Database

TOKEN = "ВАШ_ТОКЕН_БОТА"
CHAT_ID = 123456789  # куди бот буде надсилати повідомлення про нові записи

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DB_PATH = "entries.db"

# ---------------------------------------
# Об'єкт бази даних
# ---------------------------------------
db = Database(DB_PATH)

# Переконаємось, що таблиця існує
db.create_table(
    table_name="entries",
    columns=["id", "name", "email", "phone", "type"],
    types=["INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT NOT NULL", "TEXT NOT NULL", "TEXT NOT NULL", "TEXT NOT NULL"]
)

# ---------------------------------------
# Функції роботи з БД
# ---------------------------------------
def get_all_entries():
    """Отримати всі записи з таблиці entries"""
    return db.select_data("entries", ["id", "name", "email", "phone", "type"])

def update_entry(entry_id, column, new_value):
    """Оновити конкретну колонку запису по id"""
    db.update_data("entries", {column: new_value}, "id = ?", (entry_id,))

def get_latest_id():
    """Отримати максимальний id у таблиці"""
    rows = db.select_data("entries", ["MAX(id)"])
    return rows[0][0] if rows and rows[0][0] else 0

# ---------------------------------------
# Команди бота
# ---------------------------------------
@dp.message_handler(commands=['show'])
async def show_entries(message: types.Message):
    rows = get_all_entries()
    if not rows:
        await message.answer("База порожня.")
        return
    text = "Записи в базі:\n"
    for r in rows:
        text += f"ID: {r[0]}, Ім'я: {r[1]}, Email: {r[2]}, Телефон: {r[3]}, Тип: {r[4]}\n"
    await message.answer(text)

@dp.message_handler(commands=['edit'])
async def edit_entry(message: types.Message):
    """
    Формат команди: /edit <id> <column> <new_value>
    Наприклад: /edit 3 name Максим
    """
    try:
        _, entry_id, column, new_value = message.text.split(maxsplit=3)
        update_entry(int(entry_id), column, new_value)
        await message.answer(f"Запис {entry_id} успішно оновлено: {column} = {new_value}")
    except Exception as e:
        await message.answer("Помилка формату. Використовуй: /edit <id> <column> <new_value>")

# ---------------------------------------
# Фонова перевірка нових записів
# ---------------------------------------
async def monitor_new_entries():
    last_seen_id = get_latest_id()
    while True:
        await asyncio.sleep(5)
        current_last_id = get_latest_id()
        if current_last_id > last_seen_id:
            # Нові записи
            new_rows = db.select_data("entries", ["id", "name", "email", "phone", "type"], "id > ?", (last_seen_id,))
            for r in new_rows:
                await bot.send_message(
                    CHAT_ID,
                    f"Новий запис! ID: {r[0]}, Ім'я: {r[1]}, Email: {r[2]}, Телефон: {r[3]}, Тип: {r[4]}"
                )
            last_seen_id = current_last_id

# ---------------------------------------
# Старт бота
# ---------------------------------------
async def main():
    asyncio.create_task(monitor_new_entries())
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
