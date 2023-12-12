import asyncio

from BASEFOLDER.base import BaseData
from sqlalchemy import Column, BigInteger, String, ForeignKey, Float, DateTime, Boolean

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select
import sqlalchemy.exc


Base = declarative_base()


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    async def init(self):
        self._engine = create_async_engine(f"postgresql+asyncpg://{BaseData.connect_db}", echo=True)
        self._session = async_sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


async_db_session = AsyncDatabaseSession()


class MethodClass:
    @classmethod
    async def get_all(cls):
        query = select(cls)
        results = await async_db_session.execute(query)
        return results.all()

    @classmethod
    async def create(cls, acc) -> None:
        async_db_session.add(acc)
        await async_db_session.commit()

    @classmethod
    async def get_user(cls, login: str):
        query = select(cls).where(cls.login == login)
        result = await async_db_session.execute(query)
        try:
            (result,) = result.one()
        except sqlalchemy.exc.NoResultFound:
            result = None
        return result


class Transaction(Base, MethodClass):
    __tablename__ = 'transaction'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    login = Column(String, nullable=False)
    many = Column(Float, nullable=False)
    status = Column(Boolean, nullable=False)
    qiwi_trans: Mapped[list["QIWITransaction"]] = relationship()

    def __init__(self, login: str = None, many: float = None, status: bool = None):
        super().__init__()
        self.login = login
        self.many = many
        self.status = status


class QIWITransaction(Base, MethodClass):
    __tablename__ = "qiwitransaction"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    status = Column(Boolean, nullable=False)
    trans: Mapped[int] = mapped_column(ForeignKey("transaction.id"), nullable=False)


class User(Base, MethodClass):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    login = Column(String)
    password = Column(String)
    disabled = Column(Boolean)

    def __init__(self, login: str = None, password: str = None, disabled: bool = False):
        super().__init__()
        self.login = login
        self.password = password
        self.disabled = disabled

# async def main():
#     await async_db_session.init()
#     await async_db_session.create_all()
#
# if __name__ == '__main__':
#     asyncio.run(main())
