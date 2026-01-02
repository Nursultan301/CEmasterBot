import uuid
from typing import Callable

import structlog
from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from core.i18n import btn_variants
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

Translate = Callable[[str], str]


@router.message(CommandStart())
async def handle_start(message: types.Message, _: Translate):
    await message.answer(
        text=_(
            "*Hello!* 👋 \n"
            "Welcome to the Cargo system. \n\n"
            "This bot will help you: \n"
            "• 📦 track the status of your shipments; \n"
            "• 🧾 get information about your deliveries; \n"
            "• 🚚 check delivery stages; \n"
            "• ☎️ contact organization representatives if needed. \n\n"
            "To get started, please choose an option from the menu."
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_on_start_kb(_),
    )


@router.message(F.text.in_(btn_variants(ButtonText.CHINA_ADDRESS)))
async def handle_china_address(message: types.Message, _: Translate):
    await message.answer(
        text=_(
            "📌 *Address template — just copy and paste*\n\n"
            "📍 *Recipient*: 波罗特 BAT-10952-7C\n"
            "📍 *Recipient phone number*: 17324524246\n"
            "📍 *Region*: 广东省 佛山市 南海区 里水镇\n"
            "📍 *Address*: 广东省 佛山市 南海区 里水镇 得村横5路5号 "
            "(院内103菠萝吉仓) (BAT-10952-7C) 高德: 铁熊"
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.message(F.text.in_(btn_variants(ButtonText.MY_CODE)))
async def handle_me_code(
    message: types.Message,
    _: Translate,
    client: ClientInfoSchema | None = None,
):
    if client is None:
        await message.answer(
            text=_(
                "You are not registered in the system. "
                "To receive a client code, you need to complete the registration."
            ),
            reply_markup=get_on_btn_register_kb(_),
        )
    else:
        if client.code:
            await message.answer(
                text=_(
                    f"Your client code: `%(client_code)s` 📋 \n\n"
                    f"Tap and hold the code to copy it."
                )
                % {"client_code": client.code},
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_on_start_kb(_),
            )
        else:
            await message.answer(
                text=_(
                    "ℹ️ You don’t have a client code yet\n\n"
                    "To continue, please choose one of the options below:"
                ),
                reply_markup=get_on_btn_generate_code_kb(_),
            )


@router.callback_query(F.data == ClientCodeTypeEnum.CHINA_NICKNAME)
async def handle_generate_china_nickname_code(
    callback: types.CallbackQuery,
    server_api: ServerAPI,
    _: Translate,
    client: ClientInfoSchema | None = None,
):
    if client is None:
        await callback.message.answer(
            text=_(
                "You are not registered in the system. "
                "To receive a client code, you need to complete the registration."
            ),
            reply_markup=get_on_btn_register_kb(_),
        )
    else:
        client = await server_api.client.generate_code(
            callback.message.chat.id,
            ClientCodeTypeEnum.CHINA_NICKNAME,
        )
        if client:
            await callback.message.answer(
                text=_(
                    f"Your client code: `%(client_code)s` 📋 \n\n"
                    f"Tap and hold the code to copy it."
                )
                % {"client_code": client.code},
                parse_mode=ParseMode.HTML,
                reply_markup=get_on_start_kb(_),
            )


@router.callback_query(F.data == "register_client")
async def handle_register_client(callback: types.CallbackQuery, _: Translate):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        text=_("To complete the registration, please " "share your phone number."),
        reply_markup=get_phone_request_kb(_),
    )


@router.message(F.contact)
async def handle_request_phone(
    message: types.Message,
    organization_id: uuid.UUID,
    server_api: ServerAPI,
    _: Translate,
):
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
            text=_(
                "🎉 You have been successfully registered!\n\n"
                "We have saved your information and are ready to continue."
            ),
            reply_markup=get_on_start_kb(_),
        )
    else:
        await message.answer(
            text=_(
                "❌ Registration failed\n\n"
                "Unfortunately, we were unable to register you at this time.\n"
                "Please try again later or contact support."
            ),
            reply_markup=get_on_start_kb(_),
        )


def format_shipments(shipments, _: Translate) -> str:
    lines = [_("📦 *My shipments*:\n")]
    for i, s in enumerate(shipments, start=1):
        lines.append(
            (
                _("*%(index)d.* Tracking number: `%(track)s`\n")
                % {"index": i, "track": s.tracking_number}
            )
            + (_("• Weight: *%(weight).2f kg*\n") % {"weight": s.weight_kg})
            + (_("• Price: *%(price)s*\n") % {"price": s.declared_value})
            + (_("• Status: *%(status)s*\n") % {"status": s.current_status})
        )

    return "\n".join(lines)


@router.message(F.text.in_(btn_variants(ButtonText.MY_SHIPMENTS)))
async def handle_my_shipments(
    message: types.Message,
    organization_id: uuid.UUID,
    server_api: ServerAPI,
    _: Translate,
):
    shipments = await server_api.client.get_me_shipments(
        chat_id=message.chat.id,
        organization_id=organization_id,
    )
    if not shipments:
        await message.answer(
            text=_(
                "📦 No shipments yet\n\n"
                "As soon as a shipment arrives at the warehouse, it will appear in this section."
            )
        )
    else:
        await message.answer(
            format_shipments(shipments, _),
            parse_mode=ParseMode.MARKDOWN,
        )
