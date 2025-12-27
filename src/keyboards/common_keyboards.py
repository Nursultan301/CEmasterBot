from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from enums.commons import ClientCodeTypeEnum


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
        [
            KeyboardButton(text=ButtonText.MY_CODE),
            KeyboardButton(text=ButtonText.PACKAGES),
        ],
        [
            KeyboardButton(text=ButtonText.CHINA_ADDRESS),
            KeyboardButton(text=ButtonText.PVZ_ADDRESS),
        ],
        [
            KeyboardButton(text=ButtonText.TARIFFS),
            KeyboardButton(text=ButtonText.SUPPORT),
        ],
        [KeyboardButton(text=ButtonText.LANGUAGE)],
    ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_on_btn_register_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Зарегистрироватся",
                    callback_data="register_client",
                ),
            ]
        ]
    )


def get_phone_request_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📞 Поделиться номером телефона",
                    request_contact=True,
                    callback_data="request_phone",
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_on_btn_generate_code_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🈲 Китайский код",
                    callback_data=ClientCodeTypeEnum.CHINA_NICKNAME,
                ),
                InlineKeyboardButton(
                    text="🆔 Обычный код",
                    callback_data=ClientCodeTypeEnum.DIGITAL,
                ),
            ]
        ]
    )
