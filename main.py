import asyncio

from FASTAPI.main import app, async_db_session, logger
import uvicorn


async def main() -> None:
    await async_db_session.init()


if __name__ == '__main__':
    asyncio.run(main())
    logger.info("Инициализация бд успешна, запускаю сервер!")
    uvicorn.run(app, port=8082)


