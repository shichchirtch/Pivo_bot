from aiogram.types import CallbackQuery, Message
from aiogram.filters import BaseFilter
from beer_art_class import bier_dict
from postgress_function import check_user_in_table


class PRE_START(BaseFilter):
    async def __call__(self, message: Message):
        print("PRE_START Filter works")
        user_tg_id = message.from_user.id
        if await check_user_in_table(user_tg_id):
            return False
        return True

class NAME_CALLBACK_DATA(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data in bier_dict:
            return True
        return False


class VIEW_REVIEW(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data == 'view_review':
            return True
        return False

class WRITE_REVIEW(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data == 'write_review':
            return True
        return False



class STAR_EVAL(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data == 'star_likes':
            return True
        return False

class FIVE_STAR(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data in ('1', '2', '3', '4','5'):
            return True
        return False



class IS_ADMIN(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id == 6685637602:
            return True
        return False


class EXIT_FILTER(BaseFilter):
    async def __call__(self, message: Message):
        if message.text == '/exit':
            return False
        return True


class EXCLUDE_COMMAND(BaseFilter):
    async def __call__(self, message: Message):
        if message.text:
            if message.text in ('/show_collection', '/add_new_beer', '/poisk', '/help'):
                return False
            elif message.text.startswith('/show_collection') or message.text.endswith('/show_collection'):
                return False

            elif message.text.startswith('/add_new_beer') or message.text.endswith('/add_new_beer'):
                return False

            elif message.text.startswith('/poisk') or message.text.endswith('/poisk'):
                return False

            elif message.text.startswith('/help') or message.text.endswith('/help'):
                return False
            else:
                return True
        else:
            return True










