from aiogram import Router
from filters import *
from aiogram.filters import StateFilter
import asyncio
from beer_art_class import bier_dict
from aiogram.types import  CallbackQuery, InputMediaPhoto
from database import users_db
from aiogram.exceptions import TelegramBadRequest
from beer_collection import create_one_button_keyboard
from lexicon import *
from aiogram.fsm.context import FSMContext
from FSM_states import FSM_ST
from inline_keyboard import *
from contextlib import suppress
from postgress_function import *


inline_router = Router()


@inline_router.callback_query(NAME_CALLBACK_DATA(), StateFilter(FSM_ST.after_start))
async def process_beer_art_press(callback: CallbackQuery):
    """Срабатывает на нажатие на каллбэк кнопку с названием пива"""
    user_id = callback.from_user.id
    print('callbackdata = ', callback.data, type(callback.data))
    users_db[user_id]['look_now'] = callback.data
    beer_key = callback.data  # получаю ключ - названеи пива
    if callback.data in ('Рибачка соня', 'Hacker pschorr', 'Paderborner' , 'Steam brew'):
        beer_key = callback.data.lower()
        users_db[user_id]['look_now'] = callback.data.lower()

    needed_beer = bier_dict[beer_key]  # получаю ЭК Berr_Art
    foto_beer = needed_beer.foto   # Получаю фото
    description = needed_beer.description   #  Получаю описание
    rating = needed_beer.rating   #  получаю рейтинг
    full_desc = f'{description}\n\nРейтинг Пива -   {rating}   Отзывы  # {len(needed_beer.comments)}'

    temp_message = users_db[user_id]['zagruz_reply']
    if temp_message:
        with suppress(TelegramBadRequest):
            await temp_message.delete()
        users_db[user_id]['zagruz_reply'] = ''

    temp_message = users_db[user_id]['zagruz_data']
    if temp_message:
        with suppress(TelegramBadRequest):
            await temp_message.delete()
        users_db[user_id]['zagruz_data'] = ''

    await callback.message.answer_photo(
        photo=foto_beer, caption=full_desc,
        reply_markup=None)

    returned_otzyv_list = await return_otzyv_list(user_id)
    returned_stars_list = await return_stars_list(user_id)

    if beer_key not in returned_otzyv_list and beer_key not in returned_stars_list:
        temp_att = await callback.message.answer(temp_review_opp, reply_markup=sub_art_keyboard)
        users_db[user_id]['temp_msg'] = temp_att

    elif beer_key in returned_otzyv_list and beer_key not in returned_stars_list:
        temp_att = await callback.message.answer(temp_review_opp_with_stars, reply_markup=ohne_otzyv)
        users_db[user_id]['temp_msg'] = temp_att

    elif beer_key not in returned_otzyv_list and beer_key in returned_stars_list:
        temp_att = await callback.message.answer(temp_review_opp, reply_markup=ohne_stars)
        users_db[user_id]['temp_msg'] = temp_att

    else:
        temp_att = await callback.message.answer(temp_review_opp_ohne_writing, reply_markup=ohne_ohne)
        users_db[user_id]['temp_msg'] = temp_att

    await callback.answer(text=to_beer)


@inline_router.callback_query(VIEW_REVIEW(), StateFilter(FSM_ST.after_start))
async def process_show_review(callback: CallbackQuery):
    user_id = callback.from_user.id
    beer_key = users_db[user_id]['look_now']  #  Получаю название рассматриываемого пива
    if callback.data in ('Рибачка соня', 'Hacker pschorr', 'Paderborner', 'Steam brew'):
        beer_key = callback.data.lower()
    needed_beer = bier_dict[beer_key]   #  получаю ЭК Beer_Art
    otzyv_arr = needed_beer.comments  #  прлучаю список отзывов
    if otzyv_arr:  # Если есть отзывы
        for review in otzyv_arr:  #  В цикле перебираю все отзывы
            if isinstance(review, str):
                await callback.message.answer(text=review)  # Отправляю сообщение
                await asyncio.sleep(0.3)
            else:
                await callback.message.answer_photo(photo=review[0], caption=review[1])
                await asyncio.sleep(0.3)
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
        users_db[user_id]['temp_msg'] = ''

    else:
        att = await callback.message.answer(text=no_review_till_now)
        await asyncio.sleep(3)
        await att.delete()

    await callback.answer()


@inline_router.callback_query(WRITE_REVIEW(), StateFilter(FSM_ST.after_start))
async def process_write_review(callback: CallbackQuery, state:FSMContext):
    user_id = callback.from_user.id
    await state.set_state(FSM_ST.write_review)
    att = await callback.message.answer(write_review)
    await callback.answer()
    temp_message = users_db[user_id]['zagruz_reply']
    if temp_message:
        with suppress(TelegramBadRequest):
            await temp_message.delete()
    users_db[user_id]['zagruz_reply'] = att





@inline_router.callback_query(STAR_EVAL(), StateFilter(FSM_ST.after_start))
async def process_star_likes(callback: CallbackQuery):
    print('works process_star_likes\n\n')
    user_id = callback.from_user.id
    att = await callback.message.answer(star_evaluation, reply_markup=star_kb)
    users_db[user_id]['star_msg'] = att
    await callback.answer()


@inline_router.callback_query(FIVE_STAR(), StateFilter(FSM_ST.after_start))
async def process_evaluation(callback: CallbackQuery):
    print('process_evaluation works')
    user_id = callback.from_user.id
    beer_key = users_db[user_id]['look_now']
    add_rating =  int(callback.data)
    needed_beer = bier_dict[beer_key]
    needed_beer.total += add_rating
    needed_beer.like += 1
    current_rating = round(needed_beer.total/needed_beer.like, 2)
    needed_beer.rating = current_rating
    att = await callback.message.answer(evaluate_successully, reply_markup=create_one_button_keyboard(beer_key))

    await insert_stars(user_id, beer_key)

    with suppress(TelegramBadRequest):
        temp_message = users_db[user_id]['temp_msg']
        await temp_message.delete()
    users_db[user_id]['temp_msg'] = ''

    with suppress(TelegramBadRequest):
        star_message = users_db[user_id]['star_msg']
        await star_message.delete()
    users_db[user_id]['star_msg'] = ''
    await callback.answer(text=danke)
    await asyncio.sleep(4)
    await att.delete()


@inline_router.callback_query(MOVE_PAGE())
async def page_moving(callback: CallbackQuery):
    print(f'{callback.data = }')
    user_id = callback.from_user.id
    shift = -1 if callback.data == 'backward' else 1
    print('shift = ', shift)
    us_beer_index = users_db[user_id]['beer_index'] + shift
    if us_beer_index == (len(bier_dict['cat'])):
        us_beer_index = 0
    if us_beer_index == -1:
        us_beer_index = (len(bier_dict['cat'])-1)
    users_db[user_id]['beer_index'] = us_beer_index

    beer_art_name = bier_dict['cat'][us_beer_index]
    print('beer_art_name = ', beer_art_name)
    beer_art = bier_dict[beer_art_name]
    beer_art_id = beer_art.foto
    name_beer = beer_art.name
    desc = f'<b>{name_beer}</b>\n\n{beer_art.description}\n\nRating  <b>{beer_art.rating}</b>\n\nReview <b>{len(beer_art.comments)}</b>'
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=beer_art_id, caption=desc),
            reply_markup=create_pagination_keyboard_cat(name_beer, us_beer_index)
        )
    except TelegramBadRequest:
        print('Into Exeption')
    await callback.answer()
