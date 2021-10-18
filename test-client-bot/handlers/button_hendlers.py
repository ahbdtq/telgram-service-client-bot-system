"""
The module describes a catalog showing one item and buttons for moving forward / backward.
The module is not connected, the buttons "Contact" and "Delete event" are not configured.
"""
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMedia
from aiogram.utils.callback_data import CallbackData
from sqlalchemy import select, func

from db.models import EventTable

catalog_callback = CallbackData("catalog", "page")


def get_catalog_keyboard(pages: int, is_owner: bool, page: int = 0) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()  # row_width=3
    has_next_page = pages > page + 1
    button_list1 = []
    if page != 0:
        button_list1.append(
            InlineKeyboardButton(
                text="< Назад",
                callback_data=catalog_callback.new(page=page - 1)
            )
        )

    button_list1.append(
        InlineKeyboardButton(
            text=f"• {page + 1} / {pages}",
            callback_data="don't_click_me"
        )
    )

    if has_next_page:
        button_list1.append(
            InlineKeyboardButton(
                text="Вперёд >",
                callback_data=catalog_callback.new(page=page + 1)
            )
        )

    button_list2 = []
    button_list2.append(
        InlineKeyboardButton(
            text="Связаться",
            callback_data="don't_click_me"
        )
    )
    if is_owner:
        button_list2.append(
            InlineKeyboardButton(
                text="❌ Удалить событие",
                callback_data="don't_click_me"
            )
        )

    keyboard.row(*button_list1).row(*button_list2)

    return keyboard


async def get_catalog_count(message: types.Message):
    db_session = message.bot.get("db")
    sql = select(func.count(EventTable.event_id))
    async with db_session() as session:
        results = await session.scalar(sql)
    return results


async def get_catalog_item(message: types.Message, p_limit: int, p_offset: int):
    db_session = message.bot.get("db")
    sql = select(EventTable).order_by(EventTable.event_id.asc()).limit(p_limit).offset(p_offset)
    async with db_session() as session:
        results = await session.execute(sql)

    return results.scalars().one()


async def catalog_index(message: types.Message):
    item_data = await get_catalog_item(message, 1, 0)
    items_count = await get_catalog_count(message)
    caption = f'Событие#:{item_data.event_id}\n' + \
              f'Имя:{item_data.event_name}\n' + \
              f'Заголовок: {item_data.event_header}\n' + \
              f'Описание: {item_data.event_description}\n' + \
              f'Дата конца показа:{item_data.event_description}'

    is_owner = item_data.user_id == message.from_user.id
    keyboard = get_catalog_keyboard(items_count, is_owner)  # Page: 0

    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=item_data.event_media,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def catalog_page_handler(query: CallbackQuery, callback_data: dict):
    page = int(callback_data.get("page"))
    item_data = await get_catalog_item(query.message, 1, page)
    items_count = await get_catalog_count(query.message)
    caption = f'Событие#: {item_data.event_id}\n' + \
              f'Имя: {item_data.event_name}\n' + \
              f'Заголовок: {item_data.event_header}\n' + \
              f'Описание: {item_data.event_description}\n' + \
              f'Дата конца показа:{item_data.event_description}'

    is_owner = item_data.user_id == query.from_user.id
    keyboard = get_catalog_keyboard(items_count, is_owner, page)

    photo = InputMedia(type="photo", media=item_data.event_media, caption=caption)

    await query.message.edit_media(photo, keyboard)


def register_handlers_buttons(dp: Dispatcher):
    dp.register_message_handler(catalog_index, lambda message: message.text == "Каталог")
    dp.register_callback_query_handler(catalog_page_handler, catalog_callback.filter())
