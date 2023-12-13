from fastapi import FastAPI
from FASTAPI.roters.auth import (user, async_db_session, base, logger, TransactionModel, Depends, UserModel,
                                 get_current_active_user, HTTPException, status, Transaction, User, HTMLSession,
                                 SimpleCookie, cookiejar_from_dict, Connect)
import time

app = FastAPI()


@user.post("/transaction", status_code=201)
async def get_data(request: TransactionModel = Depends(TransactionModel),
                   current_user: UserModel = Depends(get_current_active_user)):
    if request.login.find(": ") >= 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=request.login.split(": ")[-1])
    elif type(request.many) is not float:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=request.many)

    user_l = await User.get_user(login=current_user.login)
    logger.info(f"Создан запрос на транзакцию для пользователя: {user_l.login}")
    await Transaction.create(Transaction(login=request.login, many=request.many, status="Waiting",
                                         login_user_id=user_l.id))
    trans = await Transaction.get_user(login=request.login)
    return {status.HTTP_201_CREATED: "Создан", "id_trans": trans.id}


@user.post("/pay")
async def pay_qmany(id_trans: int, current_user: UserModel = Depends(get_current_active_user)):
    user_l_l = await User.get_user(current_user.login)
    trans = await Transaction.get_tranc(id_l=id_trans)
    my_cookie = SimpleCookie()
    my_cookie.load(user_l_l.cookies)
    cookies = {key: morsel.value for key, morsel in my_cookie.items()}

    json_data = [
    {
        'operationName': 'GetProductPrice',
        'variables': {
            'titleCode': 'ru.wot',
            'code': 'ps_p_34',
            'quantity': int(trans.many),
        },
        'query': 'query GetProductPrice($title: String, $titleCode: String, $code: String!, $recipient: String, $quantity: Int, $isGift: Boolean, $couponCode: String, $storefront: String) {\n  product_price(\n    title: $title\n    title_code: $titleCode\n    code: $code\n    receiver_wgid: $recipient\n    quantity: $quantity\n    is_gift: $isGift\n    coupon_code: $couponCode\n    storefront: $storefront\n  ) {\n    price {\n      real_price {\n        amount\n        currency_code\n        original_amount\n        discount {\n          amount\n          pct\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    rewards {\n      product {\n        product_id\n        product_code\n        name\n        purchasable\n        price_type\n        client_payment_method_ids\n        categories\n        coupon_codes\n        giftable\n        tags\n        __typename\n      }\n      __typename\n    }\n    client_payment_method_ids\n    coupon_codes\n    __typename\n  }\n}\n',
    },
]
    import requests

    headers = {
        'authority': 'shop-graphql-ru.lesta.ru',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {cookies.get("wgnps_shop_jwt")}',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://lesta.ru',
        'pragma': 'no-cache',
        'referer': 'https://lesta.ru/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-request-id': 'e1d0d1fa-2072-4f3f-b533-35f6cfa8ee1e',
    }

    response_many = requests.post('https://shop-graphql-ru.lesta.ru/a801b41b2a10890ede2653b33746c93e', headers=headers,
                                  json=json_data)
    try:
        response_many = response_many.json()[0]["data"]["product_price"]["price"]["real_price"]["amount"]
    except:
        return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Не удалось")
    json_data = [
        {
            'operationName': 'GiftRecipients',
            'variables': {
                'usernamePrefix': f'{trans.login}',
                'titleCode': 'ru.wot',
            },
            'query': 'query GiftRecipients($usernamePrefix: String!, $titleCode: String!) {\n  gift_recipients('
                     'username_prefix: $usernamePrefix, title_code: $titleCode) {\n    wgid\n    username\n    '
                     '__typename\n  }\n}\n',
        },
    ]
    response = requests.post('https://shop-graphql-ru.lesta.ru/a801b41b2a10890ede2653b33746c93e', headers=headers,
                             json=json_data)
    a = ""
    try:
        id_chel = response.json()[0]['data']["gift_recipients"]
    except:
        return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Не удалось 2")
    for x in id_chel:
        if x["username"] == trans.login:
            a = x["wgid"]
            break
    print(a)
    json_data = [
        {
            'operationName': 'PurchaseProduct',
            'variables': {
                'client_payment_method_id': 4,
                'expected_price_amount': f"{response_many}",
                'expected_price_currency_code': 'RUB',
                'product_code': 'ps_p_34',
                'title_code': 'ru.wot',
                'meta': {
                    'cid': None,
                    'tid': None,
                    'timestamp': f"{time.time()}".replace(".", ""),
                    'session_id': None,
                },
                "receiver_wgid": a,
                'product_quantity': int(trans.many),
            },
            'query': 'mutation PurchaseProduct($client_payment_method_id: Int!, $coupon_code: String, '
                     '$expected_price_amount: String!, $expected_price_currency_code: String!, $gift_message: String, '
                     '$meta: PurchaseMeta, $product_code: String!, $product_quantity: Int, $receiver_wgid: String, '
                     '$storefront: String, $title_code: String!) {\n  purchase_product(\n    purchase_input: {'
                     'client_payment_method_id: $client_payment_method_id, coupon_code: $coupon_code, '
                     'expected_price_amount: $expected_price_amount, expected_price_currency_code: '
                     '$expected_price_currency_code, gift_message: $gift_message, meta: $meta, product_code: '
                     '$product_code, product_quantity: $product_quantity, receiver_wgid: $receiver_wgid, storefront: '
                     '$storefront, title_code: $title_code}\n  ) {\n    ... on PurchaseProductSuccess {\n      '
                     'order_id\n      redirect_url\n      transaction_id\n      __typename\n    }\n    ... on '
                     'PurchaseProductFailure {\n      code\n      context\n      __typename\n    }\n    __typename\n  '
                     '}\n}\n',
        },
    ]
    response = requests.post('https://shop-graphql-ru.lesta.ru/a801b41b2a10890ede2653b33746c93e', headers=headers,
                             json=json_data)
    pay_url = response.json()[0]['data']['purchase_product']['redirect_url']
    pay_form = requests.get(pay_url, allow_redirects=True)
    sk = Connect.get_sk(pay_form.text)
    order_id = Connect.get_client_id(pay_form.url)
    Connect.pay(order_id, sk, cookies=user_l_l.cookies_wallet)
    return status.HTTP_202_ACCEPTED


app.include_router(user)
app.include_router(base)

logger.info("Все роутера подключены")
