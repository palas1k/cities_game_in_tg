from aiogram.fsm.state import StatesGroup, State


class StepsCityForm(StatesGroup):
    START_GAME = State()
    CHECK_CITY = State()
    GET_ANSWER = State()
