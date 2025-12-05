from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils import markdown

from src.keyboards.common_keyboards import (
    ButtonText,
    get_on_start_kb,
)

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: types.Message):
    url = "https://w7.pngwing.com/pngs/547/380/png-transparent-robot-waving-hand-bot-ai-robot-thumbnail.png"

    await message.answer(
        text=f"{markdown.hide_link(url)}Hello, {markdown.hbold(message.from_user.full_name)}!",
        parse_mode=ParseMode.HTML,
        reply_markup=get_on_start_kb(),
    )


CHINA_ADDRESS_TEXT = (
    "📌 *Шаблон заполнения адреса, просто скопируй и вставь*\n\n"
    "📍 *Получатель*: 波罗特 BAT-10952-7C\n"
    "📍 *Номер телефона получателя*: 17324524246\n"
    "📍 *Регион*: 广东省 佛山市 南海区 里水镇\n"
    "📍 *Адрес*: 广东省 佛山市 南海区 里水镇 得村横5路5号 "
    "(院内103菠萝吉仓) (BAT-10952-7C) 高德: 铁熊"
)


@router.message(F.text == ButtonText.CHINA_ADDRESS)
async def handle_china_address(message: types.Message):
    await message.answer(CHINA_ADDRESS_TEXT, parse_mode=ParseMode.MARKDOWN)
