import requests


class HhApiClient:
    BASE_URL = 'https://api.hh.ru'

    def __init__(self):
        self.session = requests.Session()
        # self.session.headers = {
        #     'User-Agent': 'MyApp/1.0 (my-app-feedback@example.com)',
        # }

    def search_vacancies(self, text, area=None, experience=None, page=0, per_page=100):
        url = f'{self.BASE_URL}/vacancies'
        params = {
            'text': text,
            'area': area,
            'experience': experience,
            'page': page,
            'per_page': per_page
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()