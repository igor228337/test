import fake_useragent
from fastapi import Response, APIRouter
from DATABASE.main import async_db_session
from FASTAPI.security.token import (Depends, HTTPException, status, UserModel, User, logger, get_current_active_user,
                                    OAuth2PasswordRequestForm, Token, authenticate_user, Messages, timedelta, BaseData,
                                    create_access_token, TransactionModel, Transaction, get_password_hash)
from FASTAPI.connect_site.main import Connect, HTMLSession, SimpleCookie, cookiejar_from_dict

import re

user = APIRouter(prefix="/users", tags=["users"])
base = APIRouter(prefix="", tags=["token"])


# @user.get("/me/", response_model=UserModel)
# async def get_me(current_user: UserModel = Depends(get_current_active_user)):
#     return current_user


@base.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_l: UserModel = await authenticate_user(form_data.username, form_data.password)
    if not user_l:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Messages.BAD_DATA,
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=BaseData.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user_l.login}, expires_delta=access_token_expires
    )
    logger.info(f"Создан токен для пользователя: {user_l.login}")
    return {"access_token": access_token, "token_type": "bearer"}


@user.post("/login")
async def auth_site(user_l: UserModel = Depends(), cookies: str = None, cookies_wallet: str = None):
    user_l_l = await User.get_user(user_l.login)
    if cookies is None or cookies_wallet is None:
        if user_l_l is None:
            return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=Messages.NO_ACC_NO_COOKIE)
        elif user_l_l.cookie is None or user_l_l.cookies_wallet:
            return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=Messages.HAVE_ACC_NO_COOKIE)
    elif cookies is not None and user_l_l is None:
        password_hash = await get_password_hash(user_l.password)
        await User.create(User(login=user_l.login, password=password_hash, cookies=cookies, disabled=False,
                               cookies_wallet=cookies_wallet))
    # if user_l_l.cookies is None or user_l_l.disabled is True:
    #     return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=Messages.NO_COOKIES)
    session = HTMLSession()
    my_cookie = SimpleCookie()
    my_cookie.load(cookies)
    cookies = {key: morsel.value for key, morsel in my_cookie.items()}
    session.cookies = cookiejar_from_dict(cookies)
    session.headers["User-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    result = session.get(BaseData.site)
    try:
        names = re.search(r"user_name.+?&", result.text)
        print(names[0].split("=")[1].split("&")[0])
    except IndexError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.NO_COOKIES)

    return {status.HTTP_200_OK: "good"}

# @user.get("/me/items/")
# async def get_items(current_user: UserModel = Depends(get_current_active_user)):
#     return {"item_id": "Оуу май", "owner": current_user.login}
