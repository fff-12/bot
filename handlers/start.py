# Обробники команд /start, /help, /status та авторизації
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from database import Database
from config import ACCESS_CODE, DATABASE
from states import AuthState
from keyboards import get_main_menu

# Ініціалізація роутера для команд
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
# Команда /start
# -----------------------------
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Обробник команди /start.
    Перевіряє чи є користувач у базі даних та чи авторизований він.
    Якщо ні - просить ввести пароль.
    """
    result = db.select_data("users", ["chat_id", "registered"], "chat_id = ?", (message.chat.id,))
    
    # Якщо користувача немає в БД - створюємо нового
    if not result or len(result) == 0:
        db.insert_data("users", ["chat_id", "username", "registered", "notify"],
                      (message.chat.id, message.from_user.username or "Unknown", 0, 0))
        await message.answer("👋 Вітаю! Для доступу до функцій бота введіть пароль:")
        await state.set_state(AuthState.waiting_password)
        return
    
    # Перевіряємо статус авторизації
    user = result[0]
    if user[1] == 1:  # Користувач авторизований
        await message.answer("✅ Ви авторизовані! Оберіть дію:", reply_markup=get_main_menu())
    else:  # Користувач не авторизований
        await message.answer("🔐 Введіть пароль для доступу:")
        await state.set_state(AuthState.waiting_password)

# -----------------------------
# Авторизація (обробка пароля)
# -----------------------------
@router.message(AuthState.waiting_password)
async def process_password(message: Message, state: FSMContext):
    """
    Обробник стану очікування пароля.
    Перевіряє правильність введеного пароля та авторизує користувача.
    """
    if message.text == ACCESS_CODE:
        # Пароль правильний - авторизуємо користувача
        db.update_data("users", {"registered": 1}, "chat_id = ?", (message.chat.id,))
        await message.answer("✅ Успішно авторизовано!", reply_markup=get_main_menu())
        await state.clear()
    else:
        # Пароль неправильний - просимо спробувати ще раз
        await message.answer("❌ Невірний пароль. Спробуйте ще раз:")

# -----------------------------
# Команда /help
# -----------------------------
@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Обробник команди /help.
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

# -----------------------------
# Команда /status
# -----------------------------
@router.message(Command("status"))
async def cmd_status(message: Message):
    """
    Обробник команди /status.
    Виводить поточний статус бота та статистику.
    """
    if not is_authorized(message.chat.id):
        await message.answer("🚫 У вас немає доступу.")
        return
    
    # Отримуємо статистику
    total_entries = len(db.select_data("entries"))
    result = db.select_data("users", ["notify"], "chat_id = ?", (message.chat.id,))
    notify_status = "увімкнені ✅" if (result and len(result) > 0 and result[0][0] == 1) else "вимкнені ❌"
    
    await message.answer(
        f"📊 **Статус:**\n\n"
        f"📋 Всього записів: {total_entries}\n"
        f"🔔 Сповіщення: {notify_status}",
        parse_mode="Markdown"
    )

