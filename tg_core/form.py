from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message

from tg_core.basic import (
    get_or_create_db,
    mark_city_used,
    find_city_for_answer,
    current_city_check,
    check_city_in_db
)
from tg_core.statesform import StepsCityForm


async def check_city_status_db(before_city: str, message: Message):
    check_game_rules = await current_city_check(before_city=before_city, message_city=message.text)
    res_status = await check_city_in_db(tg_id=message.from_user.id, city_name=message.text)
    return check_game_rules, res_status


async def start_game(message: Message, state: FSMContext):
    await get_or_create_db(tg_id=message.from_user.id)
    await state.set_state(StepsCityForm.CHECK_CITY)
    await message.answer("Введите город")


async def check_city(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        before_city = data["before_city"]
    except KeyError:
        before_city = None
    db_status = await check_city_status_db(before_city, message)
    if db_status[1]:  # Есть город в базе, True город уже называли, False город еще не называли, None такого города нет
        await message.answer("Этот город уже был")
        await start_game(message, state)
    elif db_status[0] is False:  # Начинается ли введеный город на посл букву предыдущего
        await message.answer(f"Эй твой город: {message.text} не начинается на последнюю "
                                  f"букву предыдущего ответа {before_city}")
        await start_game(message, state)
    elif db_status[1] is False and db_status[0] is True:
        await mark_city_used(tg_id=message.from_user.id, city_name=message.text)
        await message.answer("Отлично, теперь моя очередь")
        await answer_city(message, state)
    elif db_status[1] is None:
        await message.answer(f"{message.text}, Я такого города не нашел, он точно существует?")
        await start_game(message, state)


async def answer_city(message: Message, state: FSMContext):
    city = await find_city_for_answer(tg_id=message.from_user.id, city_name=message.text)
    await message.answer(f"Мой ответ {city}")
    await state.update_data(before_city=city)
    await mark_city_used(tg_id=message.from_user.id, city_name=city)
    await start_game(message, state)
