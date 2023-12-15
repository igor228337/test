import asyncio
from http.cookies import SimpleCookie

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import json


async def get_url_id(cookies: dict) -> list[str, str]:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    options.add_argument('--mute-audio')
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.set_capability(
                            "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
                        )
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get('https://lesta.ru/shop/wot/gold/ps_p_34/')
    for i in cookies:
        driver.add_cookie(i)
    driver.get('https://lesta.ru/shop/wot/gold/ps_p_34/')
    WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "item-header_image"))
        )
    WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div/div[4]/div[1]/div/div[2]/div[1]/div/div/span/button[1]"))
        ).click()

    urls = []
    x_request_ids = []
    log_entries = driver.get_log("performance")
    for entry in log_entries:
        try:
            obj_serialized: str = entry.get("message")
            obj = json.loads(obj_serialized)
            message = obj.get("message")
            method = message.get("method")
            if method in "Network.responseReceived":
                try:
                    if "https://shop-graphql-ru.lesta.ru" in message["params"]["response"]["url"]:
                        url = message["params"]["response"]["url"]
                        x_request_id = message["params"]["response"]["headers"]["x-request-id"]
                        urls.append(url)
                        x_request_ids.append(x_request_id)
                except KeyError:
                    continue
            else:
                continue

        except Exception as e:
            raise e from None
    driver.quit()
    return [urls[-1], x_request_ids[-1]]


# a = """wgnps_shop_language=ru; wgnps_shop_sessionid=xpml4mls80jxo15yzbhm9qrnl84iyoct; wgnps_shop_csrftoken=WTcDZrObuOp2zFigA3d5jguPCe9YuRCpdGo3Wjv5aGtdrAEnqY2BEZ4BoJt25aCM; wgnps_shop_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IjJpZ29yMl8iLCJqdGkiOiI4OTU5YmVkNjkwNzViZGVhOTdjZGRhNzM0MGI4YzUzNyIsImhhc19lbWFpbCI6dHJ1ZSwiZXhwIjoxNzAyNjU1NzE5LCJsYW5ndWFnZSI6InJ1Iiwic2NvcGUiOltdLCJpc3MiOiJ1cm46d2FyZ2FtaW5nOnBzcyIsImNvdW50cnkiOiJSVSIsInNwYV9pZCI6MjUxMzcyODB9.yR3hylhA0kiYHj1TYzq00V1ida8tDGW8Dvxe-ML6guQ; teclient=1698329257857556405; cm.internal.bs_id=ceda802e-05fa-4e21-541c-3ecae22d5796; _ga=GA1.1.773897348.1698329438; _ym_uid=1698329439346472504; _ym_d=1698329439; cm.internal.realm=ru; _gcl_au=1.1.1265256523.1702368555; wgnp_language=ru; wgn_realm=ru; wgn_geowidget_popup=true; wgnp_csrftoken=D5HYISF8xVTHHbAbkngVEhV70Ts3nMjOfZPLx2AFD9faTeuuKeK7Al0U7cNNHdzq; tmr_lvid=42ca65c32e8fa420e3b953dd7cd481ee; tmr_lvidTS=1702385566296; lesta-cb-accepted=1; _ym_isad=1; wgn_account_is_authenticated=yes; wgnp_auth_sso_attempt_immediate=yes; STIDREFERRAL=SIDUMcfG6Vb1IDXo_vbXSr82ISBvKyJfyw3ruW2azuNTyIV9SrdYSy-YuzvhMQcN8c6w17Tpzl8Wmov18W3uZOy7UfD0h7u9WRXik2PECb2_vdzNdFs3-h5PdUaZ-rAwv16tQ; enctid=cxo6fqn7wlm2; django_language=ru; wgni_use_browser_history_update=Ax2Ek48OAulgK7Zq6g2j5gnYPedPbVDn; tspaid=5yqVW7uMpX8IOoWwordEbb3WMq8y_voC80idSaI7sKQ5TM3NFoatrNl-pDgD-MJSwz2064FTOu9aBw44janV3Q; tmr_detect=1%7C1702571055211; cm.internal.spa_id=25137280; _ga_1B6BTKKQ1V=GS1.1.1702575824.14.0.1702575824.0.0.0; pss_b7f8235d=61727173defb573aedcec0bdc5894227; pss_a05a4e6e=6976"""
# my_cookie = SimpleCookie()
# my_cookie.load(a)
#
# cookies_d: dict = [{"name": key, "value": morsel.value} for key, morsel in my_cookie.items()]
#
# async def main():
#     print(await get_url_id(cookies_d))
#
# asyncio.run(main())
