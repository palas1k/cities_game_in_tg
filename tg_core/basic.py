import asyncio
from typing import Any

import pandas as pd

from db import GameSession


def get_data_from_xls():
    path = 'spisok.xlsx'
    df = pd.read_excel(path)
    return dict(df.values)


async def clone_db_for_user(tg_id: int) -> None:
    try:
        data = get_data_from_xls()
        await GameSession.create(GameSession(tg_id=tg_id, cities=data))
    except Exception as ex:
        raise ex


async def check_city_in_db(tg_id: int, city_name: str) -> bool:
    r = await GameSession.find_city(tg_id=tg_id, city_name=city_name)
    return r


async def mark_city_used(tg_id: int, city_name: str) -> None:
    data = await GameSession.get(tg_id=tg_id)
    cities = data.cities
    cities.update({city_name: True})
    await GameSession.update(tg_id=tg_id, cities=cities)


async def check_db(tg_id: int):
    return await GameSession.get(tg_id=tg_id)


async def find_city_for_answer(tg_id: int, city_name: str):
    return await GameSession.find_city_for_answer(tg_id=tg_id, city_name=city_name)


async def current_city_check(before_city: Any, message_city):
    if before_city is None:
        return True
    elif before_city[-1] not in 'ьъыЬЪЫ' and before_city[-1] == message_city[0].lower():
        return True
    elif before_city[-1] in 'ьъыЬЪЫ':
        await current_city_check(before_city[0:-1], message_city)
    else:
        return False


async def get_or_create_db(tg_id: int):
    if await check_db(tg_id=tg_id) is None:
        await clone_db_for_user(tg_id=tg_id)


#asyncio.run(clone_db_for_user(411635386))
