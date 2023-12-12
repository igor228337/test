import asyncio

from DATABASE.main import User, async_db_session
from FASTAPI.security.password_methods import get_password_hash


async def main():
    await async_db_session.init()
    login = "Ilya"
    password = "123"
    password_hash = await get_password_hash(password)
    await User.create(User(login=login, password=password_hash, disabled=False))


if __name__ == '__main__':
    asyncio.run(main())
