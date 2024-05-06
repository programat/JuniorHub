import requests

from vacancies.models import Vacancy, VacancyDetail
from .data_provider_interface import VacancyDataProvider


class DataProviderFactory:
    @staticmethod
    def create_data_provider(source):
        if source == 'hh':
            return HhDataProvider()
        elif source == 'tinkoff':
            return TinkoffDataProvider()
        else:
            raise ValueError(f'Unknown source: {source}')


class HhDataProvider(VacancyDataProvider):
    BASE_URL = 'https://api.hh.ru'

    def __init__(self):
        self.session = requests.Session()

    def get_vacancies(self, text, area=None, experience=None, page=0, per_page=100):
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
        return response.json()['items']

    def get_vacancy_details(self, vacancy_id):
        url = f'{self.BASE_URL}/vacancies/{vacancy_id}'
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def save_vacancies(self, vacancies):
        for vacancy_data in vacancies:
            vacancy = Vacancy(
                title=vacancy_data['name'],
                description=vacancy_data['description'],
                company=vacancy_data['employer']['name'],
                url=vacancy_data['alternate_url'],
                source='hh.ru'
            )
            vacancy.save()

    def save_vacancy_details(self, vacancy_id, details):
        vacancy = Vacancy.objects.get(url=details['alternate_url'])
        salary = details.get('salary')
        if salary is not None:
            salary_from = salary.get('from', '')
            salary_to = salary.get('to', '')
            currency = salary.get('currency', '')
        else:
            salary_from = None
            salary_to = None
            currency = ''
        vacancy_detail = VacancyDetail(
            vacancy=vacancy,
            salary_from=salary_from,
            salary_to=salary_to,
            currency=currency,
            city=details['area']['name'],
            experience=details['experience']['name'],
            employment_type=details['employment']['name'],
            schedule=details['schedule']['name'],
            skills=', '.join(skill['name'] for skill in details['key_skills']),
            source_id=details['id']
        )
        vacancy_detail.save()

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


class TinkoffDataProvider(VacancyDataProvider):
    def get_vacancies(self, text, **kwargs):
        return Vacancy.objects.filter(source='tinkoff')

    def get_vacancy_details(self, vacancy_id):
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id, source='tinkoff')
            return {
                'title': vacancy.title,
                'description': vacancy.description,
                'company': 'Тинькофф',
                'url': vacancy.url,
                'area': vacancy.area
            }
        except Vacancy.DoesNotExist:
            return None

    def save_vacancies(self, vacancies):
        for category in vacancies:
            for position in category['positions']:
                vacancy, created = Vacancy.objects.update_or_create(
                    url=position['link'],
                    defaults={
                        'title': position['title'],
                        'description': position['description'],
                        'company': 'Тинькофф',
                        'source': 'tinkoff',
                    }
                )
                defaults = {
                    'area': position['area'],
                }
                if 'status' in position:
                    if position['status'] == 'Набор открыт':
                        defaults['status'] = VacancyDetail.STATUS_ACTIVE
                    elif position['status'] == 'Набор закрыт':
                        defaults['status'] = VacancyDetail.STATUS_CLOSED

                VacancyDetail.objects.update_or_create(
                    vacancy=vacancy,
                    defaults=defaults
                )

    def save_vacancy_details(self, vacancy_id, details):
        # Реализация сохранения деталей стажировки в базу данных
        pass
