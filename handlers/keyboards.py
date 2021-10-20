"""
This module describes most of the keyboards
"""
from aiogram import types
from aiogram.utils.callback_data import CallbackData

KEYBOARD_MAIN = ["Каталог", "Добавить событие"]
KEYBOARD_CANCEL = ["❌ Отменить операцию"]
KEYBOARD_CONNECT = ["Связаться"]
KEYBOARD_DELETE_EVENT = ["❌ Удалить событие"]
KEYBOARD_ANSWER = ["Ответить"]
KEYBOARD_LOOK_EVENT = ["Посмотреть событие"]
KEYBOARD_CHAT = ["❌Выйти из чата", "Посмотреть событие"]

catalog_callback = CallbackData("catalog", "page", "to_page")


def keyboard_reply_get(button_set) -> types.ReplyKeyboardMarkup:
    """
    Return keyboard according to button_set

    @param button_set: List

    @rtype: types.ReplyKeyboardMarkup

    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    return keyboard.add(*button_set)


def keyboard_catalog_get(is_owner: bool) -> types.InlineKeyboardMarkup:
    """
    Return
    """
    keyboard = types.InlineKeyboardMarkup()
    button_list = [
        types.InlineKeyboardButton(
            text="Связаться",
            callback_data="connect_owner"
        )
    ]
    if is_owner:
        button_list.append(
            types.InlineKeyboardButton(
                text="❌ Удалить событие",
                callback_data="delete_event_confirmation"
            )
        )
    keyboard.row(*button_list)  # .row(*button_list1)
    return keyboard


def keyboard_catalog_delete_confirmation() -> types.InlineKeyboardMarkup:
    """
    return confirmation keyboard

    @rtype: types.InlineKeyboardMarkup
    """
    keyboard = types.InlineKeyboardMarkup()  # row_width=3
    button_list = [
        types.InlineKeyboardButton(
            text="❌ Удалить событие",
            callback_data="delete_event"
        ),
        types.InlineKeyboardButton(
            text="Вернуться в каталог",
            callback_data="cancel_delete"
        )
    ]
    keyboard.row(*button_list)
    return keyboard


def keyboard_catalog_show_more(pages: int, page: int) -> types.InlineKeyboardMarkup:
    """
    return "more" - buttons ["+1","+5"] if are items to show

    @param pages: int amount of items in catalog
    @param page: int current page number

    @rtype: types.InlineKeyboardMarkup
    """
    keyboard = types.InlineKeyboardMarkup()  # row_width=3
    button_list = []
    if pages > page + 1:
        button_list.append(
            types.InlineKeyboardButton(
                text="+1",
                callback_data=catalog_callback.new(page=page, to_page=page + 1)
            )
        )
    if pages > page + 5:
        button_list.append(
            types.InlineKeyboardButton(
                text="+5",
                callback_data=catalog_callback.new(page=page, to_page=page + 5)
            )
        )
    keyboard.row(*button_list)
    return keyboard
