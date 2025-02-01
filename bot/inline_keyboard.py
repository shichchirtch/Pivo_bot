from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# def create_pagination_keyboard(page=1) -> InlineKeyboardMarkup:
#     print('We are into create_pagination_keyboard')
#     forward_button = InlineKeyboardButton(text=f'>>', callback_data='forward')
#     # middle_button = InlineKeyboardButton(text=f'{page} / {len(pagin_dict)}', callback_data=f'{page} / {len(pagin_dict)}')
#     backward_button = InlineKeyboardButton(text='<<', callback_data='backward')
#     if page == 1:
#         pagination_keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[[forward_button]])
#         return pagination_keyboard
#     elif 1 < page < 10: # pagin_dict
#         pagination_keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[[backward_button, forward_button]])
#         return pagination_keyboard
#     else:
#         pagination_keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[[backward_button]])
#         return pagination_keyboard


otzyv_button = InlineKeyboardButton(text='Посмотреть отзывы', callback_data='view_review')
add_otzyv = InlineKeyboardButton(text='Написать отзыв', callback_data='write_review' )
star_likes = InlineKeyboardButton(text='Оценить от  ⭐️   до   ⭐️⭐️⭐️⭐️⭐️', callback_data='star_likes' )

sub_art_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[otzyv_button], [star_likes], [ add_otzyv]])


ohne_stars = InlineKeyboardMarkup(
            inline_keyboard=[[otzyv_button], [ add_otzyv]])

ohne_otzyv = InlineKeyboardMarkup(
            inline_keyboard=[[otzyv_button], [star_likes]])

ohne_ohne = InlineKeyboardMarkup(
            inline_keyboard=[[otzyv_button]])

###########################################################################

one_star =  InlineKeyboardButton(text='⭐️', callback_data='1')
two_star =  InlineKeyboardButton(text='⭐️⭐', callback_data='2')
three_star =  InlineKeyboardButton(text='⭐️⭐️⭐️', callback_data='3')
four_star =  InlineKeyboardButton(text='⭐️⭐️⭐️⭐️', callback_data='4')
five_star =  InlineKeyboardButton(text='⭐️⭐️⭐️⭐️⭐️', callback_data='5')

star_kb= InlineKeyboardMarkup(
            inline_keyboard=[[five_star], [four_star],[three_star], [two_star], [one_star]])


















