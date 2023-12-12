from typing import Type

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from BASEFOLDER.base import BaseData, logger
from DATABASE.main import User, Transaction
from FASTAPI.security.password_methods import verify_password
from Messages import Messages
from FASTAPI.patternmodel import UserModel, TokenData, Token, TransactionModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, BaseData.SECRET_KEY, algorithm=BaseData.ALGORITHM)
    return encoded_jwt


async def db_in_model_user(user):
    user_model = UserModel
    user_model.login = user.login
    user_model.password = user.password
    user_model.disabled = user.disabled
    return user_model


async def authenticate_user(login: str, password: str):
    user = await User.get_user(login=login)
    user_model = await db_in_model_user(user)
    verify = await verify_password(password, user.password)
    if not user:
        return False
    if not verify:
        return False
    return user_model


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=Messages.NOT_VALIDATE,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, BaseData.SECRET_KEY, algorithms=[BaseData.ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = TokenData(login=login)
    except JWTError:
        raise credentials_exception
    user = await User.get_user(login=token_data.login)
    user_model = await db_in_model_user(user)
    if user is None:
        raise credentials_exception
    return user_model


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail=Messages.INACTIVE)
    return current_user
