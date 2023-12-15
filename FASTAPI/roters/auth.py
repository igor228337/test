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
        elif user_l_l.cookies is None and user_l_l.cookies_wallet is None:
            return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=Messages.HAVE_ACC_NO_COOKIE)
    elif cookies is not None and user_l_l is None:
        password_hash = await get_password_hash(user_l.password)
        await User.create(User(login=user_l.login, password=password_hash, cookies=cookies, disabled=False,
                               cookies_wallet=cookies_wallet))
    elif cookies is not None or cookies_wallet is not None:
        if cookies is not None:
            await User.update(login=user_l.login, cookies=cookies)
        if cookies_wallet is not None:
            await User.update(login=user_l.login, cookies_wallet=cookies_wallet)
    user_l_l = await User.get_user(user_l.login)
    # if user_l_l.cookies is None or user_l_l.disabled is True:
    #     return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=Messages.NO_COOKIES)
    session = HTMLSession()
    my_cookie = SimpleCookie()
    my_cookie.load(user_l_l.cookies)
    cookies = {key: morsel.value for key, morsel in my_cookie.items()}
    session.cookies = cookiejar_from_dict(cookies)
    headers = {
        'authority': 'lesta.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        # 'cookie': 'wgnps_shop_language=ru; wgnps_shop_csrftoken=W8P3TGMNJoX9OHpmKKxaleEJShycyzTl6aCZHnS7txAxZUDB51k4DotaNVWvoYnd; wgnps_shop_sessionid=43rv8zw344wagj11a0v6ktgns70vc271; wgnps_shop_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IjJpZ29yMl8iLCJqdGkiOiIyOTU2MjQ2YjM2MTdiYjhlMzhlMDU4MjgxYzA0Y2IyMiIsImhhc19lbWFpbCI6dHJ1ZSwiZXhwIjoxNzAyNjI3MTI4LCJsYW5ndWFnZSI6InJ1Iiwic2NvcGUiOltdLCJpc3MiOiJ1cm46d2FyZ2FtaW5nOnBzcyIsImNvdW50cnkiOiJSVSIsInNwYV9pZCI6MjUxMzcyODB9.OQa0svKDdfdierGqGNP37wXHIt1YVVBltNRbYX7n9n4; teclient=1698329257857556405; cm.internal.bs_id=ceda802e-05fa-4e21-541c-3ecae22d5796; _ga=GA1.1.773897348.1698329438; _ym_uid=1698329439346472504; _ym_d=1698329439; cm.internal.realm=ru; _gcl_au=1.1.1265256523.1702368555; wgnp_language=ru; wgn_realm=ru; wgn_geowidget_popup=true; wgnp_csrftoken=D5HYISF8xVTHHbAbkngVEhV70Ts3nMjOfZPLx2AFD9faTeuuKeK7Al0U7cNNHdzq; tmr_lvid=42ca65c32e8fa420e3b953dd7cd481ee; tmr_lvidTS=1702385566296; lesta-cb-accepted=1; _ym_isad=1; _ym_visorc=b; pss_b7f8235d=61727173defb573aedcec0bdc5894227; pss_a05a4e6e=6976; wgn_account_is_authenticated=yes; wgnp_auth_sso_attempt_immediate=yes; django_language=ru; wgni_use_browser_history_update=Z7OJHEdynirMFTiHYWQtZcpufGUcedn1; reg_ref_domain=www.google.com; tspaid=5jygk41dyQISO-1FOBuGSbRUQXxkLED20-rbmBb5Dzctbr7G1FRqtiu06azOaqrQqKNErOZiuBhE8DArAbbfWg; tmr_detect=1%7C1702541805229; cm.internal.spa_id=25137280; _ga_1B6BTKKQ1V=GS1.1.1702540687.11.1.1702542421.0.0.0',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://lesta.ru/shop/wot/gold/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    session.headers = headers
    result = session.get(BaseData.site, allow_redirects=True)

    try:
        names = re.search(r"window.Settings.USERNAME = '.+?'", result.text)
        print(names[0].split("=")[1].split("&")[0])
    except TypeError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.NO_COOKIES)

    return {status.HTTP_200_OK: "good"}

# @user.get("/me/items/")
# async def get_items(current_user: UserModel = Depends(get_current_active_user)):
#     return {"item_id": "Оуу май", "owner": current_user.login}
