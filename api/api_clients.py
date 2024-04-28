import requests
from .api import VacancyApiClient


class ApiClientFactory:
    @staticmethod
    def create_api_client(source):
        if source == 'hh':
            return HhApiClient()
        elif source == 'tinkoff':
            return TinkoffApiClient()
        else:
            raise ValueError(f'Unknown source: {source}')


class HhApiClient(VacancyApiClient):
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

    def get_vacancy(self, vacancy_id):
        url = f'{self.BASE_URL}/vacancies/{vacancy_id}'
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_areas(self):
        url = f'{self.BASE_URL}/areas'
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def find_area(self, area_name):
        url = f'{self.BASE_URL}/suggests/areas'
        params = {'text': area_name}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['items']:
            return data['items'][0]['id']
        return None


# TODO Реализовать класс TinkoffApiClient через парсинг сайта
class TinkoffApiClient(VacancyApiClient):
    # ...
    def search_vacancies(self, text, **kwargs):
        # Реализация поиска вакансий через API Тинькофф
        pass

    def get_vacancy(self, vacancy_id):
        # Реализация получения деталей вакансии через API Тинькофф
        pass

    def find_area(self, area_name):
        # Реализация поиска региона для Тинькофф API
        # Если не поддерживается, можно вернуть NotImplementedError
        raise NotImplementedError("Поиск региона не поддерживается для Тинькофф API")

    def get_areas(self):
        # Реализация получения списка регионов для Тинькофф API
        # Если не поддерживается, можно вернуть NotImplementedError
        raise NotImplementedError("Получение списка регионов не поддерживается для Тинькофф API")
