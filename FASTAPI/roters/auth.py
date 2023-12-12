import fake_useragent
from fastapi import Response, APIRouter
from DATABASE.main import async_db_session
from FASTAPI.security.token import (Depends, HTTPException, status, UserModel, User, logger, get_current_active_user,
                                    OAuth2PasswordRequestForm, Token, authenticate_user, Messages, timedelta, BaseData,
                                    create_access_token, TransactionModel, Transaction)
from FASTAPI.connect_site.main import Connect, HTMLSession

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


#  Вот тут, убрал части кода которые идут дальше
@user.post("/login")
async def auth_site(user_l: UserModel = Depends()):
    session = HTMLSession()
    session.headers["User-agent"] = fake_useragent.UserAgent().random
    print(session.headers)
    result = Connect.get_site(session, BaseData.site)
    print(result)
    print(session.headers)
    session.headers["Origin"] = BaseData.site
    data = {"pow": "вот хз откуда и как он берётся", "login": "", "password": "", "rememeber": "true", "captcha": "",
            "remember": "on", "next": "/id/sso/signin/notify/?next=/"}
    result = Connect.post_site(session, BaseData.site_signin, data=data)
    print(result)
    print(result.text)
    print(session.headers)


# @user.get("/me/items/")
# async def get_items(current_user: UserModel = Depends(get_current_active_user)):
#     return {"item_id": "Оуу май", "owner": current_user.login}
