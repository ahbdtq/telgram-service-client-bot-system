"""
This module describes a state machine for adding events to the database
"""

import logging.config
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType


from db.db_commands import db_get_max_event_id
from db.models import EventTable
import handlers.keyboards as keyb

logging.config.fileConfig(fname=r'logger.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


# States
class Form(StatesGroup):
    event_name = State()  # Will be represented in storage as 'Form:name'
    event_header = State()  # Will be represented in storage as 'Form:header'
    event_description = State()  # Will be represented in storage as 'Form:description'
    event_media = State() # Will be represented in storage as 'Form:media'
    event_end_show_date = State() # Will be represented in storage as 'Form:end_show_date'


async def add_event(message: types.Message):
    """
    Conversation's entry point
    """
    await message.answer(
        f"Вы создаете событие:",
        reply_markup=keyb.keyboard_reply_get(keyb.KEYBOARD_CANCEL))

    # Set state
    await Form.event_name.set()
    await message.answer("Имя события")


async def process_event_name(message: types.Message, state: FSMContext):
    """
    Process event name amd query header
    """
    async with state.proxy() as data:
        data['event_name'] = message.text

    await Form.next()
    await message.answer("Заголовок:")


async def process_header(message: types.Message, state: FSMContext):
    # Process header and query description
    await Form.next()
    await state.update_data(event_header=message.text)

    await message.answer("Описание:")


async def process_description(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(event_description=message.text)

    await message.answer("Медиа")


async def process_media(message: types.Message, state: FSMContext):
    """
    Process media file.
    Save media to disk.
    Save data from FSM to DB.
    Send FSM data to chat.
    Finish FSM.
    """
    logger.info('enter to process_media func')
    await state.update_data(event_media=message.photo[-1].file_id)
    await message.photo[-1].download()
    await state.update_data(event_end_show_date='')

    user_data = await state.get_data()
    db_session = message.bot.get("db")

    async with db_session() as session:
        async with session.begin():
            max_id = await session.run_sync(db_get_max_event_id)
        new_event_id = max_id + 1

        await session.merge(
            EventTable(
                event_id=new_event_id,
                user_id=message.from_user.id,
                event_name=user_data['event_name'],
                event_header=user_data['event_header'],
                event_description=user_data['event_description'],
                event_media=user_data['event_media'],
                event_end_show_date=user_data['event_end_show_date']
            )
        )
        await session.commit()

    await message.answer_photo(user_data['event_media'])
    await message.answer(
        f"Имя: {user_data['event_name']}\n" +
        f"Заголовок: {user_data['event_header']}\n" +
        f"Описание: {user_data['event_description']}\n" +
        f"Дата окончания показа:{user_data['event_end_show_date']}",
        reply_markup=keyb.keyboard_reply_get(keyb.KEYBOARD_MAIN))
    await message.answer(f"Вы создали событие👆👆👆\n" +
                         f"Для того, что бы получать уведомления о сообщениях перейдите в \n" +
                         f"@test_211009_server_bot")
    # Finish conversation
    await state.finish()


async def unknown_message(msg: types.Message):
    """
    informs the user if he sent unsupported media
    """
    await msg.reply('Я не знаю, что с этим делать, пришлите Фото')


async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logger.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


def register_handlers_add_event(dp: Dispatcher):
    dp.register_message_handler(cancel_handler, state='*', commands='cancel')
    dp.register_message_handler(
        cancel_handler,
        Text(equals='❌ Отменить операцию', ignore_case=True),
        state='*'
    )
    dp.register_message_handler(
        add_event,
        lambda message: message.text == "Добавить событие",
    )
    dp.register_message_handler(process_event_name, state=Form.event_name)
    dp.register_message_handler(process_header, state=Form.event_header)
    dp.register_message_handler(process_description, state=Form.event_description)
    dp.register_message_handler(
        process_media,
        content_types=["photo"],
        state=Form.event_media
    )
    dp.register_message_handler(unknown_message, content_types=ContentType.ANY)
