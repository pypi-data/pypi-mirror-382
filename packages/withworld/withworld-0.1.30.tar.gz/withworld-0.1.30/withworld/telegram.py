import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
from typing import Optional, Union
KeyboardType = Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_bot(API_TOKEN):
    """Создает объект БОТА"""
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    return dp, bot

def create_menu(button_texts: list[str]):
    """Создает объект клавиатуры с кнопками
    На вход объект БОТА, Список названий кнопок"""
    buttons = [KeyboardButton(text=text) for text in button_texts]
    # группируем кнопки в строки (по одной кнопке на строку)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button] for button in buttons],
        resize_keyboard=True
    )
    return keyboard

def create_inline_menu(buttons_info: list[dict]) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру.
    
    button_info: список словарей с параметрами кнопки, например:
        [{"text": "Нажми меня", "callback_data": "btn_1"},
         {"text": "Ссылка", "url": "https://example.com"}]
         
    Возвращает объект InlineKeyboardMarkup
    """
    buttons = []
    for info in buttons_info:
        button = InlineKeyboardButton(**info)  # передаем text, callback_data или url
        buttons.append([button])  # каждая кнопка в отдельной строке
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def send_message_to_chat(
    chat_id: int,
    text: str,
    bot: Bot,
    reply_markup: Optional[KeyboardType] = None
):
    """
    Универсальная функция отправки сообщения.
    
    reply_markup: InlineKeyboardMarkup, ReplyKeyboardMarkup или None
    """
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup  # можно None
    )



# Обработчик нажатия кнопки
async def start_bot(dp, bot):
    await dp.start_polling(bot)


def REGISTR_WEBHOOK_LINK():
    """

Регистрация вебхука у Telegram
curl -F "url=https://fokinax.com/telegram/webhook/" \
"https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook"

Проверка регистрации
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo



    """
