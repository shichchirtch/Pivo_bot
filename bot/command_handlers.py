from aiogram import Router, F, html
import asyncio
import pickle
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command, StateFilter
from beer_collection import *
from database import user_dict, users_db
from filters import PRE_START, IS_ADMIN, EXIT_FILTER, EXCLUDE_COMMAND
from lexicon import *
from postgress_function import *
from copy import deepcopy
from aiogram.fsm.context import FSMContext
from keyboards import pre_start_clava
from aiogram.exceptions import TelegramBadRequest
from asyncio import sleep
from FSM_states import FSM_ST
from beer_art_class import bier_dict, Beer_Art
from contextlib import suppress
from inline_keyboard import *
ch_router = Router()



@ch_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    if not await check_user_in_table(user_id):
        await insert_new_user_in_table(user_id, user_name)
        users_db[message.from_user.id] = deepcopy(user_dict)
        await state.set_state(FSM_ST.after_start)
        await message.answer(text=f'{html.bold(html.quote(user_name))}, '
                                  f'Добро пожаловать в Пиво-Бота !\n'
                                  f'Чтобы узнать о моих возможнотях нажмите\n\n /help',
                             parse_mode=ParseMode.HTML,
                             reply_markup=ReplyKeyboardRemove())
    else:
        users_db[message.from_user.id] = deepcopy(user_dict) # Просто создаю юзеру БД для сообщений
        await message.answer('Бот перезапущен на сервере')

@ch_router.message(PRE_START())
async def before_start(message: Message):
    prestart_ant = await message.answer(text='Нажми на кнопку <b>start</b> !',
                                        reply_markup=pre_start_clava)
    await message.delete()
    await asyncio.sleep(8)
    await prestart_ant.delete()

@ch_router.message(StateFilter(FSM_ST.after_start), Command('help'))
async def process_help(message: Message):
    att = await message.answer(help_text)
    await message.delete()
    await asyncio.sleep(30)
    await att.delete()


@ch_router.message(Command('exit'))
async def exit_review(message: Message, state: FSMContext):
    user_id = message.from_user.id
    users_db[user_id]['look_now'] = ''
    await state.update_data(name='', foto='', desc='')
    temp_msg = users_db[user_id]['temp_msg']
    if temp_msg:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()

    temp_msg = users_db[user_id]['zagruz_reply']
    if temp_msg:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['zagruz_reply']
            await temp_message.delete()
    users_db[user_id]['zagruz_reply'] = ''
    await asyncio.sleep(1.5)
    await message.delete()
    await state.set_state(FSM_ST.after_start)
    att = await message.answer('Вы вышли из режима добавления пива или написания отзыва(((')
    users_db[user_id]['temp_msg'] = att


@ch_router.message(StateFilter(FSM_ST.after_start), Command('add_new_beer'))
async def ask_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    att = await message.answer('Как называется Пиво ?')
    await state.set_state(FSM_ST.add_name)
    await state.set_data({'name':'', 'foto':'', 'desc':'', 'rating': 0, 'comments': [], 'like':0, 'total': 0})
    users_db[user_id]['zagruz_reply'] = att
    users_db[user_id]['zagruz_data'] = message


@ch_router.message(StateFilter(FSM_ST.add_name), F.text, EXIT_FILTER())
async def add_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name_beer = message.text.strip()

    with suppress(TelegramBadRequest):
        msg = users_db[user_id]['zagruz_reply']
        await msg.delete()

    with suppress(TelegramBadRequest):
        msg = users_db[user_id]['zagruz_data']
        await msg.delete()

    temp_msg = users_db[user_id]['temp_msg']
    if temp_msg:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()

    if name_beer.startswith('/'):
        att  = await message.answer('Вы в режиме добавдения пива !\n\nВведите название или нажмите   /exit')
        users_db[user_id]['temp_msg'] = att

    elif name_beer.lower() not in bier_dict['beer_keys']:
        if len(name_beer) > 100:
            name_beer = message.text.strip()[:100]
        await state.set_state(FSM_ST.add_foto)
        await state.update_data(name=name_beer)
        att = await message.answer("Отправьте фотографию !")

        users_db[user_id]['zagruz_data'] = message
        users_db[user_id]['zagruz_reply'] = att

    else:
        att = await message.answer('Такое пиво уже есть !')
        await state.set_state(FSM_ST.after_start)
        await asyncio.sleep(4)
        await message.delete()
        await att.delete()

        users_db[user_id]['zagruz_reply'] = ''
        users_db[user_id]['zagruz_data'] = ''


