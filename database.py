# Доповнюй код на українській мові
from sqlite3 import connect, Connection, Cursor

class Database:
    def __init__(self, db_name: str):
        """Ініціалізація підключення до бази даних."""
        self.connection: Connection = connect(db_name)
        self.cursor: Cursor = self.connection.cursor()

    def create_table(self, table_name: str, columns: list, types: list):
        """
        Універсальна функція для створення таблиці в базі даних.
        :param table_name: назва таблиці, яку потрібно створити
        :param columns: список назв колонок
        :param types: список типів і обмежень для колонок (наприклад "INTEGER PRIMARY KEY", "TEXT NOT NULL")
        """
        if len(columns) != len(types):
            return "Кількість колонок і типів не співпадає."

        columns_def = ", ".join([f"{col} {typ}" for col, typ in zip(columns, types)])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"

        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            return "Помилка при створенні таблиці: " + str(e)

    def insert_data(self, table: str, columns: list, values: tuple):
        """
        Універсальна функція для вставки даних у вказану таблицю.
        :param table: назва таблиці
        :param columns: список назв колонок
        :param values: кортеж значень, що вставляються
        """
        placeholders = ", ".join(["?" for _ in values])
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
        except Exception as e:
            return "Помилка при вставці даних: " + str(e)

    def select_data(self, table: str, columns: list = ["*"], where: str = "", params: tuple = ()):
        """
        Універсальна функція для отримання даних з таблиці.
        :param table: назва таблиці
        :param columns: список колонок для вибірки або ["*"] для всіх
        :param where: умова WHERE (без самого слова 'WHERE')
        :param params: параметри для WHERE
        :return: список рядків (list of tuples)
        """
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table}"
        if where:
            query += f" WHERE {where}"

        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            return "Помилка при db, виборі даних: " + str(e)

    def update_data(self, table: str, updates: dict, where: str = "", params: tuple = ()):
        """
        Універсальна функція для оновлення (зміни) даних у таблиці.
        :param table: назва таблиці
        :param updates: словник із колонками та новими значеннями
        :param where: умова WHERE (без самого слова 'WHERE')
        :param params: параметри для WHERE
        """
        set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
        values = tuple(updates.values()) + params
        query = f"UPDATE {table} SET {set_clause}"
        if where:
            query += f" WHERE {where}"

        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("✅ Дані успішно оновлено!")
        except Exception as e:
            print(f"❌ Помилка при оновленні даних: {e}")

    def delete_data(self, table: str, where: str = "", params: tuple = ()):
        """
        Універсальна функція для видалення даних з таблиці.
        :param table: назва таблиці
        :param where: умова WHERE (без самого слова 'WHERE'); якщо не вказано — видаляються всі рядки
        :param params: параметри для WHERE
        """
        query = f"DELETE FROM {table}"
        if where:
            query += f" WHERE {where}"

        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            return "Помилка при видаленні даних: " + str(e)

    def close(self):
        """Закриття підключення до бази даних."""
        self.connection.close()