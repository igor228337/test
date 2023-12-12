from fastapi.testclient import TestClient
from FASTAPI.main import app, logger, async_db_session
import asyncio


async def main():
    await async_db_session.init()

asyncio.run(main())
client = TestClient(app)


def test_get_token():
    response = client.post("/token", data={"username": "Ilya", "password": "123", "grant_type": "", "scope": "",
                                           "client_id": "", "client_secret": ""},
                           headers={"content-type": "application/x-www-form-urlencoded"})
    logger.info(response)
    assert response.status_code == 200
    response_data = response.json()
    logger.info(response_data)

