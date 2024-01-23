import asyncio
import os

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import select, Column, BigInteger, PickleType
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()
Base = declarative_base()


class AsyncDBSession:
    name_admin_db: str = os.getenv('DB_ADMIN')  # Имя админа
    password_db: str = os.getenv('DB_PASS')
    ip_db: str = os.getenv('DB_HOST')
    port_db: str = os.getenv('DB_PORT')
    name_db: str = os.getenv('DB_NAME')
    connect_db: str = f"{name_admin_db}:{password_db}@{ip_db}:{port_db}/{name_db}"

    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    async def init(self):
        self._engine = create_async_engine(f"postgresql+asyncpg://{self.connect_db}", echo=True)
        self._session = async_sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


async_db_session = AsyncDBSession()
asyncio.run(async_db_session.init())


class MethodClassAll:
    @classmethod
    async def create(cls, acc) -> None:
        async_db_session.add(acc)
        await async_db_session.commit()

    @classmethod
    async def update(cls, tg_id: int, **kwargs):
        query = (
            sqlalchemy.sql.update(cls)
            .where(cls.tg_id == tg_id)
            .values(**kwargs)
            .execution_options(synchronize_session='fetch')
        )
        await async_db_session.execute(query)
        await async_db_session.commit()

    @classmethod
    async def get(cls, tg_id: int):
        query = select(cls).where(cls.tg_id == tg_id)
        res = await async_db_session.execute(query)
        try:
            (res,) = res.one()
        except NoResultFound:
            res = None
        return res


class MethodClassUser(MethodClassAll):
    @classmethod
    async def find_city(cls, tg_id: int, city_name: str):
        query = select(cls).where(cls.tg_id == tg_id)
        res = await async_db_session.execute(query)
        try:
            (data,) = res.one()
            cities_dict = data.cities
            city_status = cities_dict.get(city_name)
        except NoResultFound:
            city_status = None
        return city_status



    @classmethod
    async def find_city_for_answer(cls, tg_id: int, city_name: str):
        query = select(cls).where(cls.tg_id == tg_id)
        last_letter = [city_name[-1] if city_name[-1]not in 'ьъы' else city_name[-2]]
        res = await async_db_session.execute(query)
        try:
            (cities,) = res.one()
            cities_dict = cities.cities
            res = [city for city, value in cities_dict.items()
                   if city.startswith(last_letter[0].upper()) and not value][0]
            return res
        except NoResultFound:
            res = None
        return res


class GameSession(Base, MethodClassUser):
    __tablename__ = "game_session"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger)
    cities = Column(PickleType)

    def __init__(self, tg_id: int, cities: str):
        self.tg_id = tg_id
        self.cities = cities

    def __repr__(self):
        return f"ID: {self.id}, TG_ID: {self.tg_id}"
