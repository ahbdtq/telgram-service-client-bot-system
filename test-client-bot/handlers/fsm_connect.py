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


async def connect_event_owner(query: types.CallbackQuery, state: FSMContext):
    """

    Conversation's entry point

    """
    await Form.chat_data.set()
    await state.update_data(chat_data=query)

    event_id = query.message.caption.split(f'\n')[1]
    event_title = event_id[event_id.find(':') + 1:]
    await query.message.answer(
        f"Вы вошли в чат с владельцем события:{event_title}",
        reply_markup=keyb.keyboard_reply_get(keyb.KEYBOARD_CHAT)
    )


async def connect_cancel(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logger.info('Cancelling chat')
    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Cancelled.', reply_markup=keyb.keyboard_reply_get(keyb.KEYBOARD_MAIN))


async def prepare_vars(message: types.Message, state: FSMContext):
    """
    Prepare vars for sending message to event owner
    """
    state_data = await state.get_data()
    event_id = state_data['chat_data'].message.caption.split(f'\n')[0]
    event_id = int(event_id[event_id.find(':') + 1:])
    item = await db_get_item_by_id(message.bot.get("db"), event_id)

    tmp_var_chat_id = item.user_id

    url = f"{config.CLIENT_BOT_URL}looktoid_{str(item.event_id)}"
    keyboard = InlineKeyboardMarkup()
    button_list1 = [
        InlineKeyboardButton(
            text="Ответить",
            callback_data=f"answeruser_{message.chat.id}"
        ),
        InlineKeyboardButton(
            text="Посмотреть событие",
            url=url
        )
    ]
    keyboard.row(*button_list1)

    text_ = f"Сообщение:{item.event_name},\n" + \
            f"{message.from_user.first_name} {message.from_user.last_name}:" + \
            f"{message.text}"

    return text_, tmp_var_chat_id, keyboard


async def forward_text(message: types.Message, state: FSMContext):
    """
    Forwards text message to Service Bot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    with message.bot.with_token(config.SERVICE_TOKEN):
        await message.bot.send_message(
            chat_id=chat_id_,
            text=text_,
            reply_markup=keyboard
        )


async def forward_photo(message: types.Message, state: FSMContext):
    """
    Forwards photo message to Service Bot.
    Each bot has its own file_id.
    Need to download the file with ClientBot then upload ane
    with ServiceBot.
    Most of the media have the same feature
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)

    photo_file = await message.photo[-1].download()
    with message.bot.with_token(config.SERVICE_TOKEN):
        photo_file = types.InputFile(os.path.abspath(os.curdir)+'/'+photo_file.name)
        await message.bot.send_photo(
            chat_id=chat_id_,
            photo=photo_file,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_audio(message: types.Message, state: FSMContext):
    """
    Forwards media message to Service Bot.
    Some media have the same message structure. Maybe it makes sense for them to make a factory.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.audio.download()
    with message.bot.with_token(config.SERVICE_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_audio(
            chat_id=chat_id_,
            audio=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_document(message: types.Message, state: FSMContext):
    """
    Forwards media message to Service Bot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.document.download()
    with message.bot.with_token(config.SERVICE_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_document(
            chat_id=chat_id_,
            document=file_,
            caption=text_,
            reply_markup=keyboard
        )




async def forward_sticker(message: types.Message, state: FSMContext):
    """
    Forwards media message to Service Bot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    with message.bot.with_token(config.SERVICE_TOKEN):
        await message.bot.send_sticker(
            chat_id=chat_id_,
            sticker=message.sticker.file_id,
            reply_markup=keyboard
        )


async def forward_video(message: types.Message, state: FSMContext):
    """
    Forwards media message to Service Bot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.video.download()
    with message.bot.with_token(config.SERVICE_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_video(
            chat_id=chat_id_,
            video=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_video_note(message: types.Message, state: FSMContext):
    """
    Forwards media message to Service Bot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.video_note.download()
    with message.bot.with_token(config.SERVICE_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_video_note(
            chat_id=chat_id_,
            video_note=file_,
            reply_markup=keyboard
        )


async def forward_voice(message: types.Message, state: FSMContext):
    """
    Forwards media message to Service Bot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.voice.download()
    with message.bot.with_token(config.SERVICE_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_voice(
            chat_id=chat_id_,
            voice=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_animation(message: types.Message, state: FSMContext):
    """
    Forwards media message to Service Bot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.animation.download()
    with message.bot.with_token(config.SERVICE_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_animation(
            chat_id=chat_id_,
            animation=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_location(message: types.Message, state: FSMContext):
    """
    Forwards media message to Service Bot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    with message.bot.with_token(config.SERVICE_TOKEN):
        await message.bot.send_location(
            chat_id=chat_id_,
            longitude=message.location.longitude,
            latitude=message.location.latitude,
            reply_markup=keyboard
        )


async def show_event(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    event_id = state_data['chat_data'].message.caption.split(f'\n')[0]
    event_id = int(event_id[event_id.find(':') + 1:])
    item = await db_get_item_by_id(message.bot.get("db"), event_id)
    caption = f'Событие#: {item.event_id}\n' + \
              f'Заголовок: {item.event_header}\n' + \
              f'Описание: {item.event_description}\n'
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=item.event_media,
        caption=caption,
        parse_mode="HTML"
    )


def register_handlers_connect_to_owner(dp: Dispatcher):
    dp.register_message_handler(connect_cancel, state='*', commands='cancel')
    dp.register_message_handler(
        connect_cancel,
        Text(equals='❌Выйти из чата', ignore_case=True),
        state='*'
    )
    dp.register_callback_query_handler(connect_event_owner, lambda c: c.data == 'connect_owner')
    dp.register_message_handler(
        show_event,
        Text(equals='Посмотреть событие', ignore_case=True),
        state=Form.chat_data
    )
    dp.register_message_handler(forward_text, content_types=ContentType.TEXT, state=Form.chat_data)
    dp.register_message_handler(forward_audio, content_types=ContentType.AUDIO, state=Form.chat_data)
    dp.register_message_handler(forward_animation, content_types=ContentType.ANIMATION, state=Form.chat_data)
    dp.register_message_handler(forward_document, content_types=ContentType.DOCUMENT, state=Form.chat_data)
    dp.register_message_handler(forward_photo, content_types=ContentType.PHOTO, state=Form.chat_data)
    dp.register_message_handler(forward_sticker, content_types=ContentType.STICKER, state=Form.chat_data)
    dp.register_message_handler(forward_video, content_types=ContentType.VIDEO, state=Form.chat_data)
    dp.register_message_handler(forward_video_note, content_types=ContentType.VIDEO_NOTE, state=Form.chat_data)
    dp.register_message_handler(forward_voice, content_types=ContentType.VOICE, state=Form.chat_data)
    dp.register_message_handler(forward_location, content_types=ContentType.LOCATION, state=Form.chat_data)
