# Обробники текстових повідомлень від користувачів
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from database import Database
from config import DATABASE
from states import EditState
from keyboards import get_main_menu, get_edit_menu

# Ініціалізація роутера для текстових повідомлень
router = Router()

# Глобальний екземпляр бази даних
db = Database(DATABASE)

# -----------------------------
# Допоміжна функція перевірки авторизації
# -----------------------------
def is_authorized(chat_id: int) -> bool:
    """
    Перевіряє чи авторизований користувач.
    :param chat_id: ID чату користувача
    :return: True якщо користувач авторизований, False інакше
    """
    result = db.select_data("users", ["registered"], "chat_id = ?", (chat_id,))
    return result and len(result) > 0 and result[0][0] == 1

# -----------------------------
# Перегляд записів
# -----------------------------
@router.message(F.text == "📋 Записи")
async def view_entries(message: Message):
    """
    Обробник кнопки "📋 Записи".
    Виводить всі записи клієнтів з бази даних.
    """
    if not is_authorized(message.chat.id):
        await message.answer("🚫 У вас немає доступу. Використайте /start")
        return

    # Отримуємо всі записи з БД
    entries = db.select_data("entries")
    if not entries:
        await message.answer("📭 Поки що немає записів на заняття.")
        return

    # Формуємо текст з усіма записами
    text = "📋 **Записи клієнтів:**\n\n"
    for entry in entries:
        text += f"🆔 ID: {entry[0]}\n"
        text += f"👤 Ім'я: {entry[1]}\n"
        text += f"📧 Email: {entry[2]}\n"
        text += f"📞 Телефон: {entry[3]}\n"
        text += f"📦 Послуга: {entry[4]}\n"
        text += "─" * 30 + "\n\n"
    
    await message.answer(text, parse_mode="Markdown")

# -----------------------------
# Редагування - початок
# -----------------------------
@router.message(F.text == "✏️ Редагувати")
async def start_edit(message: Message, state: FSMContext):
    """
    Обробник кнопки "✏️ Редагувати".
    Показує список доступних записів та просить ввести ID для редагування.
    """
    if not is_authorized(message.chat.id):
        await message.answer("🚫 У вас немає доступу.")
        return

    # Отримуємо список записів
    entries = db.select_data("entries", ["id", "name"])
    if not entries:
        await message.answer("📭 Немає записів для редагування.")
        return

    # Формуємо список доступних записів
    text = "📝 Доступні записи:\n\n"
    for entry in entries:
        text += f"🆔 {entry[0]} - {entry[1]}\n"
    
    text += "\n💡 Введіть ID запису для редагування:"
    await message.answer(text)
    await state.set_state(EditState.waiting_id)

# -----------------------------
# Редагування - обробка ID
# -----------------------------
@router.message(EditState.waiting_id)
async def process_edit_id(message: Message, state: FSMContext):
    """
    Обробник стану очікування ID запису.
    Перевіряє чи існує запис з введеним ID та переходить до вибору поля.
    """
    # Перевірка чи введено число
    if not message.text.isdigit():
        await message.answer("❌ Введіть числовий ID запису:")
        return
    
    record_id = int(message.text)
    # Перевірка чи існує запис з таким ID
    result = db.select_data("entries", ["id"], "id = ?", (record_id,))
    
    if not result or len(result) == 0:
        await message.answer("❌ Запис з таким ID не знайдено. Спробуйте ще раз:")
        return
    
    # Зберігаємо ID та переходимо до вибору поля
    await state.update_data(record_id=record_id)
    await message.answer("✏️ Оберіть поле для редагування:", reply_markup=get_edit_menu())
    await state.set_state(EditState.waiting_field)

# -----------------------------
# Редагування - скасування
# -----------------------------
@router.message(EditState.waiting_field, F.text == "❌ Скасувати")
async def cancel_edit(message: Message, state: FSMContext):
    """
    Обробник кнопки "❌ Скасувати" під час редагування.
    Скасовує процес редагування та повертає до головного меню.
    """
    await state.clear()
    await message.answer("❌ Редагування скасовано.", reply_markup=get_main_menu())

# -----------------------------
# Редагування - обробка вибору поля
# -----------------------------
@router.message(EditState.waiting_field)
async def process_edit_field(message: Message, state: FSMContext):
    """
    Обробник вибору поля для редагування.
    Перевіряє вибране поле та просить ввести нове значення.
    """
    # Відображення назв кнопок на поля БД
    field_map = {
        "Ім'я": "name",
        "Email": "email",
        "Телефон": "phone",
        "Послуга": "service"
    }
    
    field = field_map.get(message.text)
    if not field:
        await message.answer("❌ Оберіть поле з меню:")
        return
    
    # Зберігаємо поле та переходимо до введення значення
    await state.update_data(field=field)
    await message.answer(f"✍️ Введіть нове значення для поля '{message.text}':")
    await state.set_state(EditState.waiting_value)

# -----------------------------
# Редагування - обробка нового значення
# -----------------------------
@router.message(EditState.waiting_value)
async def process_edit_value(message: Message, state: FSMContext):
    """
    Обробник введення нового значення поля.
    Оновлює запис у базі даних з новим значенням.
    """
    # Отримуємо дані зі стану
    data = await state.get_data()
    record_id = data['record_id']
    field = data['field']
    new_value = message.text
    
    # Оновлюємо запис у БД
    db.update_data("entries", {field: new_value}, "id = ?", (record_id,))
    await message.answer(
        f"✅ Запис #{record_id} оновлено!\n{field} → {new_value}",
        reply_markup=get_main_menu()
    )
    await state.clear()

# -----------------------------
# Сповіщення
# -----------------------------
@router.message(F.text == "🔔 Сповіщення")
async def toggle_notifications(message: Message):
    """
    Обробник кнопки "🔔 Сповіщення".
    Перемикає статус сповіщень користувача (увімкнути/вимкнути).
    """
    if not is_authorized(message.chat.id):
        await message.answer("🚫 У вас немає доступу.")
        return

    # Отримуємо поточний статус сповіщень
    result = db.select_data("users", ["notify"], "chat_id = ?", (message.chat.id,))
    current_state = result[0][0] if result and len(result) > 0 else 0
    new_state = 0 if current_state == 1 else 1  # Перемикаємо стан
    
    # Оновлюємо статус у БД
    db.update_data("users", {"notify": new_state}, "chat_id = ?", (message.chat.id,))
    
    if new_state == 1:
        await message.answer(
            "🔔 **Сповіщення увімкнені** ✅\n\n"
            "Ви отримуватимете повідомлення про нові записи клієнтів.", 
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "🔕 **Сповіщення вимкнені** ❌\n\n"
            "Ви більше не отримуватимете повідомлення.", 
            parse_mode="Markdown"
        )

# -----------------------------
# Допомога
# -----------------------------
@router.message(F.text == "ℹ️ Допомога")
async def cmd_help(message: Message):
    """
    Обробник кнопки "ℹ️ Допомога".
    Виводить довідку по використанню бота.
    """
    help_text = """
📖 **Довідка по боту**

**Основні функції:**
📋 Записи - Перегляд всіх записів клієнтів
✏️ Редагувати - Зміна даних запису
🔔 Сповіщення - Увімкнути/вимкнути повідомлення про нові записи
ℹ️ Допомога - Ця довідка

**Команди:**
/start - Перезапуск бота
/status - Статус підключення

💡 Записи надходять автоматично з сайту.
    """
    await message.answer(help_text, parse_mode="Markdown")

