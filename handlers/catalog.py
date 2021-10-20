"""
The module provides functions for displaying navigation in the event catalog
"""
from aiogram import types, Dispatcher

from db.db_commands import db_get_catalog_items, db_get_catalog_count, db_delete_item_by_id
import handlers.keyboards as keyb


async def catalog_show_event(message: types.Message, offset: int):
    """
    Get one event from catalog and send message chat in format:
    {photo}
    {event_id}
    {event_header}
    {event_description}
    ['Связаться','Удалить событие']

    @param message: aiogram.types.Massage
    @param offset: int
    """
    item = await db_get_catalog_items(message.bot.get("db"), 1, offset)
    caption = f'Событие#:{item.event_id}\n' + \
              f'Заголовок: {item.event_header}\n' + \
              f'Описание: {item.event_description}\n'

    is_owner = item.user_id == message.chat.id
    keyboard = keyb.keyboard_catalog_get(is_owner)

    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=item.event_media,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def catalog_index(message: types.Message):
    """
    form catalog. send first two items of catalog and "more"-buttons ['+1','+5'] to chat.

    @param message: aiogram.types.Massage
    """
    items_count = await db_get_catalog_count(message.bot.get("db"))
    if items_count <= 0:
        await message.answer('Каталог пуст.', reply_markup=keyb.keyboard_reply_get(keyb.KEYBOARD_MAIN))
        return

    offset = 2  # number of items to show
    for offset in range(offset):
        await catalog_show_event(message, offset)

    if items_count > offset+1:
        keyboard = keyb.keyboard_catalog_show_more(items_count, offset)
        await message.answer('Показать больше', reply_markup=keyboard)


async def catalog_page_handler(query: types.CallbackQuery, callback_data: dict):
    """
    Show +1 or +5 catalog items according to pressed "more"-button

    @param query: types.CallbackQuery
    @param callback_data: dict
    """
    items_count = await db_get_catalog_count(query.bot.get("db"))
    page = int(callback_data.get("page"))
    to_page = int(callback_data.get("to_page"))
    for offset in range(page + 1, to_page + 1):
        await catalog_show_event(query.message, offset)

    if items_count > to_page + 1:
        keyboard = keyb.keyboard_catalog_show_more(items_count, to_page)
        await query.message.answer('Показать больше', reply_markup=keyboard)


async def catalog_delete_event_confirmation_handler(query: types.CallbackQuery):
    """Delete confirmation dialog"""
    event_id = query.message.html_text.split(f'\n')[0]
    event_id = int(event_id[event_id.find(':') + 1:])
    keyboard = keyb.keyboard_catalog_delete_confirmation()
    await query.message.answer(f'Вы дейтвительно хотите удалить событие? #{event_id}', reply_markup=keyboard)


async def catalog_delete_event_handler(query: types.CallbackQuery):
    """
    Delete catalog item. Item ID take from query
    """
    event_id = int(query.message.html_text.split(f'#')[1])
    await db_delete_item_by_id(query.bot.get("db"), event_id)
    await query.message.answer(f'Событие {event_id} удалено')
    await catalog_index(query.message)

async def catalog_return_to_catalog(query: types.CallbackQuery):
    """If the user refused to delete, show the catalog from beginning"""
    await catalog_index(query.message)

def register_catalog_handlers(dp: Dispatcher):
    """register handlers"""
    dp.register_message_handler(catalog_index, lambda message: message.text == "Каталог")
    dp.register_callback_query_handler(catalog_delete_event_handler, lambda c: c.data == 'delete_event')
    dp.register_callback_query_handler(catalog_return_to_catalog, lambda c: c.data == 'cancel_delete')
    dp.register_callback_query_handler(catalog_delete_event_confirmation_handler, lambda c: c.data == 'delete_event_confirmation')
    dp.register_callback_query_handler(catalog_page_handler, keyb.catalog_callback.filter())
