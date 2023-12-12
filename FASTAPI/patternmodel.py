from pydantic import (
    BaseModel,
    field_validator, confloat
)


class TransactionModel(BaseModel):
    login: str
    many: confloat(gt=99)

    @field_validator('login')
    @classmethod
    def name_is_not_none(cls, v: str) -> str:
        if v is None or v == " ":
            return f'{v}: Логин не должен быть пустым'
        return v

    @field_validator('many')
    @classmethod
    def many_is_float(cls, v: str) -> float | str:
        try:
            v = float(v)
        except ValueError:
            return "Это должно быть число"
        if v < 100:
            return "Число не должно быть меньше 100"
        return v


class UserModel(BaseModel):
    login: str
    password: str
    disabled: bool | None = None

    @field_validator('login', 'password')
    @classmethod
    def valid_login_password(cls, v: str) -> str:
        if v is None or v == " ":
            return f'{v}: Логин или пароль не должен быть пустым'
        return v


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    login: str | None = None


class QIWIDataForm(BaseModel):
    number_phone_qiwi: str
    token_qiwi_wallet: str
    many_int: str
    many_float: str
    currency: str = "643"
