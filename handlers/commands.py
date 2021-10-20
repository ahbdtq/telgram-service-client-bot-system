from aiogram import types, Dispatcher

import handlers.keyboards as keyb
from db.db_commands import db_get_item_by_id


async def cmd_start(message: types.Message):
    """
    function for processing start and deep link commands
    """
    unique_code = extract_unique_code(message.text)
    if unique_code:  # if the '/start' command contains a unique_code
        event_id = int(unique_code[unique_code.find('_') + 1:])
        item = await db_get_item_by_id(message.bot.get("db"), event_id)
        caption = f'Событие#:{item.event_id}\n' + \
                  f'Заголовок: {item.event_header}\n' + \
                  f'Описание: {item.event_description}\n'
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=item.event_media,
            caption=caption,
            parse_mode="HTML",
            # reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            f"Добро пожаловать, {message.from_user.full_name}",
            reply_markup=keyb.keyboard_reply_get(keyb.KEYBOARD_MAIN))


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None


def register_commands(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(cmd_start, state='*', commands="start")

