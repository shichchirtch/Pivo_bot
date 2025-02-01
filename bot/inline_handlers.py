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
    beer_key = callback.data   # получаю ключ - названеи пива
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
    brack_list = ['Жигули Export', 'Natakhtari Gold', 'Чешский Старовар',
                  'Букет Чувашии Пшеничное', 'Львовское', 'Чуваш Тест', 'Лев', 'natakhtari gold']
    shift = -1 if callback.data == 'backward' else 1
    print('shift = ', shift)
    beer_key_list = bier_dict['beer_keys']
    us_beer_index = users_db[user_id]['beer_index'] + shift
    users_db[user_id]['beer_index'] = us_beer_index
    print(*beer_key_list, sep='\n')
    beer_art_name = beer_key_list[us_beer_index]
    print('beer_art_name = ', beer_art_name)
    if beer_art_name in ('лвiвске', 'Чуваш Тест', 'Лев','львов', 'Букет Чувашии Леди Ночь', '/poisk',
                         'Lav', 'lav','чуваш тест', 'Букет Чувашии Леди Ночь'.lower(), 'хз', 'львов', 'mixery' ):
        beer_key_list.remove(beer_art_name)
        print('pivo deleted')
        beer_art_name = beer_key_list[us_beer_index+4]
        shift  = shift+4
        users_db[user_id]['beer_index'] = us_beer_index+4

    if ' ' in beer_art_name:
        temp = beer_art_name.split()
        s = ''
        for teil in temp:
            s+=teil.capitalize()+' '
        beer_art_name = s[:-1]
    else:
        beer_art_name = beer_art_name.capitalize()

    if beer_art_name in brack_list:
        if beer_art_name == 'Жигули Export':
            beer_art_name = 'Жигули EXPORT'
        elif beer_art_name == 'natakhtari gold':
            beer_art_name = 'Natakhtari GOLD'.upper()
        elif beer_art_name == 'Чешский Старовар':
            beer_art_name = 'Чешский старовар'
        elif beer_art_name == 'Букет Чувашии Пшеничное':
            beer_art_name = 'Букет Чувашии пшеничное'
        elif beer_art_name == 'Львовское':
            beer_art_name = 'Львiвске'

    # if beer_art_name not in bier_dict:
    #     print('us_beer_index', us_beer_index)
    #     us_beer_index = users_db[user_id]['beer_index'] + shift
    #     print('us_beer_index', us_beer_index)
    #     users_db[user_id]['beer_index'] = us_beer_index
    #     beer_art_name = beer_key_list[us_beer_index]
    #     if ' ' in beer_art_name:
    #         temp = beer_art_name.split()
    #         s = ''
    #         for teil in temp:
    #             s += teil.capitalize() + ' '
    #         beer_art_name = s[:-1]
    #     else:
    #         beer_art_name = beer_art_name.capitalize()

        # if beer_art_name in brack_list:
        #     if beer_art_name == 'Жигули Export':
        #         beer_art_name = 'Жигули EXPORT'
        #     elif beer_art_name == 'Natakhtari Gold':
        #         beer_art_name = 'Natakhtari GOLD'
        #     elif beer_art_name == 'Чешский Старовар':
        #         beer_art_name = 'Чешский старовар'
        #     elif beer_art_name == 'Букет Чувашии Пшеничное':
        #         beer_art_name = 'Букет Чувашии пшеничное'
        #     elif beer_art_name == 'Львовское':
        #         beer_art_name ='Львiвске'



    beer_art = bier_dict[beer_art_name]
    beer_art_id = beer_art.foto
    name_beer = beer_art.name
    desc = f'<b>{name_beer}</b>\n\n{beer_art.description}\n\nRating  {beer_art.rating}\n\nReview {len(beer_art.comments)}'
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=beer_art_id, caption=desc),
            reply_markup=create_pagination_keyboard_cat(name_beer, us_beer_index)
        )
    except TelegramBadRequest:
        print('Into Exeption')
    await callback.answer()
