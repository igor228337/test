from loguru import logger

logger.add("./out.log", format="{time} {level} {message}", level="INFO", rotation="100 MB", enqueue=True)


class BaseData:
    site_signin: str = "https://lesta.ru/id/signin/process/?type=pow"
    site: str = "https://lesta.ru"
    name_admin_db: str = "postgres"  # Имя админа
    password_db: str = "Vfnhtif1"  # Пароль бд
    ip_db: str = "localhost"  # IP бд
    name_db: str = "zadanie1"  # Имя бд
    connect_db: str = f"{name_admin_db}:{password_db}@{ip_db}/{name_db}"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Секретный ключ для шифрования
    ALGORITHM: str = "HS256"  # Алгоритм шифрования
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Время жизни токена
