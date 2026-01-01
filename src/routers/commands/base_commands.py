import uuid

import structlog
from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils import markdown

from core.structlog import Logger
from enums.commons import ClientCodeTypeEnum
from infrastructures.http.server_api import ServerAPI
from keyboards.common_keyboards import (
    ButtonText,
    get_on_start_kb,
    get_on_btn_register_kb,
    get_phone_request_kb,
    get_on_btn_generate_code_kb,
)
from schemas.client import ClientInfoSchema, ClientCreateSchema

router = Router(name=__name__)

logger: Logger = structlog.get_logger(__name__)


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


@router.message(F.text == ButtonText.MY_CODE)
async def handle_me_code(
    message: types.Message,
    client: ClientInfoSchema | None = None,
):
    if client is None:
        await message.answer(
            "Вы не зарегистрированы в системе. Для получения кода необходимо пройти регистрацию.",
            reply_markup=get_on_btn_register_kb(),
        )
    else:
        if client.code:
            await message.answer(
                f"Ваш клиентский код: <b><code>{client.code}</code></b> 📋 \n\nНажмите на код, чтобы скопировать.",
                parse_mode=ParseMode.HTML,
                reply_markup=get_on_start_kb(),
            )
        else:
            await message.answer(
                "ℹ️ У вас пока нет клиентского кода\n\n"
                "Для продолжения работы, пожалуйста, выберите один из вариантов:",
                reply_markup=get_on_btn_generate_code_kb(),
            )


@router.callback_query(F.data == ClientCodeTypeEnum.CHINA_NICKNAME)
async def handle_generate_china_nickname_code(
    callback: types.CallbackQuery,
    server_api: ServerAPI,
    client: ClientInfoSchema | None = None,
):
    if client is None:
        await callback.message.answer(
            "Вы не зарегистрированы в системе. Для получения кода необходимо пройти регистрацию.",
            reply_markup=get_on_btn_register_kb(),
        )
    else:
        client = await server_api.client.generate_code(
            callback.message.chat.id, ClientCodeTypeEnum.CHINA_NICKNAME
        )
        if client:
            await callback.message.answer(
                f"Ваш клиентский код: <b><code>{client.code}</code></b> 📋 \n\nНажмите на код, чтобы скопировать.",
                parse_mode=ParseMode.HTML,
                reply_markup=get_on_start_kb(),
            )


@router.callback_query(F.data == "register_client")
async def handle_register_client(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        "Для завершения регистрации, пожалуйста, поделитесь вашим номером телефона.",
        reply_markup=get_phone_request_kb(),
    )


@router.message(F.contact)
async def handle_request_phone(
    message: types.Message,
    organization_id: uuid.UUID,
    server_api: ServerAPI,
):
    logger.info(message.contact)
    new_client = ClientCreateSchema(
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name or "lastName",
        phone=message.contact.phone_number,
        chat_id=str(message.chat.id),
        organization_id=organization_id,
    )
    client = await server_api.client.create(new_client)
    if client:
        await message.answer(
            "🎉 Вы успешно зарегистрированы!\n\n "
            "Мы сохранили ваши данные и готовы продолжить работу.",
            reply_markup=get_on_start_kb(),
        )
    else:
        await message.answer(
            "❌ Не удалось завершить регистрацию\n\n"
            "К сожалению, в данный момент мы не смогли зарегистрировать вас.\n"
            "Пожалуйста, попробуйте ещё раз чуть позже или свяжитесь с поддержкой.",
            reply_markup=get_on_start_kb(),
        )


def format_shipments(shipments) -> str:
    lines = ["📦 *Мои посылки*:\n"]
    for i, s in enumerate(shipments, start=1):
        lines.append(
            f"*{i}.* Трек-номер: `{s.tracking_number}`\n"
            f"• Вес: *{s.weight_kg:.2f} кг*\n"
            f"• Цена: *{s.declared_value}*\n"
            f"• Статус: *{s.current_status}*\n"
        )
    return "\n".join(lines)


@router.message(F.text == ButtonText.MY_SHIPMENTS)
async def handle_my_shipments(
    message: types.Message,
    organization_id: uuid.UUID,
    server_api: ServerAPI,
):
    shipments = await server_api.client.get_me_shipments(
        chat_id=message.chat.id,
        organization_id=organization_id,
    )
    if not shipments:
        await message.answer(
            "📦 Посылок пока нет\n\n"
            "Как только посылка поступит на склад, она появится в этом разделе."
        )
    else:
        await message.answer(
            format_shipments(shipments),
            parse_mode=ParseMode.MARKDOWN,
        )
