from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from core.i18n import Translator
from enums.commons import ClientCodeTypeEnum


class ButtonText:
    MY_CODE = "btn.my_code"
    MY_SHIPMENTS = "btn.my_shipments"
    CHINA_ADDRESS = "btn.china_address"
    PVZ_ADDRESS = "btn.pvz_address"
    TARIFFS = "btn.tariffs"
    SUPPORT = "btn.support"
    LANGUAGE = "btn.language"


def get_on_start_kb(_: Translator) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text=_(ButtonText.MY_CODE)),
            KeyboardButton(text=_(ButtonText.MY_SHIPMENTS)),
        ],
        [
            KeyboardButton(text=_(ButtonText.CHINA_ADDRESS)),
            KeyboardButton(text=_(ButtonText.PVZ_ADDRESS)),
        ],
        [
            KeyboardButton(text=_(ButtonText.TARIFFS)),
            KeyboardButton(text=_(ButtonText.SUPPORT)),
        ],
        [KeyboardButton(text=_(ButtonText.LANGUAGE))],
    ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_on_btn_register_kb(_: Translator) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("Register"),
                    callback_data="register_client",
                ),
            ]
        ]
    )


def get_phone_request_kb(_: Translator) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=_("📞 Share phone number"),
                    request_contact=True,
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_on_btn_generate_code_kb(_: Translator) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("🈲 Chinese code"),
                    callback_data=ClientCodeTypeEnum.CHINA_NICKNAME,
                ),
                InlineKeyboardButton(
                    text=_("🆔 Standard code"),
                    callback_data=ClientCodeTypeEnum.DIGITAL,
                ),
            ]
        ]
    )


def language_kb(_: Translator) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang:ky"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ],
            [InlineKeyboardButton(text=_("Back"), callback_data="lang:back")],
        ]
    )
