from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import requests
from http.cookies import SimpleCookie
from requests.cookies import cookiejar_from_dict


class Connect:

    @staticmethod
    def get_sk(html):
        soup = BeautifulSoup(html, 'html.parser')
        script_tags = soup.find_all('script')
        for script_tag in script_tags:
            script_content = script_tag.string
            if script_content and '__secretKey__' in script_content:
                secret_key_start = script_content.find('__secretKey__') + len('__secretKey__') + 3
                secret_key_end = script_content.find('"', secret_key_start)
                secret_key = script_content[secret_key_start:secret_key_end]
                return secret_key

    @staticmethod
    def get_client_id(url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('orderid', [None])[0]

    @staticmethod
    def pay(order_id, sk, cookies):
        my_cookie = SimpleCookie()
        my_cookie.load(cookies)
        cookies = {key: morsel.value for key, morsel in my_cookie.items()}
        cookies = cookiejar_from_dict(cookies)
        headers = {
            'authority': 'yoomoney.ru',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://yoomoney.ru',
            # 'referer': 'https://yoomoney.ru/checkout/payments/v2/contract/wallet?orderid=2d0b9df8-000f-5000-8000-19af4be2d07a',
            'sec-ch-ua': '"Chromium";v="118", "YaBrowser";v="23", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.731 YaBrowser/23.11.1.731 Yowser/2.5 Safari/537.36',
        }

        json_data = {
            'orderId': order_id,
            'sk': sk,
        }

        response = requests.post(
            'https://yoomoney.ru/checkout/payments/v2/payment/wallet/start',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        print(response.text)
        response = requests.post(
            'https://yoomoney.ru/checkout/payments/v2/payment/status',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        print(response.text)

