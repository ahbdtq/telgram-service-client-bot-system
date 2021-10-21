"""
This module describes a state machine for chat with event owner
"""
import logging.config
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.message import ContentType

import config
from db.db_commands import db_get_item_by_id
import handlers.keyboards as keyb


logging.config.fileConfig(fname=r'logger.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class Form(StatesGroup):
    chat_data = State()


async def connect_user(query: types.CallbackQuery, state: FSMContext):
    async def create_connection(query: types.CallbackQuery, state: FSMContext):
        await Form.chat_data.set()
        await state.update_data(chat_data=query)

        if query.message.bot.data["bot"] == 'CLIENT_BOT':
            event_id = query.message.caption.split(f'\n')[1]
            event_title = event_id[event_id.find(':') + 1:]
            text_ = f"Вы вошли в чат с владельцем события:{event_title}"
            keyboard = keyb.keyboard_reply_get(keyb.KEYBOARD_CHAT)
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(f"❌Выйти из чата c:" + query.message.html_text.split('\n')[1].split(':')[0])
            text_ = f"Вы вошли в чат с:" + query.message.html_text.split('\n')[1].split(':')[0]
        return text_,keyboard


    if not bool(await state.get_data()):
        text_, keyboard = await create_connection(query, state)
    else:
        state_data = await state.get_data()
        if query.message.bot.data["bot"] == 'CLIENT_BOT':
            event_id = state_data['chat_data'].message.caption.split(f'\n')[1]
            old_query_name = "владельцем события: "+event_id[event_id.find(':') + 1:]
            event_id = query.message.caption.split(f'\n')[1]
            new_query_name = "владельцем события: "+event_id[event_id.find(':') + 1:]
        else:
            old_query_name = ": " + state_data['chat_data'].message.html_text.split('\n')[1].split(':')[0]
            new_query_name = ": " + query.message.html_text.split('\n')[1].split(':')[0]

        if old_query_name == new_query_name:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(f"❌Выйти из чата c " + new_query_name)
            text_ = f"Вы уже в чате с " + new_query_name
        else:
            await state.finish()
            text_, keyboard = await create_connection(query, state)

    await query.message.answer(
        text_,
        reply_markup=keyboard
    )

async def connect_cancel(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


async def prepare_vars(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    keyboard = InlineKeyboardMarkup()
    if message.bot.data["bot"] == 'CLIENT_BOT':
        event_id = state_data['chat_data'].message.caption.split(f'\n')[0]
        event_id = int(event_id[event_id.find(':') + 1:])
        item = await db_get_item_by_id(message.bot.get("db"), event_id)

        url = f"{config.CLIENT_BOT_URL}looktoid_{str(item.event_id)}"
        keyboard.row(
            InlineKeyboardButton(
                text="Ответить",
                callback_data=f"answeruser_{message.chat.id}"
            ),
            InlineKeyboardButton(
                text="Посмотреть событие",
                url=url
            )
        )
        text_ = f"Сообщение:{item.event_name},\n" + \
                f"{message.from_user.full_name}: "
        text_ += f"{message.text}" if message.text else ""
        tmp_var_chat_id = item.user_id
    else:
        event_name = state_data['chat_data'].message.html_text.split(f'\n')[0]
        event_name = event_name[event_name.find(':') + 1:]
        keyboard.row(
            InlineKeyboardButton(
                text="Ответить",
                callback_data="connect_owner"
            ),
            InlineKeyboardButton(
                text="Посмотреть событие",
                callback_data="Посмотреть событие"
            )
        )
        text_ = f"Сообщение от владельца события {event_name}\n"
        text_ += f"{message.text}" if message.text else ""
        tmp_var_chat_id = state_data['chat_data'].data.split(f'_')[1]

    destination_dir = config.FILE_DIR[message.bot.data["bot"]]
    return text_, tmp_var_chat_id, keyboard, destination_dir


async def forward_text(message: types.Message, state: FSMContext):
    """
    Forwards text message to pair bot.
    """
    text_, chat_id_, keyboard, _ = await prepare_vars(message, state)
    with message.bot.with_token(message.bot.data["send_to_bot_token"]):
        await message.bot.send_message(
            chat_id=chat_id_,
            text=text_,
            reply_markup=keyboard
        )


async def forward_sticker(message: types.Message, state: FSMContext):
    """
    Forwards media message to pair bot.
    """
    text_, chat_id_, keyboard, _ = await prepare_vars(message, state)
    with message.bot.with_token(message.bot.data["send_to_bot_token"]):
        await message.bot.send_sticker(
            chat_id=chat_id_,
            sticker=message.sticker.file_id,
            reply_markup=keyboard
        )


async def forward_video_note(message: types.Message, state: FSMContext):
    """
    Forwards media message to pair bot.
    """
    text_, chat_id_, keyboard, _ = await prepare_vars(message, state)
    file_ = await message.video_note.download()
    with message.bot.with_token(message.bot.data["send_to_bot_token"]):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_video_note(
            chat_id=chat_id_,
            video_note=file_,
            reply_markup=keyboard
        )


async def forward_media_message(message: types.Message, state: FSMContext):
    """
    Forwards media message to pair bot.
    work with next content types:
    voice, animation, video, document, audio, photo
    """
    text_, chat_id_, keyboard, destination_dir = await prepare_vars(message, state)
    if message.content_type == 'photo':
        file_ = await getattr(message, message.content_type)[-1].download(destination_dir=destination_dir)
    else:
        file_ = await getattr(message, message.content_type).download(destination_dir=destination_dir)
    with message.bot.with_token(message.bot.data["send_to_bot_token"]):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await getattr(message.bot, 'send_'+message.content_type)(
            chat_id_,
            file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_location(message: types.Message, state: FSMContext):
    """
    Forwards location to pair bot.
    """
    text_, chat_id_, keyboard, _ = await prepare_vars(message, state)
    with message.bot.with_token(message.bot.data["send_to_bot_token"]):
        await message.bot.send_location(
            chat_id=chat_id_,
            longitude=message.location.longitude,
            latitude=message.location.latitude,
            reply_markup=keyboard
        )


async def show_event(message: types.Message, state: FSMContext):
    """
    Get one event from catalog and send message chat in format:
    {photo}
    {event_id}
    {event_header}
    {event_description}

    @param message: aiogram.types.Massage
    @param offset: int
    """
    state_data = await state.get_data()
    event_id = state_data['chat_data'].message.caption.split(f'\n')[0]
    event_id = int(event_id[event_id.find(':') + 1:])

    item = await db_get_item_by_id(message.bot.get("db"), event_id)
    caption = f'Событие#:{item.event_id}\n' + \
              f'Заголовок: {item.event_header}\n' + \
              f'Описание: {item.event_description}\n'

    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=item.event_media,
        caption=caption,
        parse_mode="HTML",
    )


def register_handlers_connect(dp: Dispatcher):
    dp.register_message_handler(connect_cancel, state='*', commands='cancel')
    dp.register_message_handler(
        connect_cancel,
        Text(startswith='❌Выйти из чата', ignore_case=True),
        state='*'
    )
    dp.register_callback_query_handler(connect_user, lambda c: c.data.split('_')[0] == 'answeruser', state='*')
    dp.register_callback_query_handler(connect_user, lambda c: c.data == 'connect_owner', state='*')

    dp.register_message_handler(show_event, lambda message: message.text == "Посмотреть событие", state=Form.chat_data)
    dp.register_message_handler(forward_text, content_types=ContentType.TEXT, state=Form.chat_data)
    dp.register_message_handler(forward_sticker, content_types=ContentType.STICKER, state=Form.chat_data)
    dp.register_message_handler(forward_video_note, content_types=ContentType.VIDEO_NOTE, state=Form.chat_data)
    dp.register_message_handler(forward_media_message,
                                content_types=[
                                    ContentType.VOICE,
                                    ContentType.AUDIO,
                                    ContentType.DOCUMENT,
                                    ContentType.VIDEO,
                                    ContentType.PHOTO
                                ],
                                state=Form.chat_data)
    dp.register_message_handler(forward_location, content_types=ContentType.LOCATION, state=Form.chat_data)
