from requests_html import HTMLSession


class Connect:
    @staticmethod
    def get_site(session: HTMLSession, url: str):
        r = session.get(url)
        return r

    @staticmethod
    def post_site(session: HTMLSession, url: str, data: dict):
        r = session.post(url, data=data)
        return r

