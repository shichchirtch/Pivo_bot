from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis, StorageKey
from config import settings

using_redis = Redis(host=settings.REDIS_HOST)
redis_storage = RedisStorage(redis=using_redis)


class FSM_ST(StatesGroup):
    after_start = State()
    add_name = State()
    add_foto = State()
    add_desc = State()
    edit_desc = State()
    write_review = State()
    admin=State()
    delete_record = State()
    poisk = State()
    delete_otzyv = State()