@ch_router.message(StateFilter(FSM_ST.add_foto), F.photo)
async def add_foto(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(FSM_ST.add_desc)
    foto = message.photo[-1].file_id
    await state.update_data(foto=foto)
    att = await message.answer('Отправьте описание !')

    with suppress(TelegramBadRequest):
        msg = users_db[user_id]['zagruz_data']
        await msg.delete()
    users_db[user_id]['zagruz_data'] = message

    with suppress(TelegramBadRequest):
        msg = users_db[user_id]['zagruz_reply']
        await msg.delete()
    users_db[user_id]['zagruz_reply'] = att


@ch_router.message(StateFilter(FSM_ST.add_desc), F.text, EXCLUDE_COMMAND())
async def add_desc(message: Message, state: FSMContext):
    await state.set_state(FSM_ST.edit_desc)
    user_id = message.from_user.id
    beer_art = await state.get_data()
    beer_name = beer_art['name']
    foto = beer_art['foto']
    desc = message.text
    if len(desc) > 800:
        desc = message.text[:800]

    test_att = await message.answer_photo(photo=foto, caption=desc)
    att = await message.answer('У вас есть  2 минуты, чтобы отредактировать описание !\n\n'
                               'Если не хотите ничего редактировать - просто подождите немного')

    name_plus_desc = f'Пиво <b>{beer_name}</b>\n\n{desc}'


    await state.update_data(desc=desc)
    att2 = await message.answer(f'<b>Ваше описание</b>  ⬇️\n\n{name_plus_desc}')

    await sleep(100)
    current_dict = await state.get_data()
    desc = current_dict['desc']

    if desc != message.text:
        await state.update_data(desc=desc)

    new_beer_art = await state.get_data()
    new_beer_art['desc'] = name_plus_desc


    bier_dict[beer_name] = Beer_Art(name=beer_name, foto=foto, descripion=name_plus_desc)
    print('beer_name = ', beer_name)
    bier_dict.get('beer_keys', []).append(beer_name.lower()) # Добавляю пиво в список названий, чтобы потом оттуда его доставать, сверять и т.д
    test = bier_dict[beer_name]
    print('test.comments = ', test.comments, 'test.name = ', test.name)
    await state.set_state(FSM_ST.after_start)

    with suppress(TelegramBadRequest):
        msg = users_db[user_id]['zagruz_data']
        await msg.delete()
    users_db[user_id]['zagruz_data'] = ''

    with suppress(TelegramBadRequest):
        msg = users_db[user_id]['zagruz_reply']
        await msg.delete()
    users_db[user_id]['zagruz_reply'] = ''

    await state.update_data(name='', foto='', desc='')
    await message.delete()
    await att.delete()
    await att2.delete()
    await test_att.delete()


@ch_router.message(StateFilter(FSM_ST.edit_desc), F.text, EXCLUDE_COMMAND())
async def edit_desc(message: Message, state: FSMContext):
    beer_art = await state.get_data()
    foto = beer_art['foto']
    print('edit desc works')
    desc = message.text
    if len(desc) > 800:
        desc = message.text[:800]
    await state.update_data(desc=desc) # Перезаписываю описание в редис
    att = await message.answer_photo(photo=foto, caption=desc)
    await asyncio.sleep(10)
    await message.delete()
    await att.delete()


@ch_router.message(StateFilter(FSM_ST.add_desc, FSM_ST.add_foto, FSM_ST.add_name))
async def something_goes_wrong(message: Message, state: FSMContext):
    print('something_goes_wrong')
    user_id = message.from_user.id
    users_db[user_id]['look_now'] = ''


    temp_msg = users_db[user_id]['zagruz_reply']
    if temp_msg:
        with suppress(TelegramBadRequest):
            msg = users_db[user_id]['zagruz_reply']
            await msg.delete()

    temp_msg = users_db[user_id]['zagruz_data']
    if temp_msg:
        with suppress(TelegramBadRequest):
            msg = users_db[user_id]['zagruz_data']
            await msg.delete()

    users_db[user_id]['zagruz_reply'] = ''
    users_db[user_id]['zagruz_data'] = ''
    await state.update_data(name='', foto='', desc='')
    await state.set_state(FSM_ST.after_start)
    att = await message.answer(wrong_add_new_beer)
    await asyncio.sleep(4)
    await message.delete()
    await att.delete()


@ch_router.message(StateFilter(FSM_ST.after_start), Command('show_collection'))
async def show_collection(message: Message):
    user_id = message.from_user.id
    users_db[user_id]['beer_index'] = 1
    temp_msg = users_db[user_id]['temp_msg']
    if temp_msg:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
        users_db[user_id]['temp_msg'] = ''

    star_msg = users_db[user_id]['star_msg']
    if star_msg:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['star_msg']
            await temp_message.delete()
        users_db[user_id]['star_msg'] = ''

    star_msg = users_db[user_id]['zagruz_reply']
    if star_msg:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['zagruz_reply']
            await temp_message.delete()
        users_db[user_id]['zagruz_reply'] = ''


    if bier_dict:
        quantity_arts = len(bier_dict)-1
        vull_collection = f'{beer_collection}\nОбщее количество сортов - <b>{quantity_arts}</b>'
        if len(bier_dict)<101:
            att = await message.answer(
                text=vull_collection,
                reply_markup=create_beer_collection_keyboard(*bier_dict.keys()))
            users_db[user_id]['zagruz_reply'] = att
        else:
            key_list = []
            for x in bier_dict.keys():
                key_list.append(x)

            first_hundred = key_list[:100]
            rest = key_list[100:]
            att = await message.answer(
                text=beer_collection,
                reply_markup=create_beer_collection_keyboard(*first_hundred))

            att2 = await message.answer(
                text=vull_collection,
                reply_markup=create_beer_collection_keyboard(*rest))
            users_db[user_id]['zagruz_data'] = att2
            users_db[user_id]['zagruz_reply'] = att
    await message.delete()



@ch_router.message(StateFilter(FSM_ST.write_review), F.content_type.in_({'photo', 'text'}), EXCLUDE_COMMAND())
async def write_review(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    current_time = message.date.date().strftime("%d.%m.%Y")
    current_beer = users_db[user_id]['look_now']

    temp_message = users_db[user_id]['zagruz_reply']
    if temp_message:
        with suppress(TelegramBadRequest):
            await temp_message.delete()
        users_db[user_id]['zagruz_reply'] = ''

    if message.text:
        new_review = message.text
        full_review = f'🔸 {new_review}\n\n{current_time}\n{user_name}'

        nedeed_beer = bier_dict[current_beer] # Получаю ЭК Beer_Art
        otzyv_list = nedeed_beer.comments
        updated_list = otzyv_list + [full_review]
        nedeed_beer.comments = updated_list
        print('nedeed_beer.comments = ', nedeed_beer.comments)

    else:
        foto_id = message.photo[-1].file_id
        print('foto_id = ', foto_id)
        capcha = message.caption
        full_capcha = f'🔸 {capcha}\n\n{current_time}\n{user_name}'

        nedeed_beer = bier_dict[current_beer]  # Получаю ЭК Beer_Art
        otzyv_list = nedeed_beer.comments
        updated_list = otzyv_list + [(foto_id, full_capcha,)]
        nedeed_beer.comments = updated_list
        print('nedeed_beer.comments = ', nedeed_beer.comments)

    att = await message.answer(successfully_add, reply_markup=create_one_button_keyboard(current_beer))

    await insert_otzyv(user_id, current_beer)

    temp_message = users_db[user_id]['temp_msg']
    if temp_message:
        with suppress(TelegramBadRequest):
            await temp_message.delete()
        users_db[user_id]['temp_msg'] = ''

    users_db[user_id]['look_now'] = ''
    await state.set_state(FSM_ST.after_start)
    await asyncio.sleep(5)
    await att.delete()
    await message.delete()


@ch_router.message(Command('catalog'), StateFilter(FSM_ST.after_start))
async def catalog_beer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    index = users_db[user_id]['beer_index']
    start_beer_key = bier_dict['beer_keys'][index]
    start_beer_art = bier_dict[start_beer_key.capitalize()]
    name_beer = start_beer_art.name

    desc = f'<b>{name_beer}</b>\n\n{start_beer_art.description}\n\nRating  {start_beer_art.rating}\n\nReview {len(start_beer_art.comments)}'
    start_page = await message.answer_photo(
                photo=start_beer_art.foto,
                caption=desc,
                reply_markup=create_pagination_keyboard_cat(name_beer, index)
            )

    users_db[user_id]['zagruz_data'] = start_page


@ch_router.message(Command('poisk'), StateFilter(FSM_ST.after_start))
async def poisk_beer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(FSM_ST.poisk)
    att = await message.answer('Какое Пиво ищете ?\nВведите название')
    users_db[user_id]['zagruz_data'] = message
    users_db[user_id]['zagruz_reply'] = att



@ch_router.message(StateFilter(FSM_ST.poisk), F.text, EXCLUDE_COMMAND())
async def get_beer_info(message: Message, state: FSMContext):
    user_id = message.from_user.id
    art_beer = message.text.strip()

    msg = users_db[user_id]['zagruz_data']
    if msg:
        with suppress(TelegramBadRequest):
            await msg.delete()
        users_db[user_id]['zagruz_data'] = ''

    otvet = users_db[user_id]['zagruz_reply']

    if otvet:
        with suppress(TelegramBadRequest):
            await otvet.delete()
        users_db[user_id]['zagruz_reply'] = ''

    if art_beer.lower() in bier_dict['beer_keys']:
        users_db[user_id]['look_now'] = art_beer
        if art_beer not in bier_dict:
            art_beer = art_beer.capitalize()
            if art_beer not in bier_dict:
                art_beer = art_beer.upper()
                if art_beer not in bier_dict:
                    art_beer_split = art_beer.split()
                    if len(art_beer_split)==2:
                        t_1 = art_beer_split[0].capitalize()
                        t_2 = art_beer_split[1].capitalize()
                        art_beer = t_1 + ' '+ t_2
                        if art_beer not in bier_dict:
                            await message.answer('Название этого пива записано иначе, найдитe его сами в коллекции')
                            await state.set_state(FSM_ST.after_start)

                    else:
                        await message.answer('Название этого пива записано иначе, найдитe его сами в коллекции')
                        await state.set_state(FSM_ST.after_start)

        needed_beer = bier_dict[art_beer]
        foto_beer = needed_beer.foto
        description = needed_beer.description
        rating = needed_beer.rating
        full_desc = f'{description}\n\nРейтинг Пива -   {rating}   Отзывы  # {len(needed_beer.comments)}'

        await message.answer_photo(
            photo=foto_beer, caption=full_desc,
            reply_markup=None)

        returned_otzyv_list = await return_otzyv_list(user_id)
        returned_stars_list = await return_stars_list(user_id)

        if art_beer not in returned_otzyv_list and art_beer not in returned_stars_list:
            temp_att = await message.answer(temp_review_opp, reply_markup=sub_art_keyboard)
            users_db[user_id]['temp_msg'] = temp_att

        elif art_beer in returned_otzyv_list and art_beer not in returned_stars_list:
            temp_att = await message.answer(temp_review_opp_with_stars, reply_markup=ohne_otzyv)
            users_db[user_id]['temp_msg'] = temp_att

        elif art_beer not in returned_otzyv_list and art_beer in returned_stars_list:
            temp_att = await message.answer(temp_review_opp, reply_markup=ohne_stars)
            users_db[user_id]['temp_msg'] = temp_att

        else:
            temp_att = await message.answer(temp_review_opp_ohne_writing, reply_markup=ohne_ohne)
            users_db[user_id]['temp_msg'] = temp_att

    else:
        att = await message.answer(no_beer)
        await asyncio.sleep(3)
        await message.delete()
        await att.delete()

    await state.set_state(FSM_ST.after_start)

############################################ADMIN#############################################

@ch_router.message(Command('admin'), IS_ADMIN())
async def go_to_admin_state(message: Message, state: FSMContext):
    await state.set_state(FSM_ST.admin)
    await message.answer(admin_enter)


@ch_router.message(StateFilter(FSM_ST.admin, FSM_ST.delete_otzyv, FSM_ST.delete_record),Command('dump'))
async def dump_db(message: Message, state:FSMContext):
    with open('save_db.pkl', 'wb') as file:
        pickle.dump(bier_dict, file)
    await message.answer('База данных успешно записана !')
    await state.set_state(FSM_ST.after_start)

@ch_router.message(StateFilter(FSM_ST.admin),Command('load'))
async def load_db(message: Message, state:FSMContext):
    with open('save_db.pkl', 'rb') as file:
        recover_base = pickle.load(file)
        bier_dict.update(recover_base)
    await message.answer('База данных успешно загружена !')
    await state.set_state(FSM_ST.after_start)


@ch_router.message(StateFilter(FSM_ST.admin), Command('delete'))
async def delete_position(message: Message, state:FSMContext):
    await message.answer('Admin will delete now')
    await state.set_state(FSM_ST.delete_record)


@ch_router.message(StateFilter(FSM_ST.delete_record, FSM_ST.delete_otzyv), Command('break'))
async def break_position(message: Message, state:FSMContext):
    await message.answer('Admin out')
    await state.set_state(FSM_ST.after_start)


@ch_router.message(StateFilter(FSM_ST.delete_record), F.text)
async def delete_position(message: Message):
    deleted_record = message.text
    name_list = bier_dict['beer_keys']
    if deleted_record in bier_dict:
        del bier_dict[deleted_record]
        name_list.remove(deleted_record.lower())
        await message.answer('Перезапишите БД, если закончили    /dump\n\n'
                             'если нет - продолжайте удаление\n\n'
                             '/break')
    else:
        await message.answer('Wrong key')

@ch_router.message(StateFilter(FSM_ST.admin), Command('delete_otzyv'))
async def process_delete_otzyv_command(message: Message, state:FSMContext):
    await message.answer('Admin will delete OTZYV now')
    await state.set_state(FSM_ST.delete_otzyv)


@ch_router.message(StateFilter(FSM_ST.delete_otzyv), F.text)
async def delete_otzyv(message: Message):

    key = users_db[message.from_user.id]['look_now']
    needed_art = bier_dict[key]
    otzyv_list = needed_art.comments
    for tayli, otzyv in enumerate(otzyv_list, 0):
        if isinstance(otzyv, str):
            deleted_record = '🔸 ' + message.text
            if otzyv.startswith(deleted_record):
                del otzyv_list[tayli]
                await message.answer('Отзыв удалёт\n\nПерезапишите БД, если закончили    /dump\n\n если нет - продолжайте удаление\n\n'
                                 '/break')
                break
            else:
                await message.answer('Wrong chunk')
        else:
            if otzyv[1].endswith(message.text):
                del otzyv_list[tayli]
                await message.answer('Отзыв удалёт\n\nПерезапишите БД, если закончили   /dump\n\n если нет - продолжайте удаление\n\n'
                                 '/break')
                break
            else:
                await message.answer('Wrong foto chunk')
    needed_art.comments = otzyv_list


@ch_router.message()
async def crush_tresh(message: Message):
    await asyncio.sleep(2)
    await message.delete()

