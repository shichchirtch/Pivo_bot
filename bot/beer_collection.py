from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_beer_collection_keyboard(*args) -> InlineKeyboardMarkup:
    # Создаем объект клавиатуры
    kb_builder = InlineKeyboardBuilder()
    # Наполняем клавиатуру кнопками-закладками в порядке возрастания

    for button in sorted(args):
        if button != 'beer_keys':
            kb_builder.row(InlineKeyboardButton(
                text=button,
                callback_data=button))
    return kb_builder.as_markup()


def create_one_button_keyboard(beer_name) -> InlineKeyboardMarkup:
    # Создаем объект клавиатуры
    kb_builder = InlineKeyboardBuilder()
    # Наполняем клавиатуру кнопками-закладками в порядке возрастания

    kb_builder.row(InlineKeyboardButton(
        text=beer_name,
        callback_data=beer_name))
    return kb_builder.as_markup()

