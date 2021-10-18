import logging.config
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.message import ContentType

import config

logging.config.fileConfig(fname=r'logger.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class Form(StatesGroup):
    chat_data = State()


async def connect_user(query: types.CallbackQuery, state: FSMContext):
    await Form.chat_data.set()
    await state.update_data(chat_data=query)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(f"❌Выйти из чата c {query.message.chat.first_name} {query.message.chat.last_name}")

    await query.message.answer(
        f"Вы вошли в чат с:{query.message.chat.first_name} {query.message.chat.last_name}",
        reply_markup=keyboard
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
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


async def prepare_vars(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    event_name = state_data['chat_data'].message.html_text.split(f'\n')[0]
    event_name = event_name[event_name.find(':') + 1:]
    keyboard = InlineKeyboardMarkup()
    button_list1 = [
        InlineKeyboardButton(
            text="Ответить",
            callback_data="connect_owner"
        ),
        InlineKeyboardButton(
            text="Посмотреть событие",
            callback_data="Посмотреть событие"

        )
    ]
    keyboard.row(*button_list1)
    text_ = f"Сообщение от владельца события {event_name}\n" + \
        f"{message.text}"
    tmp_var_chat_id = state_data['chat_data'].data.split(f'_')[1]
    return text_, tmp_var_chat_id, keyboard


async def forward_text(message: types.Message, state: FSMContext):
    """
    Forwards text message to ClientBot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    with message.bot.with_token(config.CLIENT_TOKEN):
        await message.bot.send_message(
            chat_id=chat_id_,
            text=text_,
            reply_markup=keyboard
        )


async def forward_photo(message: types.Message, state: FSMContext):
    """
    Forwards photo message to ClientBot.
    Each bot has its own file_id.
    Need to download the file with ClientBot then upload ane
    with ServiceBot.
    Most of the media have the same feature
    """

    text_, chat_id_, keyboard = await prepare_vars(message, state)

    photo_file = await message.photo[-1].download()
    with message.bot.with_token(config.CLIENT_TOKEN):
        photo_file = types.InputFile(os.path.abspath(os.curdir)+'/'+photo_file.name)
        await message.bot.send_photo(
            chat_id=chat_id_,
            photo=photo_file,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_audio(message: types.Message, state: FSMContext):
    """
    Forwards media message to ClientBot.
    Some media have the same message structure. Maybe it makes sense for them to make a factory.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.audio.download()
    with message.bot.with_token(config.CLIENT_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_audio(
            chat_id=chat_id_,
            audio=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_document(message: types.Message, state: FSMContext):
    """
    Forwards media message to ClientBot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.document.download()
    with message.bot.with_token(config.CLIENT_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_document(
            chat_id=chat_id_,
            document=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_sticker(message: types.Message, state: FSMContext):
    """
    Forwards media message to ClientBot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    with message.bot.with_token(config.CLIENT_TOKEN):
        await message.bot.send_sticker(
            chat_id=chat_id_,
            sticker=message.sticker.file_id,
            reply_markup=keyboard
        )


async def forward_video(message: types.Message, state: FSMContext):
    """
    Forwards media message to ClientBot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.video.download()
    with message.bot.with_token(config.CLIENT_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_video(
            chat_id=chat_id_,
            video=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_video_note(message: types.Message, state: FSMContext):
    """
    Forwards media message to ClientBot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.video_note.download()
    with message.bot.with_token(config.CLIENT_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_video_note(
            chat_id=chat_id_,
            video_note=file_,
            reply_markup=keyboard
        )


async def forward_voice(message: types.Message, state: FSMContext):
    """
    Forwards media message to ClientBot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.voice.download()
    with message.bot.with_token(config.CLIENT_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_voice(
            chat_id=chat_id_,
            voice=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_animation(message: types.Message, state: FSMContext):
    """
    Forwards media message to ClientBot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    file_ = await message.animation.download()
    with message.bot.with_token(config.CLIENT_TOKEN):
        file_ = types.InputFile(os.path.abspath(os.curdir)+'/'+file_.name)
        await message.bot.send_animation(
            chat_id=chat_id_,
            animation=file_,
            caption=text_,
            reply_markup=keyboard
        )


async def forward_location(message: types.Message, state: FSMContext):
    """
    Forwards media message to ClientBot.
    """
    text_, chat_id_, keyboard = await prepare_vars(message, state)
    with message.bot.with_token(config.CLIENT_TOKEN):
        await message.bot.send_location(
            chat_id=chat_id_,
            longitude=message.location.longitude,
            latitude=message.location.latitude,
            reply_markup=keyboard
        )



def register_handlers_connect_to_owner(dp: Dispatcher):
    dp.register_message_handler(connect_cancel, state='*', commands='cancel')
    dp.register_message_handler(
        connect_cancel,
        Text(startswith='❌Выйти из чата', ignore_case=True),
        state='*'
    )
    dp.register_callback_query_handler(connect_user, lambda callback: callback.data.split('_')[0] == 'answeruser')
    dp.register_message_handler(forward_text, content_types=ContentType.TEXT, state=Form.chat_data)
    dp.register_message_handler(forward_audio, content_types=ContentType.AUDIO, state=Form.chat_data)
    dp.register_message_handler(forward_document, content_types=ContentType.DOCUMENT, state=Form.chat_data)
    dp.register_message_handler(forward_photo, content_types=ContentType.PHOTO, state=Form.chat_data)
    dp.register_message_handler(forward_sticker, content_types=ContentType.STICKER, state=Form.chat_data)
    dp.register_message_handler(forward_video, content_types=ContentType.VIDEO, state=Form.chat_data)
    dp.register_message_handler(forward_video_note, content_types=ContentType.VIDEO_NOTE, state=Form.chat_data)
    dp.register_message_handler(forward_voice, content_types=ContentType.VOICE, state=Form.chat_data)
    dp.register_message_handler(forward_location, content_types=ContentType.LOCATION, state=Form.chat_data)
