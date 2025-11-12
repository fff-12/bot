from sqlite3 import connect, Connection, Cursor

class Database:
    def __init__(self, db_name: str):
        """Ініціалізація підключення до бази даних.
        Підключається до файлу SQLite і створює курсор для виконання запитів.
        """
        self.connection: Connection = connect(db_name, check_same_thread=False)
        self.cursor: Cursor = self.connection.cursor()

    def create_table(self, table_name: str, columns: list, types: list):
        """
        Створює таблицю у базі даних, якщо вона ще не існує.
        :param table_name: Назва таблиці
        :param columns: Список колонок
        :param types: Список типів і обмежень для колонок
        """
        if len(columns) != len(types):
            return "Кількість колонок і типів не співпадає."
        columns_def = ", ".join([f"{col} {typ}" for col, typ in zip(columns, types)])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            return f"Помилка при створенні таблиці: {e}"

    def insert_data(self, table: str, columns: list, values: tuple):
        """
        Вставляє рядок у таблицю.
        :param table: Назва таблиці
        :param columns: Список колонок
        :param values: Значення для вставки у вигляді кортежу
        """
        placeholders = ", ".join(["?" for _ in values])
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
        except Exception as e:
            return f"Помилка при вставці даних: {e}"

    def select_data(self, table: str, columns: list = ["*"], where: str = "", params: tuple = ()):
        """
        Отримує дані з таблиці.
        :param table: Назва таблиці
        :param columns: Список колонок для вибірки або ["*"] для всіх
        :param where: Умова WHERE (без слова 'WHERE')
        :param params: Параметри для умови WHERE
        :return: Список рядків (list of tuples)
        """
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table}"
        if where:
            query += f" WHERE {where}"
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            return f"Помилка при виборі даних: {e}"

    def update_data(self, table: str, updates: dict, where: str = "", params: tuple = ()):
        """
        Оновлює дані у таблиці.
        :param table: Назва таблиці
        :param updates: Словник колонка → нове значення
        :param where: Умова WHERE (без слова 'WHERE')
        :param params: Параметри для WHERE
        """
        set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
        values = tuple(updates.values()) + params
        query = f"UPDATE {table} SET {set_clause}"
        if where:
            query += f" WHERE {where}"
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
        except Exception as e:
            return f"Помилка при оновленні даних: {e}"

    def delete_data(self, table: str, where: str = "", params: tuple = ()):
        """
        Видаляє рядки з таблиці.
        :param table: Назва таблиці
        :param where: Умова WHERE (без слова 'WHERE'), якщо не вказано — видаляються всі рядки
        :param params: Параметри для WHERE
        """
        query = f"DELETE FROM {table}"
        if where:
            query += f" WHERE {where}"
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            return f"Помилка при видаленні даних: {e}"

    def close(self):
        """Закриває підключення до бази даних."""
        self.connection.close()
