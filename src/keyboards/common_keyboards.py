from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

class ButtonText:
    MY_CODE = "🎫 Мой код"
    PACKAGES = "📦 Мои посылки"
    CHINA_ADDRESS = "🇨🇳 Адрес в Китае"
    PVZ_ADDRESS = "📍 Адрес (ПВЗ)"
    TARIFFS = "📘 Тарифы и условия"
    SUPPORT = "💬 Техподдержка"
    LANGUAGE = "🌐 Выбор языка"


def get_on_start_kb() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=ButtonText.MY_CODE),
         KeyboardButton(text=ButtonText.PACKAGES)],
        [KeyboardButton(text=ButtonText.CHINA_ADDRESS),
         KeyboardButton(text=ButtonText.PVZ_ADDRESS)],
        [KeyboardButton(text=ButtonText.TARIFFS),
         KeyboardButton(text=ButtonText.SUPPORT)],
        [KeyboardButton(text=ButtonText.LANGUAGE)],
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
