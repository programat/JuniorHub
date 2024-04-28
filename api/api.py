from abc import ABC, abstractmethod


class VacancyApiClient(ABC):
    @abstractmethod
    def search_vacancies(self, text, **kwargs):
        pass

    @abstractmethod
    def get_vacancy(self, vacancy_id):
        pass

    @abstractmethod
    def find_area(self, area_name):
        pass

    @abstractmethod
    def get_areas(self):
        pass
