from postgress_table import session_marker, User
from sqlalchemy import select

async def insert_new_user_in_table(user_tg_id: int, name: str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        if not needed_data:
            print('Now we are into first function')
            new_us = User(tg_us_id=user_tg_id, user_name=name)
            session.add(new_us)
            await session.commit()


async def check_user_in_table(user_tg_id:int):
    """Функция проверяет есть ли юзер в БД"""
    async with session_marker() as session:
        print("Work check_user Function")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        data = query.one_or_none()
        return data

async def insert_otzyv(user_tg_id: int, otzyv:str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('works insert_otzyv')
        otzyv_list = needed_data.otzyv_beer
        updated_otzyv_list = otzyv_list + [otzyv]
        needed_data.otzyv_beer = updated_otzyv_list
        await session.commit()

async def insert_stars(user_tg_id: int, otzyv:str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('works insert_stars')
        star_list = needed_data.evaluated_beer
        updated_star_list = star_list + [otzyv]
        needed_data.evaluated_beer = updated_star_list
        await session.commit()

async def return_otzyv_list(user_tg_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        return needed_data.otzyv_beer

async def return_stars_list(user_tg_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        return needed_data.evaluated_beer